from typing import Dict, Any, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import openai
from pathlib import Path
import json

class ModelManager:
    def __init__(self):
        self.config_path = Path("config/models")
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.models_config = self._load_models_config()
        self.local_models = {}
        self.api_models = {}
        self._initialize_models()

    def _load_models_config(self) -> Dict[str, Any]:
        config_file = self.config_path / "models_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            "local_models": {
                "llama2": {
                    "path": "TheBloke/Llama-2-7B-Chat-GGML",
                    "type": "causal",
                    "max_length": 2048,
                    "device": "cpu"
                },
                "codegen": {
                    "path": "Salesforce/codegen-350M-mono",
                    "type": "causal",
                    "max_length": 1024,
                    "device": "cpu"
                },
                "gpt2": {
                    "path": "gpt2",
                    "type": "causal",
                    "max_length": 1024,
                    "device": "cpu"
                }
            },
            "api_models": {
                "falcon": {
                    "provider": "huggingface",
                    "model_id": "tiiuae/falcon-7b",
                    "api_key_env": "HF_API_KEY"
                },
                "bloom": {
                    "provider": "huggingface",
                    "model_id": "bigscience/bloom",
                    "api_key_env": "HF_API_KEY"
                }
            },
            "fallback_strategy": {
                "order": ["local", "api"],
                "timeout": 30
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config

    def _initialize_models(self):
        """Initialize configured models"""
        # Initialize local models
        for model_name, config in self.models_config["local_models"].items():
            try:
                model = AutoModelForCausalLM.from_pretrained(
                    config["path"],
                    device_map=config["device"]
                )
                tokenizer = AutoTokenizer.from_pretrained(config["path"])
                self.local_models[model_name] = {
                    "model": model,
                    "tokenizer": tokenizer,
                    "config": config
                }
            except Exception as e:
                print(f"Failed to load local model {model_name}: {str(e)}")

        # Initialize API clients
        for model_name, config in self.models_config["api_models"].items():
            if config["provider"] == "openai":
                self.api_models[model_name] = {
                    "client": openai,
                    "config": config
                }

    async def generate(self, prompt: str, model_preference: str = None) -> Dict[str, Any]:
        """Generate response using available models"""
        if model_preference:
            # Try specific model first
            if model_preference in self.local_models:
                return await self._generate_local(prompt, model_preference)
            elif model_preference in self.api_models:
                return await self._generate_api(prompt, model_preference)

        # Follow fallback strategy
        for model_type in self.models_config["fallback_strategy"]["order"]:
            try:
                if model_type == "local" and self.local_models:
                    # Try first available local model
                    model_name = next(iter(self.local_models))
                    return await self._generate_local(prompt, model_name)
                elif model_type == "api" and self.api_models:
                    # Try first available API model
                    model_name = next(iter(self.api_models))
                    return await self._generate_api(prompt, model_name)
            except Exception as e:
                continue

        raise Exception("No available models could generate a response")

    async def _generate_local(self, prompt: str, model_name: str) -> Dict[str, Any]:
        """Generate response using local model"""
        model_data = self.local_models[model_name]
        model = model_data["model"]
        tokenizer = model_data["tokenizer"]
        config = model_data["config"]

        inputs = tokenizer(prompt, return_tensors="pt").to(config["device"])
        outputs = model.generate(
            **inputs,
            max_length=config["max_length"],
            num_return_sequences=1,
            temperature=0.7
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {
            "success": True,
            "response": response,
            "model": f"local/{model_name}"
        }

    async def _generate_api(self, prompt: str, model_name: str) -> Dict[str, Any]:
        """Generate response using API model"""
        model_data = self.api_models[model_name]
        client = model_data["client"]
        config = model_data["config"]

        if config["provider"] == "openai":
            response = client.ChatCompletion.create(
                model=config["model_id"],
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model": f"api/{model_name}"
            }

    def add_local_model(self, name: str, config: Dict[str, Any]) -> bool:
        """Add a new local model configuration"""
        try:
            self.models_config["local_models"][name] = config
            self._initialize_models()
            self._save_config()
            return True
        except Exception:
            return False

    def add_api_model(self, name: str, config: Dict[str, Any]) -> bool:
        """Add a new API model configuration"""
        try:
            self.models_config["api_models"][name] = config
            self._initialize_models()
            self._save_config()
            return True
        except Exception:
            return False

    def _save_config(self):
        """Save current configuration to file"""
        with open(self.config_path / "models_config.json", 'w') as f:
            json.dump(self.models_config, f, indent=2) 