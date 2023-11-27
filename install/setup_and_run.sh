#!/bin/bash

# Function to check if Miniconda is installed
check_miniconda() {
    if ! [ -x "$(command -v conda)" ]; then
        echo "Miniconda is not installed. Installing Miniconda..."
        # Replace this URL with the latest Miniconda installer for your platform
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
        bash miniconda.sh -b -p $HOME/miniconda
        export PATH="$HOME/miniconda/bin:$PATH"
        echo "Miniconda installed."
    else
        echo "Miniconda is already installed."
    fi
}

# Step 1: Check and install Miniconda if necessary
check_miniconda

# Step 2: Clone the GitHub repository
git clone https://github.com/MDGrey33/Nur.git
cd Nur

# Step 3: Create a Miniconda environment
conda create -n myenv python=3.8 -y

# Step 4: Activate the Miniconda environment
# You may need to modify this depending on how your shell handles script execution
source activate myenv

# Step 5: Install Python dependencies
pip install -r requirements.txt

# Step 6: Start the Docker containers
docker-compose up --build

