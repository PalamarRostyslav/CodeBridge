import os
import tempfile
from pathlib import Path
from typing import Optional

class FileManager:
    """
    Utility class for managing file operations.
    """

    @staticmethod
    def save_code_to_file(code: str, language: str, filename: Optional[str] = None) -> str:
        """
        Save code to a file with the specified language extension.

        :param code: The code to save.
        :param language: The programming language of the code.
        :param filename: Optional filename for the saved file.
        :return: Path to the saved file.
        """
        
        extensions = {
            "c#": ".cs",
            "c++": ".cpp",
            "java": ".java"
        }

        if language.lower() not in extensions:
            raise ValueError(f"Unsupported language: {language}")

        extension = extensions[language.lower()]
        if not filename:
            filename = f"converted_code{extension}"
        elif not filename.endswith(extension):
            filename += extension

        try:
            filepath = Path(filename)
            filepath.write_text(code, encoding='utf-8')
            return str(filepath.absolute())
        except Exception as e:
            raise Exception(f"Failed to save code to file: {str(e)}")

    @staticmethod
    def create_temp_file(code: str, extension: str) -> str:
        """
        Create a temporary file with the given code and extension.

        :param code: The code to write to the temporary file.
        :param extension: The file extension for the temporary file.
        :return: Path to the created temporary file.
        """

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix=extension) as temp_file:
            temp_file.write(code)
            return temp_file.name
        
    @staticmethod
    def cleanup_temp_file(filepath: str):
        """
        Remove the temporary file.

        :param filepath: Path to the temporary file to remove.
        """
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
        
    @staticmethod
    def get_language_extension(language: str) -> str:
        """
        Get file extension for the given programming language.
        
        Args:
            language: Programming language name
            
        Returns:
            str: File extension including the dot
        """
        extensions = {
            "python": ".py",
            "c#": ".cs",
            "c++": ".cpp",
            "java": ".java"
        }
        
        return extensions.get(language.lower(), ".txt")