from flask import Flask, request, jsonify
from flask_cors import CORS
from orchestrator.task_manager import TaskManager
from llm.llm_service import LLMService
from llm.task_handler import TaskHandler
from llm.config import LLMConfig

app = Flask(__name__)
CORS(app)

task_manager = TaskManager()
llm_service = LLMService()
task_handler = TaskHandler()
LLMConfig.initialize()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    
    # Process the message through LLM
    llm_response = llm_service.process_input(user_input)
    
    # Create task if needed
    if llm_response.get('create_task'):
        task = task_manager.create_task(llm_response['task_details'])
        return jsonify({
            'message': llm_response['response'],
            'task': task.to_dict()
        })
    
    return jsonify({'message': llm_response['response']})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = task_manager.get_all_tasks()
    return jsonify({'tasks': [task.to_dict() for task in tasks]})

@app.route('/api/llm/analyze', methods=['POST'])
def analyze_task():
    data = request.json
    result = task_handler.analyze_task(data.get('task'))
    return jsonify(result)

@app.route('/api/llm/generate', methods=['POST'])
def generate_code():
    data = request.json
    result = task_handler.generate_java_code(
        data.get('task'),
        data.get('context')
    )
    return jsonify(result)

@app.route('/api/llm/execute', methods=['POST'])
def execute_code():
    data = request.json
    result = task_handler.execute_dynamic_code(
        data.get('task'),
        data.get('code')
    )
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 