#!/bin/bash

# Change to the directory containing this script, then up to the server root
cd "$(dirname "$0")/../.."

# Run the launch module
# --force flag to force the nginx restart
python3 -m scripts.launch --force
