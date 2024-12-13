from typing import Dict, Any, Optional
from .adaptive_config import AdaptiveConfig
import importlib
import sys
from pathlib import Path

class IntegrationManager:
    def __init__(self):
        self.adaptive_config = AdaptiveConfig()
        self.integration_path = Path("integrations")
        self.integration_path.mkdir(exist_ok=True)

    def register_integration(self, integration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new integration"""
        try:
            # Validate integration data
            if self._validate_integration(integration_data):
                # Generate integration code
                code_path = self._generate_integration_code(integration_data)
                
                # Register in adaptive config
                self.adaptive_config.register_integration({
                    **integration_data,
                    "code_path": str(code_path)
                })
                
                return {
                    "success": True,
                    "message": f"Integration registered: {integration_data.get('id')}"
                }
            
            return {
                "success": False,
                "error": "Integration validation failed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _validate_integration(self, integration_data: Dict[str, Any]) -> bool:
        """Validate integration data"""
        required_fields = ["id", "name", "type", "config"]
        return all(field in integration_data for field in required_fields)

    def _generate_integration_code(self, integration_data: Dict[str, Any]) -> Path:
        """Generate integration code file"""
        integration_id = integration_data["id"]
        code_path = self.integration_path / f"{integration_id}.py"
        
        # Generate code using templates or LLM
        code_content = self._generate_code_content(integration_data)
        
        with open(code_path, 'w') as f:
            f.write(code_content)
            
        return code_path

    def _generate_code_content(self, integration_data: Dict[str, Any]) -> str:
        """Generate integration code content"""
        # Template for integration code
        return f"""
# Generated integration code for {integration_data['name']}
from typing import Dict, Any

class {integration_data['id'].capitalize()}Integration:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Integration logic here
            return {{"success": True, "result": "Integration executed"}}
        except Exception as e:
            return {{"success": False, "error": str(e)}}
"""

    def get_integration(self, integration_id: str) -> Optional[Any]:
        """Get integration instance by ID"""
        try:
            # Import integration module
            sys.path.append(str(self.integration_path))
            module = importlib.import_module(integration_id)
            
            # Get integration class
            integration_class = getattr(module, f"{integration_id.capitalize()}Integration")
            
            # Get configuration
            config = self.adaptive_config.integrations["available_integrations"].get(integration_id, {}).get("config", {})
            
            return integration_class(config)
        except Exception:
            return None 