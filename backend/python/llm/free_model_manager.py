from typing import Dict, Any, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from pathlib import Path
import json

class FreeModelManager:
    def __init__(self):
        self.config_path = Path("config/models")
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.models_config = self._load_models_config()
        self.local_models = {}
        self._initialize_models()

    def _initialize_models(self):
        """Initialize with minimal resource usage"""
        try:
            # Load the smallest model first
            model_name = "gpt2"  # Start with smallest model
            config = self.models_config["local_models"][model_name]
            
            # Use smaller precision and efficient loading
            model = AutoModelForCausalLM.from_pretrained(
                config["path"],
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            )
            tokenizer = AutoTokenizer.from_pretrained(config["path"])
            
            self.local_models[model_name] = {
                "model": model,
                "tokenizer": tokenizer,
                "config": config
            }
            
        except Exception as e:
            print(f"Failed to load model: {str(e)}")

    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate response using available free model"""
        try:
            model_name = "gpt2"  # Use the smallest model
            model_data = self.local_models[model_name]
            
            inputs = model_data["tokenizer"](
                prompt, 
                return_tensors="pt", 
                max_length=512,
                truncation=True
            )
            
            outputs = model_data["model"].generate(
                **inputs,
                max_length=512,
                num_return_sequences=1,
                temperature=0.7,
                pad_token_id=model_data["tokenizer"].eos_token_id
            )
            
            response = model_data["tokenizer"].decode(outputs[0], skip_special_tokens=True)
            return {
                "success": True,
                "response": response,
                "model": f"local/gpt2"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def load_quantized_model(self, model_name: str):
        """Load 4-bit quantized model for memory efficiency"""
        try:
            from transformers import BitsAndBytesConfig
            
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16
            )
            
            model = AutoModelForCausalLM.from_pretrained(
                self.models_config["local_models"][model_name]["path"],
                quantization_config=quantization_config,
                device_map="auto"
            )
            
            return model
        except Exception as e:
            print(f"Failed to load quantized model: {str(e)}")
            return None 