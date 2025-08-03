import os
import tempfile
from pathlib import Path
from typing import Optional


class FileManager:
    """Utility class for file operations."""
    
    @staticmethod
    def save_code_to_file(code: str, language: str, filename: Optional[str] = None, save_path: Optional[str] = None) -> str:
        """
        Save code to a file with appropriate extension.
        
        Args:
            code: Code content to save
            language: Programming language (determines extension)
            filename: Optional custom filename
            save_path: Optional directory path to save the file
            
        Returns:
            str: Path to the saved file
            
        Raises:
            Exception: If save operation fails
        """
        
        extensions = {
            "c#": ".cs",
            "c++": ".cpp",
            "java": ".java"
        }
        
        if language.lower() not in extensions:
            raise ValueError(f"Unsupported language: {language}")
        
        extension = extensions[language.lower()]
        
        # Generate filename if not provided
        if not filename:
            filename = f"converted_code{extension}"
        elif not filename.endswith(extension):
            filename += extension
        
        try:
            if save_path:
                save_dir = Path(save_path)
                save_dir.mkdir(parents=True, exist_ok=True)
                filepath = save_dir / filename
            else:
                filepath = Path(filename)
            
            # Save the file
            filepath.write_text(code, encoding='utf-8')
            return str(filepath.absolute())
            
        except Exception as e:
            raise Exception(f"Failed to save file: {str(e)}")
    
    @staticmethod
    def create_temp_file(code: str, extension: str) -> str:
        """
        Create a temporary file with the given code.
        
        Args:
            code: Code content
            extension: File extension (e.g., '.py', '.cpp')
            
        Returns:
            str: Path to temporary file
        """
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=extension,
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(code)
            return f.name
    
    @staticmethod
    def cleanup_temp_file(filepath: str):
        """
        Remove temporary file if it exists.
        
        Args:
            filepath: Path to file to remove
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
    
    @staticmethod
    def get_language_extension(language: str) -> str:
        """
        Get file extension for a programming language.
        
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