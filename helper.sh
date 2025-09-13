#!/bin/bash

FILENAME=""

source venv/bin/activate

if [ -z "$2" ]
then
  FILENAME=$(python3 generator.py $1)
else
  FILENAME=$(python3 generator.py $1 $2)
fi

echo $FILENAME
