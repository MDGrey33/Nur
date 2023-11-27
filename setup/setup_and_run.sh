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

# Determine the project root path
current_dir="$(basename "$PWD")"
parent_dir="$(basename "$(dirname "$PWD")")"

if [ "$current_dir" = "setup" ] && [ "$parent_dir" = "Nur" ]; then
    # In /Nur/setup, navigate to /Nur and set project root path
    project_root_path="$(dirname "$PWD")"
    echo "In /Nur/setup. Project root is: $project_root_path"
    cd ..
elif [ "$current_dir" = "Nur" ]; then
    # Already in /Nur, set project root path
    project_root_path="$PWD"
    echo "Already in /Nur. Project root is: $project_root_path"
else
    # Not in /Nur or /Nur/setup, clone the repo and set project root path
    git clone https://github.com/MDGrey33/Nur.git
    cd Nur
    project_root_path="$PWD"
    echo "Cloned repository. Project root is: $project_root_path"
fi

# Define path for setup directory
setup_path="$project_root_path/setup"

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
source activate "$env_name" || conda activate "$env_name"

# Install Python dependencies from the setup directory
requirements_file="$setup_path/requirements.txt"
if [ -f "$requirements_file" ]; then
    echo "Installing Python dependencies from $requirements_file."
    pip install -r "$requirements_file"
else
    echo "No requirements.txt found in $setup_path. Skipping Python dependencies installation."
fi

# Start the Docker containers
echo "Starting Docker containers from $project_root_path."
(cd "$project_root_path" && docker-compose up --build)
