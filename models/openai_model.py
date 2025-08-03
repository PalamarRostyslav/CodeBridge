from openai import OpenAI
from typing import Optional
from .base_model import BaseCodeModel

class OpenAIModel(BaseCodeModel):
    """OpenAI model implementation."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.client = None
        if api_key:
            self.client = OpenAI(api_key=api_key)

    def convert_code(self, python_code: str, target_language: str, add_comments: bool = False) -> str:
        """Convert Python code using OpenAI API."""
        if not self.is_available():
            raise Exception("OpenAI API key is required but not provided.")
        
        prompt = self._create_prompt(python_code, target_language, add_comments)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert programmer skilled in converting code between different programming languages. Respond with only the converted code, no explanations or markdown formatting."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=16384,
            )
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"OpenAI API request failed: {str(e)}")

    def is_available(self) -> bool:
        """Check if OpenAI API key is provided."""
        return self.api_key is not None and self.client is not None
    
    def update_api_key(self, api_key: str):
        """Update the API key and reinitialize client."""
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key) if api_key else None