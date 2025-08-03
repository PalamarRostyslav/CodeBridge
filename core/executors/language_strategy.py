from abc import ABC, abstractmethod
from typing import Dict, Any
import os

class LanguageStrategy(ABC):
    """Abstract base class for language-specific execution strategies."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    def prepare_code(self, code: str, temp_dir: str) -> Dict[str, str]:
        """
        Prepare code for execution (create files, setup project structure).
        
        Args:
            code: Source code to prepare
            temp_dir: Temporary directory path
            
        Returns:
            Dict containing preparation info (filename, commands, etc.)
        """
        pass
    
    @abstractmethod
    def get_execution_command(self, prep_info: Dict[str, str]) -> str:
        """
        Get the command to execute in Docker container.
        
        Args:
            prep_info: Information from prepare_code step
            
        Returns:
            str: Command to execute
        """
        pass
    
    def get_image(self) -> str:
        """Get Docker image for this language."""
        return self.config['image']
    
    def get_working_dir(self) -> str:
        """Get working directory for Docker container."""
        return self.config.get('working_dir', '/tmp')
    
    def get_timeout(self) -> int:
        """Get execution timeout in seconds."""
        return self.config.get('timeout', 30)


class CppStrategy(LanguageStrategy):
    """Strategy for C++ code execution."""
    
    def prepare_code(self, code: str, temp_dir: str) -> Dict[str, str]:
        """Prepare C++ code for compilation and execution."""
        filename = "code.cpp"
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return {
            'filename': filename,
            'compile_cmd': self.config['compile_command'],
            'run_cmd': self.config['run_command']
        }
    
    def get_execution_command(self, prep_info: Dict[str, str]) -> str:
        """Get C++ execution command."""
        compile_cmd = prep_info['compile_cmd']
        run_cmd = prep_info['run_cmd']
        return f"bash -c '{compile_cmd} && {run_cmd}'"


class JavaStrategy(LanguageStrategy):
    """Strategy for Java code execution."""
    
    def prepare_code(self, code: str, temp_dir: str) -> Dict[str, str]:
        """Prepare Java code for compilation and execution."""
        class_name = self._extract_class_name(code)
        if not class_name:
            raise ValueError("Could not extract class name from Java code. Make sure your code contains a public class.")
        
        filename = f"{class_name}.java"
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        
        compile_cmd = self.config['compile_command'].format(class_name=class_name)
        run_cmd = self.config['run_command'].format(class_name=class_name)
        
        return {
            'filename': filename,
            'class_name': class_name,
            'compile_cmd': compile_cmd,
            'run_cmd': run_cmd
        }
    
    def get_execution_command(self, prep_info: Dict[str, str]) -> str:
        """Get Java execution command."""
        compile_cmd = prep_info['compile_cmd']
        run_cmd = prep_info['run_cmd']
        return f"bash -c '{compile_cmd} && {run_cmd}'"
    
    def _extract_class_name(self, code: str) -> str:
        """Extract class name from Java code."""
        import re
        
        # Look for public class first
        pattern = r'public\s+class\s+(\w+)'
        match = re.search(pattern, code)
        if match:
            return match.group(1)
        
        # Fallback to any class
        pattern = r'class\s+(\w+)'
        match = re.search(pattern, code)
        if match:
            return match.group(1)
        
        return ""


class CsharpStrategy(LanguageStrategy):
    """Strategy for C# code execution."""
    
    def prepare_code(self, code: str, temp_dir: str) -> Dict[str, str]:
        """Prepare C# code with proper project structure."""
        # Wrap code if needed
        program_cs_content = self._wrap_code(code)
        
        # Write Program.cs
        program_file = os.path.join(temp_dir, "Program.cs")
        with open(program_file, 'w', encoding='utf-8') as f:
            f.write(program_cs_content)
        
        # Create project file
        csproj_content = '''<Project Sdk="Microsoft.NET.Sdk">
        <PropertyGroup>
            <OutputType>Exe</OutputType>
            <TargetFramework>net8.0</TargetFramework>
            <ImplicitUsings>enable</ImplicitUsings>
            <Nullable>enable</Nullable>
        </PropertyGroup>
        </Project>'''
        
        csproj_file = os.path.join(temp_dir, "Program.csproj")
        with open(csproj_file, 'w', encoding='utf-8') as f:
            f.write(csproj_content)
        
        return {
            'filename': 'Program.cs',
            'project_file': 'Program.csproj'
        }
    
    def get_execution_command(self, prep_info: Dict[str, str]) -> str:
        """Get C# execution command."""
        return "bash -c 'dotnet run'"
    
    def _wrap_code(self, code: str) -> str:
        """Wrap C# code in proper Main method if needed."""
        if "static void Main" in code or "class " in code:
            return code
        
        wrapped_code = f'''using System;
            using System.Collections.Generic;
            using System.Linq;

            namespace Program
            {{
                class Program
                {{
                    static void Main(string[] args)
                    {{
            {self._indent_code(code, 12)}
                    }}
                }}
            }}'''
            
        return wrapped_code
    
    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent code by specified number of spaces."""
        indent = " " * spaces
        lines = code.split('\n')
        return '\n'.join(indent + line if line.strip() else line for line in lines)


class LanguageStrategyFactory:
    """Factory for creating language strategies."""
    
    _strategies = {
        'c++': CppStrategy,
        'java': JavaStrategy,
        'c#': CsharpStrategy
    }
    
    @classmethod
    def create_strategy(cls, language: str, config: Dict[str, Any]) -> LanguageStrategy:
        """
        Create a strategy for the specified language.
        
        Args:
            language: Programming language name
            config: Language configuration
            
        Returns:
            LanguageStrategy: Strategy instance for the language
            
        Raises:
            ValueError: If language is not supported
        """
        language = language.lower()
        if language not in cls._strategies:
            raise ValueError(f"Unsupported language: {language}")
        
        strategy_class = cls._strategies[language]
        return strategy_class(config)
    
    @classmethod
    def get_supported_languages(cls) -> list:
        """Get list of supported languages."""
        return list(cls._strategies.keys())