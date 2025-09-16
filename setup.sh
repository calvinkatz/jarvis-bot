#!/bin/bash

if [ ! -d images ]; then
  echo "Creating images dir..."
  mkdir images
fi

if [ ! -d prompts ]; then
  echo "Creating prompts dir..."
  mkdir prompts
fi

if [ ! -d venv ]; then
  echo "Creating venv..."
  python3 -m venv venv
fi

cp jarvis.conf.example jarvis.conf
cp system.txt.example system.txt

echo "Updating venv..."
source venv/bin/activate
pip install -U -r requirements.txt
deactivate

echo " "
echo "Edit files to complete setup:"
echo "  jarvis.conf - Bot configuration"
echo "  system.txt  - Ollama system prompt"
echo " "
