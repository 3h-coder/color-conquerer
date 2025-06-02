#!/bin/bash

# Change to the directory containing this script, then up to the server root
cd "$(dirname "$0")/../.."

# Import environment variables
source /etc/profile.d/envvars.sh

# Run the launch module
python3 -m scripts.launch