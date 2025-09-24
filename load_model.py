#!/usr/bin/env bash

import configparser
import json
import os
import urllib.request
import urllib.parse
import uuid
import websocket

config = configparser.ConfigParser()
config.read('jarvis.conf')

comfy_addr = config['comfyui']['address']
comfy_ckpt = config['comfyui']['checkpoint']
client_id  = str(uuid.uuid4())

# Send and return workflow
def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(comfy_addr), data=data)
    return json.loads(urllib.request.urlopen(req).read())

# Run and wait for workflow to finish
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

# Get workflow from file
with open("load_model.json") as file:
    workflow_text = file.read()
workflow = json.loads(workflow_text)

# Set comfy_ckpt
workflow["22"]["inputs"]["ckpt_name"] = "jarvis/{}".format(comfy_ckpt)

# Send prompt to Comfy, download image
ws = websocket.WebSocket()
ws.connect("ws://{}/ws?clientId={}".format(comfy_addr, client_id))
get_images(ws, workflow)
ws.close()
