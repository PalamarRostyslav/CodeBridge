from abc import ABC, abstractmethod
from typing import Optional

class BaseCodeModel(ABC):
    """
    Abstract base class for code models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the code model with an optional API key.
        
        :param api_key: API key for authentication, if required.
        """
        self.api_key = api_key

    @abstractmethod
    def convert_code(self, python_code: str, target_language: str, add_comments: bool = False) -> str:
        """
        Convert code from one programming language to another.
        
        :param python_code: The input code in Python.
        :param target_language: The target programming language to convert to.
        :param add_comments: Whether to add comments to the generated code.
        :return: Converted code as a string.
        
        Returns:
            Converted code as string
            
        Raises:
            Exception: If conversion fails
        """
        pass

    @abstractmethod
    def is_available(self, code: str) -> Optional[str]:
        """Check if the model is available and properly configured."""
        pass

    def _create_prompt(self, python_code: str, target_language: str, add_comments: bool = False) -> str:
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
                
                