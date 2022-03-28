#!/bin/bash

python3 --version

python3 -m venv venv

source ./venv/bin/activate

pip3 install --no-input -r ./requirements.txt
