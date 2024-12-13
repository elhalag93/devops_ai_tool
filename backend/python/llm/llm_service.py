from typing import Dict, Any, Optional
import openai
import json
import os
from pathlib import Path
import importlib.util
import ast
from adaptive_config import AdaptiveConfig
from .model_manager import ModelManager

class LLMService:
    def __init__(self):
        self.model_manager = ModelManager()
        self.adaptive_config = AdaptiveConfig()
        self.code_generation_path = Path("generated_code")
        self.code_generation_path.mkdir(exist_ok=True)
        
    async def process_input(self, user_input: str) -> Dict[str, Any]:
        try:
            # Get context from the input
            context = await self._extract_context(user_input)
            
            # Find best matching pattern
            pattern = self.adaptive_config.get_best_pattern("execution", context)
            
            if pattern:
                # Use existing pattern
                result = await self._execute_pattern(pattern, context)
            else:
                # Generate new solution
                result = await self._generate_new_solution(context)
                
            # Learn from the execution
            self.adaptive_config.adapt_to_feedback({
                "type": "execution",
                "success": result.get("success", False),
                "context": context
            })
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _extract_context(self, user_input: str) -> Dict[str, Any]:
        """Extract context using available models"""
        response = await self.model_manager.generate(
            prompt="Extract key context elements from this input: " + user_input,
            model_preference="local/codellama"  # Prefer local CodeLlama for code understanding
        )
        
        try:
            return json.loads(response["response"])
        except:
            return {"raw_input": user_input}

    async def _execute_pattern(self, pattern: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an existing pattern with the given context"""
        try:
            if pattern.get("code"):
                # Execute existing code pattern
                return await self._execute_code_pattern(pattern["code"], context)
            elif pattern.get("integration"):
                # Execute existing integration pattern
                return await self._execute_integration_pattern(pattern["integration"], context)
            else:
                # Fall back to generating new solution
                return await self._generate_new_solution(context)
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _generate_new_solution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new solution when no pattern matches"""
        try:
            # Generate solution using LLM
            response = await self.model_manager.generate(
                prompt="Generate a complete solution including: 1. Code implementation 2. Integration points 3. Execution strategy 4. Error handling",
                model_preference="local/codellama"  # Prefer local CodeLlama for code understanding
            )
            
            solution = response["response"]
            
            # Validate and execute the solution
            if await self._validate_solution(solution):
                result = await self._execute_solution(solution, context)
                
                # If successful, learn the pattern
                if result.get("success"):
                    self.adaptive_config.learn_pattern("execution", {
                        "context": context,
                        "solution": solution,
                        "result": result
                    })
                
                return result
            
            return {"success": False, "error": "Solution validation failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _validate_solution(self, solution: str) -> bool:
        """Validate generated solution"""
        try:
            # Use LLM to validate the solution
            response = await self.model_manager.generate(
                prompt="Validate this solution for: 1. Security issues 2. Best practices 3. Error handling 4. Performance considerations",
                model_preference="local/codellama"  # Prefer local CodeLlama for code understanding
            )
            
            validation_result = response["response"]
            return "VALID" in validation_result.upper()
        except:
            return False

    async def _analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input to determine the required action"""
        response = await self.model_manager.generate(
            prompt="You are an AI assistant specialized in: 1. Code generation and modification 2. System integration 3. Task automation Analyze the user request and determine the required action.",
            model_preference="local/codellama"  # Prefer local CodeLlama for code understanding
        )
        
        # Parse the response to determine intent
        content = response["response"]
        return await self._categorize_intent(content, user_input)

    async def _handle_code_generation(self, intent: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Handle dynamic code generation and deployment"""
        response = await self.model_manager.generate(
            prompt="Generate production-ready code based on the request. Include: 1. Code implementation 2. Tests 3. Documentation 4. Integration points",
            model_preference="local/codellama"  # Prefer local CodeLlama for code understanding
        )
        
        code_content = response["response"]
        
        # Parse and validate generated code
        validated_code = await self._validate_code(code_content)
        if validated_code:
            # Deploy the code
            deployment_result = await self._deploy_code(validated_code)
            return {
                'success': True,
                'response': 'Code generated and deployed successfully',
                'code': validated_code,
                'deployment': deployment_result
            }
        
        return {
            'success': False,
            'response': 'Code validation failed'
        }

    async def _handle_integration(self, intent: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Handle third-party service integration"""
        # Get integration details from LLM
        response = await self.model_manager.generate(
            prompt="Analyze the integration requirements and provide: 1. Required APIs 2. Authentication methods 3. Data mapping 4. Integration code",
            model_preference="local/codellama"  # Prefer local CodeLlama for code understanding
        )
        
        integration_details = response["response"]
        
        # Implement the integration
        integration_result = await self._implement_integration(integration_details)
        return integration_result

    async def _validate_code(self, code_content: str) -> Optional[Dict[str, Any]]:
        """Validate generated code for security and correctness"""
        try:
            # Parse code to check for syntax errors
            ast.parse(code_content)
            
            # Additional security checks
            security_check = await self._security_check(code_content)
            if not security_check['safe']:
                return None
                
            return {
                'content': code_content,
                'security_check': security_check
            }
        except SyntaxError:
            return None

    async def _deploy_code(self, validated_code: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy validated code to appropriate location"""
        try:
            # Generate unique filename
            filename = f"generated_{hash(validated_code['content'])}.py"
            filepath = self.code_generation_path / filename
            
            # Write code to file
            with open(filepath, 'w') as f:
                f.write(validated_code['content'])
            
            # Load and register the module
            spec = importlib.util.spec_from_file_location(
                filename.replace('.py', ''),
                filepath
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return {
                'success': True,
                'module_path': str(filepath),
                'module_name': filename.replace('.py', '')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def _security_check(self, code_content: str) -> Dict[str, Any]:
        """Perform security analysis on generated code"""
        # Ask LLM to analyze code for security concerns
        response = await self.model_manager.generate(
            prompt="Analyze this code for security issues including: 1. Potential vulnerabilities 2. Unsafe operations 3. Resource leaks 4. Input validation Return a detailed security analysis.",
            model_preference="local/codellama"  # Prefer local CodeLlama for code understanding
        )
        
        analysis = response["response"]
        
        # Parse analysis to determine if code is safe
        return {
            'safe': 'UNSAFE' not in analysis.upper(),
            'analysis': analysis
        }

    async def _implement_integration(self, integration_details: str) -> Dict[str, Any]:
        """Implement third-party integration based on LLM guidance"""
        try:
            # Generate integration code
            integration_code = await self._handle_code_generation(
                {'requires_code_generation': True},
                f"Implement integration with the following details: {integration_details}"
            )
            
            if integration_code['success']:
                return {
                    'success': True,
                    'response': 'Integration implemented successfully',
                    'details': integration_code
                }
            
            return {
                'success': False,
                'response': 'Integration implementation failed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def _categorize_intent(self, content: str, user_input: str) -> Dict[str, Any]:
        """Categorize the intent of the user request"""
        # Ask LLM to categorize the intent
        response = await self.model_manager.generate(
            prompt="Categorize this request into one of: 1. Code generation 2. Integration 3. Task creation Provide the category and confidence score.",
            model_preference="local/codellama"  # Prefer local CodeLlama for code understanding
        )
        
        category = response["response"]
        
        return {
            'requires_code_generation': 'code generation' in category.lower(),
            'requires_integration': 'integration' in category.lower(),
            'requires_task': 'task creation' in category.lower(),
            'confidence': await self._extract_confidence(category),
            'original_response': content
        }

    async def _extract_confidence(self, category: str) -> float:
        """Extract confidence score from category response"""
        try:
            # Look for numbers in the response
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', category)
            if numbers:
                return float(numbers[0]) / 100
            return 0.5
        except:
            return 0.5 