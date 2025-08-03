from abc import ABC, abstractmethod
from typing import Dict, Any
import time

class ExecutionResult:
    """Container for execution results."""

    def __init__(self, success: bool, output: str, error: str, execution_time: float):
        self.output = output
        self.error = error
        self.execution_time = execution_time
        self.success = success
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time
        }
    
    def format_result(self) -> str:
        """Format result for display."""
        result = f"⏱️ Execution Time: {self.execution_time:.3f}s\n\n"
        
        if self.success:
            result += "✅ **Execution Successful**\n\n"
            if self.output:
                result += f"**Output:**\n{self.output}\n"
            else:
                result += "**Output:** (No output produced)\n"
        else:
            result += "❌ **Execution Failed**\n\n"
            if self.error:
                result += f"**Error:**\n{self.error}\n"
        
        return result

class BaseExecutor(ABC):
    @abstractmethod
    def execute(self, code: str, language: str = None) -> ExecutionResult:
        """
        Execute the provided code.
        
        Args:
            code: Code to execute
            
        Returns:
            ExecutionResult: Result of execution
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the executor is available and properly configured."""
        pass
    

    def _measure_execution_time(self, func):
        """Decorator to measure execution time."""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            return result, end_time - start_time
        return wrapper