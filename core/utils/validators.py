import ast
from typing import Tuple

class CodeValidator:
    """Utility class for validating Python code."""

    @staticmethod
    def validate_python_code(code: str) -> Tuple[bool, str]:
        """
        Validate if the provided code is valid Python code.

        :param code: The Python code to validate.
        :return: A tuple containing a boolean indicating validity and an error message if invalid.
        """
        
        if not code.strip():
            return False, "Code is empty or only contains whitespace."
        
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error in code: {e.msg} at line {e.lineno}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
        
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Validate the provided API key.

        :param api_key: The API key to validate.
        :return: True if the API key is valid, False otherwise.
        """
        
        if not api_key or not api_key.strip():
            return False
        
        key = api_key.strip()
        return len(key) >= 10 and any(c.isalnum() for c in key)
    
    @staticmethod
    def is_supported_language(language: str) -> bool:
        """
        Check if the provided language is supported.

        :param language: The programming language to check.
        :return: True if the language is supported, False otherwise.
        """
        
        supported = {"c#", "c++", "java"}
        return language.lower() in supported