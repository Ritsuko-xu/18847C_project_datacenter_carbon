#!/bin/bash

# Path to your Python script
PYTHON_SCRIPT="compute_latency.py"

# Base directory path
BASE_DIR="outputs/jaeger_json/rs620_load_980_jsons"

# Array of directory name suffixes
SERVICENAMES=(
    "compose-post"
    "home-timeline"
    "media"
    "nginx-web-server"
    "post-storage"
    "social-graph"
    "text"
    "unique-id"
    "url-shorten"
    "user"
    "user-mention"
    "user-timeline"
)

# Percentiles to calculate
PERCENTILES="99"

# Loop through each suffix and construct the directory path
for SERVICENAME in "${SERVICENAMES[@]}"; do
    # Construct the full directory path by appending the suffix to the base directory
    DIR="$BASE_DIR/$SERVICENAME"
    echo "Computing the $PERCENTILES%-ile latency of $SERVICENAME:"
    python3 $PYTHON_SCRIPT --json_files "$DIR" --percentiles $PERCENTILES
    echo "-------------------------------------------------"
done

