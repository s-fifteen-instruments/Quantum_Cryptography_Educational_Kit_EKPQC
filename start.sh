#!/bin/bash

python3 --version

python3 -m venv venv

source ./venv/bin/activate

pip install --no-input -r ./requirements.txt
