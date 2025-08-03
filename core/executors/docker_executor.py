import time
from .base_docker_executor import BaseDockerExecutor
from .language_strategy import LanguageStrategyFactory
from .base_executor import ExecutionResult


class DockerExecutor(BaseDockerExecutor):
    """Refactored Docker executor using Strategy pattern for language-specific execution."""
    
    def __init__(self, config_path: str = None):
        super().__init__(config_path)
        self.strategy_factory = LanguageStrategyFactory()
    
    def execute(self, code: str, language: str) -> ExecutionResult:
        """
        Execute code in a Docker container using appropriate language strategy.
        
        Args:
            code: Source code to execute
            language: Programming language
            
        Returns:
            ExecutionResult: Execution result with output, errors, and timing
        """
        if not self.is_available():
            return ExecutionResult(
                success=False,
                output="",
                error="Docker is not available. Please ensure Docker is installed and running.",
                execution_time=0.0
            )
        
        start_time = time.time()
        temp_dir = None
        
        try:
            # Get language configuration and strategy
            language_config = self.get_language_config(language)
            strategy = self.strategy_factory.create_strategy(language, language_config)
            
            temp_dir = self._create_temp_directory()
            prep_info = strategy.prepare_code(code, temp_dir)
            
            command = strategy.get_execution_command(prep_info)
            
            # Ensure Docker image is available
            image = strategy.get_image()
            self._ensure_image_available(image)
            
            container = self._create_container(
                image=image,
                command=command,
                temp_dir=temp_dir,
                working_dir=strategy.get_working_dir()
            )
            
            result = self._wait_for_container(container, strategy.get_timeout())
            
            return result
            
        except ValueError as e:
            # Language not supported or configuration error
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self._handle_execution_error(e, execution_time)
            
        finally:
            if temp_dir:
                self._cleanup_temp_directory(temp_dir)
    
    def get_language_info(self, language: str) -> dict:
        """
        Get information about a specific language.
        
        Args:
            language: Programming language name
            
        Returns:
            dict: Language information including image, commands, etc.
        """
        try:
            config = self.get_language_config(language)
            strategy = self.strategy_factory.create_strategy(language, config)
            
            return {
                'language': language,
                'image': strategy.get_image(),
                'working_dir': strategy.get_working_dir(),
                'timeout': strategy.get_timeout(),
                'file_extension': config.get('file_extension', ''),
                'project_based': config.get('project_based', False)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def validate_language_support(self, language: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language: Programming language name
            
        Returns:
            bool: True if supported, False otherwise
        """
        try:
            self.get_language_config(language)
            return True
        except ValueError:
            return False