#!/bin/bash

# Update package list
sudo apt-get update

# Install Python and related tools
sudo apt-get install -y python3 python3-pip python3-venv

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Java
sudo apt-get install -y openjdk-17-jdk

# Install other utilities
sudo apt-get install -y git curl wget gnome-terminal

# Configure Git
echo "Configuring Git..."
read -p "Enter your Git username: " git_username
read -p "Enter your Git email: " git_email

git config --global user.name "$git_username"
git config --global user.email "$git_email"

# Configure Git credentials helper (optional)
read -p "Would you like to store Git credentials? (y/n): " store_credentials
if [ "$store_credentials" = "y" ]; then
    git config --global credential.helper store
    echo "Git credentials will be stored permanently"
fi

# Generate SSH key (optional)
read -p "Would you like to generate SSH key for Git? (y/n): " generate_ssh
if [ "$generate_ssh" = "y" ]; then
    ssh-keygen -t ed25519 -C "$git_email"
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519
    echo "Your SSH public key:"
    cat ~/.ssh/id_ed25519.pub
    echo "Add this key to your GitHub account"
fi

# Verify installations
echo "Checking installations..."
python3 --version
node --version
npm --version
java -version
git --version

# Show Git configuration
echo "Git configuration:"
git config --list