import subprocess
import sys
import time
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from .base_executor import BaseExecutor, ExecutionResult
from ..utils.file_utils import FileManager

class PythonExecutor(BaseExecutor):
    """Executor for running Python code."""
    
    def __init__(self):
        self.file_manager = FileManager()
        

    def execute(self, code: str) -> ExecutionResult:
        """
        Execute Python code safely.
        
        Args:
            code: Python code to execute
            
        Returns:
            ExecutionResult: Execution result with output, errors, and timing
        """
        start_time = time.time()
        
        try:
            # Capture stdout and stderr
            stdout_capture = StringIO()
            stderr_capture = StringIO()
            
            # Create a restricted global environment
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                    'abs': abs,
                    'round': round,
                }
            }
            
            # Execute with output capture
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, safe_globals)
            
            execution_time = time.time() - start_time
            
            # Get captured output
            output = stdout_capture.getvalue()
            error = stderr_capture.getvalue()
            
            success = len(error) == 0
            
            return ExecutionResult(
                success=success,
                output=output,
                error=error,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time
            )
    
    def execute_file(self, code: str) -> ExecutionResult:
        """
        Execute Python code by creating a temporary file.
        Alternative method for complex code that might not work with exec().
        
        Args:
            code: Python code to execute
            
        Returns:
            ExecutionResult: Execution result
        """
        temp_file = None
        start_time = time.time()
        
        try:
            # Create temporary Python file
            temp_file = self.file_manager.create_temp_file(code, '.py')
            
            # Execute using subprocess
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                execution_time=execution_time
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error="Execution timed out (30s limit)",
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution failed: {str(e)}",
                execution_time=execution_time
            )
        finally:
            # Cleanup
            if temp_file:
                self.file_manager.cleanup_temp_file(temp_file)
    
    def is_available(self) -> bool:
        """Python executor is always available."""
        return True