import os
from pathlib import Path

class LLMConfig:
    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    GENERATED_CODE_DIR = BASE_DIR / "generated_code"
    
    # LLM Configuration
    MODEL_CONFIG = {
        "default_model": "gpt-4",
        "fallback_model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    # Security Configuration
    SECURITY_CONFIG = {
        "allowed_imports": [
            "os", "sys", "pathlib", "json", "yaml", 
            "requests", "urllib", "datetime"
        ],
        "blocked_operations": [
            "eval", "exec", "subprocess", "system"
        ],
        "max_file_size": 1024 * 1024  # 1MB
    }
    
    # Integration Configuration
    INTEGRATION_CONFIG = {
        "supported_services": [
            "github", "gitlab", "bitbucket",
            "jenkins", "travis", "circleci",
            "docker", "kubernetes",
            "aws", "azure", "gcp",
            "prometheus", "grafana", "elasticsearch"
        ],
        "timeout": 30,  # seconds
        "max_retries": 3
    }

    @classmethod
    def initialize(cls):
        """Initialize configuration and create necessary directories"""
        os.makedirs(cls.GENERATED_CODE_DIR, exist_ok=True)
        
        # Validate environment variables
        required_vars = [
            'OPENAI_API_KEY',
            'GITHUB_TOKEN',
            'AWS_ACCESS_KEY',
            'AWS_SECRET_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}") 