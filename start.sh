#!/bin/bash

# Activate virtual environment
echo "Activating Virtual Environment"
source ./venv/bin/activate

# Install dependencies
echo "Installing Python Dependencies"
pip3 install -r requirements.txt

# Run CAN test
echo "Starting CAN Test..."
python -m  Scripts.test
