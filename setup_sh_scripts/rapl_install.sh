#!/usr/bin/env bash

# Usage check
#if [ $# -ne 2 ]; then
#    echo "Usage: $0 <name of output file> <duration>"
#    exit 1
#fi

# Function to install cpu-energy-meter
install_cpu_energy_meter() {
    echo "Checking for cpu-energy-meter..."
    if ! command -v cpu-energy-meter &> /dev/null
    then
        echo "cpu-energy-meter could not be found, attempting to install..."
        # Set non-interactive frontend for apt-get
        export DEBIAN_FRONTEND=noninteractive
        sudo apt-get update
        sudo apt-get install -y git build-essential libcap-dev
        # Check if the cpu-energy-meter directory exists and clear it if it does
        if [ -d "cpu-energy-meter" ]; then
            echo "Removing existing cpu-energy-meter directory..."
            rm -rf cpu-energy-meter
        fi
        git clone https://github.com/sosy-lab/cpu-energy-meter.git
        cd cpu-energy-meter
        make
        sudo make install
        cd ..
        echo "Installation complete."
    else
        echo "cpu-energy-meter is already installed."
    fi
}

# Ensure the msr module is loaded
echo "Checking and loading msr module..."
sudo modprobe msr

# Install cpu-energy-meter if not already installed
install_cpu_energy_meter

# Remove existing data file
rm -f "$1"

# Check if the user has permission to access MSR files and set it if not
for msr in /dev/cpu/*/msr; do
    sudo chmod 666 $msr
done
