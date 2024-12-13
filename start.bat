@echo off
start cmd /k "cd backend\python && .\venv\Scripts\activate && python app.py"
timeout /t 5
start cmd /k "cd backend\java-api && .\mvnw spring-boot:run"
timeout /t 5
start cmd /k "cd frontend-react && npm start" 