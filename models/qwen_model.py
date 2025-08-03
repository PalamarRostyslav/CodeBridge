import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import Optional
from .base_model import BaseCodeModel

class QwenModel(BaseCodeModel):
    """Qwen2.5-7B-Instruct local model implementation."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
        
    def _load_model(self):
        """Load the Qwen2.5-7B-Instruct model and tokenizer."""
        try:
            model_name = "Qwen/Qwen2.5-7B-Instruct"
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
                quantization_config=quantization_config,
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
        except Exception as e:
            print(f"Error loading model: {e}")
            
            self.model = None
            self.tokenizer = None
            
    def convert_code(self, python_code: str, target_language: str, add_comments: bool = False) -> str:
        """Convert Python code to the target programming language using Qwen2.5-7B-Instruct."""
        if not self.is_available():
            raise Exception("Qwen model is not available. Please check your CUDA setup and model installation.")
        
        prompt = self._create_prompt(python_code, target_language, add_comments)
        
        messages = [
            {"role": "system", "content": "You are an expert programmer skilled in converting code between different programming languages."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            text = self.tokenizer.apply_chat_template(messages, return_tensors="pt").to(self.device)
            
            inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=2048,
                    temperature=0.1,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract only the assistents response
            assistant_response = response.find("<|im_start|>assistant\n")
            if assistant_response != -1:
                response = response[assistant_response + len("<|im_start|>assistant\n"):]

            return response.strip()

        except Exception as e:
            raise Exception(f"Qwen model generation failed: {str(e)}")
        
    def is_available(self) -> bool:
        """Check if Qwen model is properly loaded."""
        return self.model is not None and self.tokenizer is not None and torch.cuda.is_available()