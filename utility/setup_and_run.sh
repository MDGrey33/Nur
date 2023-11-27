#!/bin/bash

# Function to check and install Miniconda if necessary
check_miniconda() {
    if ! [ -x "$(command -v conda)" ]; then
        echo "Miniconda is not installed. Installing Miniconda..."
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
        bash miniconda.sh -b -p $HOME/miniconda
        export PATH="$HOME/miniconda/bin:$PATH"
        echo "Miniconda installed."
    else
        echo "Miniconda is already installed."
    fi
}

# Check if already in Nur directory with main.py
if [ -d "Nur" ] && [ -f "Nur/main.py" ]; then
    echo "Nur directory with main.py already exists. Skipping cloning."
    cd Nur
else
    # Clone the GitHub repository if Nur directory doesn't exist
    git clone https://github.com/MDGrey33/Nur.git
    cd Nur
fi

# Check if the Miniconda environment already exists
env_name="myenv"
if conda info --envs | grep -q "$env_name"; then
    echo "Miniconda environment '$env_name' already exists. Activating it."
else
    echo "Creating Miniconda environment '$env_name'."
    conda create -n "$env_name" python=3.8 -y
fi

# Activate the Miniconda environment
# Modify this depending on your shell compatibility
source activate "$env_name"

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies."
    pip install -r requirements.txt
else
    echo "No requirements.txt found. Skipping Python dependencies installation."
fi

# Start the Docker containers
echo "Starting Docker containers."
docker-compose up --build
