import configparser
import sys
from ollama import Client

config = configparser.ConfigParser()
config.read('jarvis.conf')

ollama_addr = config['ollama']['address']
ollama_mdl  = config['ollama']['model']
ollama_temp = config['ollama']['temperature']

print('Enter prompt: \n')
positive = input()

while True:
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

text = response.message.content
print(text)
