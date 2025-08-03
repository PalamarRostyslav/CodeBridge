from abc import ABC, abstractmethod
from typing import Optional


class BaseCodeModel(ABC):
    """Abstract base class for code generation models."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    def convert_code(self, python_code: str, target_language: str, add_comments: bool = False, stream: bool = False) -> str:
        """
        Convert Python code to target language.
        
        Args:
            python_code: The Python code to convert
            target_language: Target language (c#, c++, java)
            add_comments: Whether to add explanatory comments
            stream: Whether to stream the response in real-time
            
        Returns:
            Converted code as string, or generator for streaming
            
        Raises:
            Exception: If conversion fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available and properly configured."""
        pass
    
    def _create_prompt(self, python_code: str, target_language: str, add_comments: bool) -> str:
        """Create a standardized prompt for code conversion."""
        comments_instruction = " Add detailed comments explaining the logic." if add_comments else ""
        
        return f"""Convert the following Python code to {target_language}.{comments_instruction}
            Make sure the converted code:
            1. Maintains the same functionality
            2. Uses appropriate {target_language} conventions and syntax
            3. Handles edge cases properly
            4. Is compilable and runnable

            Python code:
            ```python
            {python_code}
            ```

            Please respond with ONLY the {target_language} code, no explanations or markdown formatting."""