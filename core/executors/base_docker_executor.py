import docker
import time
import tempfile
import shutil
import json
import os
from pathlib import Path
from typing import Dict, Any
from .base_executor import BaseExecutor, ExecutionResult


class BaseDockerExecutor(BaseExecutor):
    """Base class for Docker-based code execution with shared functionality."""
    
    def __init__(self, config_path: str = None):
        self.client = None
        self.config = self._load_config(config_path)
        self._initialize_docker()
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if config_path is None:
            current_dir = Path(__file__).parent.parent.parent
            config_path = current_dir / "config" / "language_config.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _initialize_docker(self):
        """Initialize Docker client."""
        try:
            self.client = docker.from_env()
            self.client.ping()
        except Exception as e:
            print(f"Docker initialization failed: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Docker is available."""
        return self.client is not None
    
    def _ensure_image_available(self, image: str):
        """Ensure Docker image is available, pull if necessary."""
        try:
            self.client.images.get(image)
        except docker.errors.ImageNotFound:
            print(f"Pulling Docker image: {image}")
            self.client.images.pull(image)
    
    def _create_container(self, image: str, command: str, temp_dir: str, working_dir: str) -> object:
        """
        Create and start a Docker container.
        
        Args:
            image: Docker image name
            command: Command to execute
            temp_dir: Host temporary directory
            working_dir: Container working directory
            
        Returns:
            Docker container object
        """
        docker_config = self.config['docker']
        
        return self.client.containers.run(
            image=image,
            command=command,
            volumes={temp_dir: {'bind': working_dir, 'mode': 'rw'}},
            working_dir=working_dir,
            detach=True,
            remove=False,
            mem_limit=docker_config.get('memory_limit', '512m'),
            cpu_period=docker_config.get('cpu_period', 100000),
            cpu_quota=docker_config.get('cpu_quota', 50000),
            network_disabled=docker_config.get('network_disabled', True)
        )
    
    def _wait_for_container(self, container: object, timeout: int) -> ExecutionResult:
        """
        Wait for container completion and collect results.
        
        Args:
            container: Docker container object
            timeout: Timeout in seconds
            
        Returns:
            ExecutionResult: Execution result
        """
        start_time = time.time()
        
        try:
            # Wait for completion
            exit_info = container.wait(timeout=timeout)
            exit_code = exit_info['StatusCode']
            
            # Get logs
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            
            execution_time = time.time() - start_time
            
            # Success if exit code is 0
            success = exit_code == 0
            
            if success:
                return ExecutionResult(
                    success=True,
                    output=logs,
                    error="",
                    execution_time=execution_time
                )
            else:
                return ExecutionResult(
                    success=False,
                    output="",
                    error=logs,
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Try to get logs if possible
            logs = ""
            try:
                logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            except Exception:
                pass
            
            return ExecutionResult(
                success=False,
                output="",
                error=f"Container execution error: {str(e)}\nLogs: {logs}",
                execution_time=execution_time
            )
        finally:
            # Always clean up container
            self._cleanup_container(container)
    
    def _cleanup_container(self, container: object):
        """Clean up Docker container."""
        try:
            container.remove(force=True)
        except Exception:
            pass  # Ignore cleanup errors
    
    def _create_temp_directory(self) -> str:
        """Create temporary directory for code execution."""
        return tempfile.mkdtemp()
    
    def _cleanup_temp_directory(self, temp_dir: str):
        """Clean up temporary directory."""
        try:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception:
            pass  # Ignore cleanup errors
    
    def _handle_execution_error(self, error: Exception, execution_time: float) -> ExecutionResult:
        """
        Handle execution errors in a centralized way.
        
        Args:
            error: Exception that occurred
            execution_time: Time taken before error
            
        Returns:
            ExecutionResult: Error result
        """
        error_msg = f"Execution failed: {str(error)}"
        
        # Add specific error handling for common Docker issues
        if "No such container" in str(error):
            error_msg = "Container was removed unexpectedly. This might be a Docker configuration issue."
        elif "timeout" in str(error).lower():
            error_msg = "Execution timed out. Your code might be running an infinite loop or taking too long."
        elif "permission denied" in str(error).lower():
            error_msg = "Permission denied. Check Docker permissions and file access rights."
        elif "no space left" in str(error).lower():
            error_msg = "No disk space available for code execution."
        
        return ExecutionResult(
            success=False,
            output="",
            error=error_msg,
            execution_time=execution_time
        )
    
    def get_supported_languages(self) -> list:
        """Get list of supported programming languages."""
        return list(self.config['languages'].keys())
    
    def get_language_config(self, language: str) -> Dict[str, Any]:
        """
        Get configuration for a specific language.
        
        Args:
            language: Programming language name
            
        Returns:
            Dict: Language configuration
            
        Raises:
            ValueError: If language is not supported
        """
        language = language.lower()
        if language not in self.config['languages']:
            raise ValueError(f"Unsupported language: {language}. Supported: {self.get_supported_languages()}")
        
        return self.config['languages'][language]