#!/bin/bash

if [ ! -d images ]; then
  echo "Creating images dir..."
  mkdir images
fi

if [ ! -d prompts ]; then
  echo "Creating prompts dir..."
  mkdir prompts
fi

if [ ! -f .token ]; then
  echo "App token missing!"
  echo -n "Enter token: "
  read -s TOKEN
  echo $TOKEN > .token
fi

if [ ! -d venv ]; then
  echo "Creating venv..."
  python3 -m venv venv
fi

echo "Updating venv..."
source venv/bin/activate
pip install -U -r requirements.txt
deactivate

echo ""
echo "Copy and edit the config file to complete: jarvis.conf.example -> jarvis.conf"
echo "Done!"
