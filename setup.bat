@echo off
echo Setting up Automation Platform...

echo Setting up Python Backend...
cd backend\python
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
cd ..

echo Setting up Java Backend...
cd java-api
call mvnw clean install
cd ..

echo Setting up Frontend...
cd ..\frontend-react
call npm install

echo Setup complete!
cd .. 