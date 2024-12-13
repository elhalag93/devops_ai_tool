#!/bin/bash

echo "Setting up Automation Platform..."

# Make script executable
chmod +x start.sh

# Setup Python Backend
echo "Setting up Python Backend..."
cd backend/python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ../..

# Setup Java Backend
echo "Setting up Java Backend..."
cd backend/java-api
chmod +x mvnw
./mvnw clean install
cd ../..

# Setup Frontend
echo "Setting up Frontend..."
cd frontend-react
npm install
cd ..

echo "Setup complete!" 