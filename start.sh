#!/bin/bash

# Start Python Backend
gnome-terminal --title="Python Backend" -- bash -c "cd backend/python && source venv/bin/activate && python app.py; exec bash"

# Wait for Python backend to start
sleep 5

# Start Java Backend
gnome-terminal --title="Java Backend" -- bash -c "cd backend/java-api && ./mvnw spring-boot:run; exec bash"

# Wait for Java backend to start
sleep 5

# Start Frontend
gnome-terminal --title="React Frontend" -- bash -c "cd frontend-react && npm start; exec bash" 