#!/usr/bin/env python3

import configparser
import json
import os
import random
import sys
import urllib.request
import urllib.parse
import uuid
import websocket
import ollama
from ollama import Client

config = configparser.ConfigParser()
config.read('jarvis.conf')

identity    = sys.argv[1]
filename    = "images/SPOILER_{}.webp".format(identity)
client_id   = str(uuid.uuid4())

comfy_addr  = config['comfyui']['address']
comfy_ckpt  = config['comfyui']['checkpoint']
comfy_neg   = config['comfyui']['negative']

ollama_addr = config['ollama']['address']
ollama_mdl  = config['ollama']['model']
ollama_temp = config['ollama']['temperature']

with open("prompts/{}.txt".format(identity)) as f:
    prompt_text = f.read()
prompt_text = prompt_text.split('|')
if len(prompt_text) > 1:
    positive = prompt_text[0]
    negative = prompt_text[1]
else:
    positive = prompt_text[0]
    negative = ""

with open("system.txt") as f:
    system_prompt = f.read()

# Get text from LLM
def get_prompt(arg):
    client = Client(
        host = "http://{}".format(ollama_addr)
    )

    response = client.chat(model = ollama_mdl, messages = [
        {
            'role': 'system',
            'content': "{}".format(system_prompt),
        },
        {
            'role': 'user',
            'content': "Generate a stable-diffusion prompt and wrap it in triple quotes: {}".format(arg),
        }
        ],
        options = {"temperature": float(config['ollama']['temperature'])}
    )

    # Assuming thinking model, split on end of thinking section.
    text = response.message.content.split('</think>')
    if type(text) is list:
        text = text[1].strip()
    # Assuming prompt worked and prompt is wrapped in """
    text = text.split('"""')
    if type(text) is list:
        text = text[1]
    # Prompt is whatever it is at this point.
    text = text.strip()
    return text

# Send and return workflow
def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(comfy_addr), data=data)
    return json.loads(urllib.request.urlopen(req).read())

# Get images
def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    current_node = ""
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['prompt_id'] == prompt_id:
                    if data['node'] is None:
                        break #Execution is done
                    else:
                        current_node = data['node']
        else:
            if current_node == '18':
                images_output = output_images.get(current_node, [])
                images_output.append(out[8:])
                output_images[current_node] = images_output
    return output_images

# Get workflow from file
with open("workflow.json") as file:
    workflow_text = file.read()
workflow = json.loads(workflow_text)

# If 2nd arg exists, get LLM prompt
if len(sys.argv) > 2:
    text = get_prompt(positive)
    if text != "":
        positive = text

# Set checkpoint
workflow["4"]["inputs"]["ckpt_name"] = "jarvis/{}".format(comfy_ckpt)
# Set positive prompt
workflow["6"]["inputs"]["text"] = "{}".format(positive)
# Set negatives
workflow['7']['inputs']['text'] = "{},{}".format(comfy_neg, negative)
# Set seed number
workflow["12"]["inputs"]["seed"] = random.randint(100000000000000, 999999999999999)

# Send prompt to Comfy, download image
ws = websocket.WebSocket()
ws.connect("ws://{}/ws?clientId={}".format(comfy_addr, client_id))
images = get_images(ws, workflow)
ws.close()

# Save image
for node_id in images:
    for image_data in images[node_id]:
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(image_data))
        image = image.save(filename, quality=90)

# Print filename for bot
print(filename)
