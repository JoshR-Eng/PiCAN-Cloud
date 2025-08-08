#!/bin/bash

# Activate virtual environment
echo "Activating Virtual Environment"
source ./venv/bin/activate

# Install dependencies
echo "Installing Python Dependencies"
pip3 install -r Scripts/requirements.txt

# Run CAN test
echo "Starting CAN Test..."
python3 Scripts/other_can_test.py
 
