import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
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
        """Load the Qwen model and tokenizer with quantization."""
        try:
            model_name = "Qwen/Qwen2.5-7B-Instruct"
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            
            # Load model with quantization for memory efficiency
            from transformers import BitsAndBytesConfig
            
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
                low_cpu_mem_usage=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
        except Exception as e:
            print(f"Failed to load Qwen model: {e}")
            self.model = None
            self.tokenizer = None
    
    def convert_code(self, python_code: str, target_language: str, add_comments: bool = False, stream: bool = False) -> str:
        """Convert Python code using Qwen model."""
        if not self.is_available():
            raise Exception("Qwen model is not available. Please check your CUDA setup and model installation.")
        
        prompt = self._create_prompt(python_code, target_language, add_comments)
        
        messages = [
            {"role": "system", "content": "You are an expert programmer skilled in converting code between different programming languages."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            if hasattr(self.tokenizer, 'apply_chat_template'):
                text = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            else:
                # Fallback if apply_chat_template is not available
                text = f"<|im_start|>system\nYou are an expert programmer skilled in converting code between different programming languages.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            
            if not isinstance(text, str):
                raise Exception(f"Chat template returned unexpected type: {type(text)}")
            
            try:
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=4096,
                    padding=False
                ).to(self.device)
            except Exception as e:
                raise Exception(f"Tokenization failed: {str(e)}. Input type: {type(text)}")
            
            if stream:
                return self._generate_streaming(inputs)
            else:
                return self._generate_complete(inputs)
            
        except Exception as e:
            raise Exception(f"Qwen model generation failed: {str(e)}")
    
    def _generate_streaming(self, inputs):
        """Generate with streaming support."""
        from transformers import TextIteratorStreamer
        from threading import Thread
        
        # Create streamer
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )
        
        # Generation parameters
        generation_kwargs = {
            **inputs,
            "max_new_tokens": 2048,
            "temperature": 0.1,
            "top_p": 0.9,
            "do_sample": True,
            "pad_token_id": self.tokenizer.eos_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            "streamer": streamer
        }
        
        # Start generation in separate thread
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        
        # Collect streamed tokens
        generated_text = ""
        for new_text in streamer:
            generated_text += new_text
            yield generated_text
        
        thread.join()
    
    def _generate_complete(self, inputs):
        """Generate complete response at once."""
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=2048,
                temperature=0.1,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response
        if "<|im_start|>assistant" in response:
            assistant_start = response.find("<|im_start|>assistant")
            response = response[assistant_start + len("<|im_start|>assistant"):]
            if "<|im_end|>" in response:
                response = response[:response.find("<|im_end|>")]
        
        # Clean up the response
        response = response.strip()
        if response.startswith("\n"):
            response = response[1:]
        
        return response
    
    def is_available(self) -> bool:
        """Check if Qwen model is properly loaded."""
        return self.model is not None and self.tokenizer is not None and torch.cuda.is_available()