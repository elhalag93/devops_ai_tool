from typing import Dict, Any
from .llm_service import LLMService
from .config import LLMConfig

class TaskHandler:
    def __init__(self):
        self.llm_service = LLMService()
        self.config = LLMConfig()

    def analyze_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task and determine if it needs dynamic code generation"""
        prompt = f"""Analyze this task and determine if it requires dynamic code generation:
        Task Name: {task_data.get('name')}
        Description: {task_data.get('description')}
        Type: {task_data.get('type')}
        """
        
        return self.llm_service.process_input(prompt)

    def generate_java_code(self, task_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Java code for task execution"""
        prompt = f"""Generate Java code to execute this task:
        Task Details: {task_data}
        Context: {context}
        Requirements:
        1. Must be compatible with Spring Boot
        2. Include error handling
        3. Include logging
        4. Follow best practices
        """
        
        return self.llm_service.process_input(prompt)

    def execute_dynamic_code(self, task_data: Dict[str, Any], code: str) -> Dict[str, Any]:
        """Execute dynamically generated code"""
        # Validate the code first
        validated_code = self.llm_service._validate_code(code)
        if not validated_code:
            return {
                'success': False,
                'error': 'Code validation failed'
            }

        # Deploy and execute the code
        try:
            deployment_result = self.llm_service._deploy_code(validated_code)
            if deployment_result['success']:
                return {
                    'success': True,
                    'result': f"Code executed successfully: {deployment_result['module_name']}"
                }
            return deployment_result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 