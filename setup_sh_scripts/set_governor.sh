#!/usr/bin/env bash

# take one argument, the governor to set
if [ $# -ne 1 ]; then
    echo "Usage: $0 <governor>"
    exit 1
fi

# make sure the governor is valid
# get the available governors
governors=$(cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_available_governors | uniq)
# check if the governor is in the list of available governors
if [[ ! $governors =~ (^|[[:space:]])$1($|[[:space:]]) ]]; then
    echo "Invalid governor"
    exit 1
fi

# set the governor
echo $1 | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# check if the previous command failed
if [ $? -ne 0 ]; then
    echo "Failed to set governor"
    exit 1
fi

sleep 5

# assert that the governor was set correctly
if [ $(cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | uniq) != $1 ]; then
    echo "Failed to set governor"
    exit 1
fi