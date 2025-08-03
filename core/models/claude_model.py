from anthropic import Anthropic
from typing import Optional
from .base_model import BaseCodeModel


class ClaudeModel(BaseCodeModel):
    """Claude Sonnet 4 implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.client = None
        if api_key:
            self.client = Anthropic(api_key=api_key)
    
    def convert_code(self, python_code: str, target_language: str, add_comments: bool = False) -> str:
        """Convert Python code using Claude API."""
        if not self.is_available():
            raise Exception("Claude API key is required but not provided.")
        
        prompt = self._create_prompt(python_code, target_language, add_comments)
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=15000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": f"You are an expert programmer. {prompt}"
                    }
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            raise Exception(f"Claude API call failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Claude API key is provided."""
        return self.api_key is not None and self.client is not None
    
    def update_api_key(self, api_key: str):
        """Update the API key and reinitialize client."""
        self.api_key = api_key
        self.client = Anthropic(api_key=api_key) if api_key else None