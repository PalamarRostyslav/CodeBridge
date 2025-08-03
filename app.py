#!/usr/bin/env python3
"""
Python Code Converter - Main Application
A Gradio-based application for converting Python code to other languages using AI models.
"""

import gradio as gr
import os
import traceback
from typing import Optional, Tuple

# Import core modules
from core.models import QwenModel, OpenAIModel, ClaudeModel
from core.executors import PythonExecutor
from core.executors.docker_executor import DockerExecutor
from core.utils import CodeValidator, FileManager


class CodeConverterApp:
    """Main application class for the Python Code Converter."""
    
    def __init__(self):
        self.models = {
            "Qwen2.5-7B-Instruct (Local)": QwenModel(),
            "OpenAI GPT-4o-mini": OpenAIModel(),
            "Claude Sonnet 4": ClaudeModel()
        }
        
        self.python_executor = PythonExecutor()
        self.docker_executor = DockerExecutor()
        self.file_manager = FileManager()
        self.validator = CodeValidator()
        
        # Current API keys
        self.current_openai_key = None
        self.current_claude_key = None
        
        # Check Docker and language support on startup
        self._initialize_docker_support()
    
    def _initialize_docker_support(self):
        """Initialize Docker support and log available languages."""
        if self.docker_executor.is_available():
            supported_languages = self.docker_executor.get_supported_languages()
            print(f"✅ Docker: Available with support for {', '.join(supported_languages)}")
            
            # Log language configurations
            for lang in supported_languages:
                info = self.docker_executor.get_language_info(lang)
                if 'error' not in info:
                    print(f"   📋 {lang.upper()}: {info['image']} (timeout: {info['timeout']}s)")
        else:
            print("⚠️ Docker: Not available - compiled language execution disabled")
    
    def update_api_key(self, model_name: str, api_key: str) -> str:
        """Update API key for the selected model."""
        try:
            if "OpenAI" in model_name:
                self.current_openai_key = api_key
                self.models["OpenAI GPT-4o-mini"].update_api_key(api_key)
                return "✅ OpenAI API key updated successfully"
            elif "Claude" in model_name:
                self.current_claude_key = api_key
                self.models["Claude Sonnet 4"].update_api_key(api_key)
                return "✅ Claude API key updated successfully"
            else:
                return "ℹ️ No API key required for local model"
        except Exception as e:
            return f"❌ Failed to update API key: {str(e)}"
    
    def convert_code(
        self, 
        python_code: str, 
        target_language: str, 
        model_name: str, 
        add_comments: bool,
        api_key: str
    ) -> str:
        """Convert Python code to target language using selected model."""
        try:
            # Validate input
            if not python_code.strip():
                return "❌ **Error:** Please provide Python code to convert."
            
            # Validate Python syntax
            is_valid, error_msg = self.validator.validate_python_code(python_code)
            if not is_valid:
                return f"❌ **Invalid Python Code:** {error_msg}"
            
            # Update API key if provided
            if api_key and api_key.strip():
                key_update_msg = self.update_api_key(model_name, api_key.strip())
                if "Failed" in key_update_msg:
                    return key_update_msg
            
            # Get the selected model
            model = self.models.get(model_name)
            if not model:
                return f"❌ **Error:** Unknown model: {model_name}"
            
            # Check if model is available
            if not model.is_available():
                if "OpenAI" in model_name:
                    return "❌ **Error:** OpenAI API key is required. Please provide your API key."
                elif "Claude" in model_name:
                    return "❌ **Error:** Claude API key is required. Please provide your API key."
                elif "Qwen" in model_name:
                    return "❌ **Error:** Qwen model is not available. Please check CUDA installation and model files."
            
            # Convert the code
            converted_code = model.convert_code(python_code, target_language, add_comments)
            
            return f"✅ **Conversion Successful**\n\n```{target_language.lower()}\n{converted_code}\n```"
            
        except Exception as e:
            error_trace = traceback.format_exc()
            return f"❌ **Conversion Failed:** {str(e)}\n\n**Debug Info:**\n```\n{error_trace}\n```"
    
    def execute_python_code(self, python_code: str) -> str:
        """Execute Python code and return results."""
        try:
            if not python_code.strip():
                return "❌ **Error:** Please provide Python code to execute."
            
            # Validate Python syntax
            is_valid, error_msg = self.validator.validate_python_code(python_code)
            if not is_valid:
                return f"❌ **Invalid Python Code:** {error_msg}"
            
            # Execute the code
            result = self.python_executor.execute(python_code)
            return result.format_results()
            
        except Exception as e:
            return f"❌ **Execution Failed:** {str(e)}"
    
    def execute_converted_code(self, converted_code: str, target_language: str) -> str:
        """Execute converted code using Docker."""
        try:
            if not converted_code.strip():
                return "❌ **Error:** No converted code to execute."
            
            # Clean the converted code (remove markdown formatting if present)
            code = self._clean_code_output(converted_code)
            
            if not self.docker_executor.is_available():
                return "❌ **Error:** Docker is not available. Please ensure Docker is installed and running."
            
            # Validate language support
            if not self.docker_executor.validate_language_support(target_language):
                supported = ", ".join(self.docker_executor.get_supported_languages())
                return f"❌ **Error:** Language '{target_language}' is not supported. Supported languages: {supported}"
            
            # Execute using Docker
            result = self.docker_executor.execute(code, target_language)
            return result.format_results()
            
        except Exception as e:
            return f"❌ **Execution Failed:** {str(e)}"
    
    def save_converted_code(self, converted_code: str, target_language: str) -> str:
        """Save converted code to file."""
        try:
            if not converted_code.strip():
                return "❌ **Error:** No code to save."
            
            # Clean the converted code
            code = self._clean_code_output(converted_code)
            
            # Save to file
            filepath = self.file_manager.save_code_to_file(code, target_language)
            return f"✅ **File Saved Successfully**\n\nSaved to: `{filepath}`"
            
        except Exception as e:
            return f"❌ **Save Failed:** {str(e)}"
    
    def _clean_code_output(self, output: str) -> str:
        """Clean code output by removing markdown formatting and status messages."""
        lines = output.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            # Skip status messages
            if line.strip().startswith(('✅', '❌', '**Error:**', '**Conversion')):
                continue
            
            # Handle code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            # If we're in a code block or this looks like code, add it
            if in_code_block or (line.strip() and not line.startswith('*')):
                code_lines.append(line)
        
        return '\n'.join(code_lines).strip()
    
    def get_api_key_visibility(self, model_name: str) -> bool:
        """Determine if API key input should be visible."""
        return "OpenAI" in model_name or "Claude" in model_name
    
    def create_interface(self):
        """Create and return the Gradio interface."""
        
        # Custom CSS for better styling
        css = """
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .code-input, .code-output {
            font-family: 'Monaco', 'Consolas', monospace !important;
        }
        
        .status-success {
            color: #22c55e;
        }
        
        .status-error {
            color: #ef4444;
        }
        """
        
        with gr.Blocks(css=css, title="Python Code Converter", theme=gr.themes.Soft()) as app:
            gr.Markdown(
                """
                # 🐍➡️💻 Python Code Converter
                
                Convert your Python code to C#, C++, or Java using AI models!
                
                **Features:**
                - Multiple AI models (Local Qwen, OpenAI GPT-4o-mini, Claude Sonnet 4)
                - Code execution with Docker isolation
                - Syntax validation and error handling
                - Save generated code to files
                """,
                elem_classes=["container"]
            )
            
            with gr.Row():
                with gr.Column(scale=1):
                    # Input section
                    gr.Markdown("## 📝 Input")
                    
                    python_input = gr.Textbox(
                        label="Python Code",
                        placeholder="Enter your Python code here...",
                        lines=10,
                        elem_classes=["code-input"]
                    )
                    
                    with gr.Row():
                        target_language = gr.Dropdown(
                            choices=["C#", "C++", "Java"],
                            label="Target Language",
                            value="C++",
                            interactive=True
                        )
                        
                        model_selection = gr.Dropdown(
                            choices=list(self.models.keys()),
                            label="AI Model",
                            value="Qwen2.5-7B-Instruct (Local)",
                            interactive=True
                        )
                    
                    api_key_input = gr.Textbox(
                        label="API Key",
                        placeholder="Enter your API key (for OpenAI/Claude models)",
                        type="password",
                        visible=False
                    )
                    
                    add_comments = gr.Checkbox(
                        label="Add explanatory comments",
                        value=False
                    )
                    
                    convert_btn = gr.Button("🔄 Convert Code", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    # Output section
                    gr.Markdown("## 💻 Generated Code")
                    
                    converted_output = gr.Textbox(
                        label="Converted Code",
                        lines=12,
                        elem_classes=["code-output"],
                        interactive=False
                    )
                    
                    with gr.Row():
                        save_btn = gr.Button("💾 Save Code", variant="secondary")
                        execute_converted_btn = gr.Button("▶️ Execute Converted", variant="secondary")
                    
                    save_status = gr.Textbox(
                        label="Save Status",
                        lines=2,
                        interactive=False
                    )
            
            # Execution Results Section
            gr.Markdown("## 🚀 Execution Results")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Python Code Execution")
                    execute_python_btn = gr.Button("▶️ Execute Python Code", variant="secondary")
                    python_result = gr.Textbox(
                        label="Python Execution Result",
                        lines=6,
                        interactive=False
                    )
                
                with gr.Column():
                    gr.Markdown("### Converted Code Execution")
                    converted_result = gr.Textbox(
                        label="Converted Code Execution Result",
                        lines=6,
                        interactive=False
                    )
            
            # Event handlers
            def update_api_key_visibility(model_name):
                return gr.update(visible=self.get_api_key_visibility(model_name))
            
            model_selection.change(
                fn=update_api_key_visibility,
                inputs=[model_selection],
                outputs=[api_key_input]
            )
            
            convert_btn.click(
                fn=self.convert_code,
                inputs=[python_input, target_language, model_selection, add_comments, api_key_input],
                outputs=[converted_output]
            )
            
            execute_python_btn.click(
                fn=self.execute_python_code,
                inputs=[python_input],
                outputs=[python_result]
            )
            
            execute_converted_btn.click(
                fn=self.execute_converted_code,
                inputs=[converted_output, target_language],
                outputs=[converted_result]
            )
            
            save_btn.click(
                fn=self.save_converted_code,
                inputs=[converted_output, target_language],
                outputs=[save_status]
            )
            
            gr.Markdown(
                """
                ## 📚 Example Python Code
                
                Try this bubble sort implementation:
                
                ```python
                def bubble_sort(arr):
                    n = len(arr)
                    for i in range(n):
                        for j in range(0, n - i - 1):
                            if arr[j] > arr[j + 1]:
                                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    return arr
                
                # Test the function
                numbers = [64, 34, 25, 12, 22, 11, 90]
                print("Original array:", numbers)
                sorted_numbers = bubble_sort(numbers.copy())
                print("Sorted array:", sorted_numbers)
                ```
                
                ## 🐳 Docker Status
                """
            )
            
            # Add Docker status information
            if self.docker_executor.is_available():
                supported_langs = self.docker_executor.get_supported_languages()
                docker_status = f"✅ **Docker is running** - Supported languages: {', '.join(supported_langs).upper()}"
            else:
                docker_status = "❌ **Docker is not available** - Please install and start Docker Desktop"
            
            gr.Markdown(docker_status)
        
        return app


def main():
    """Main function to run the application."""
    print("🚀 Starting Python Code Converter...")
    
    # Check dependencies
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
    except ImportError:
        print("❌ PyTorch not installed")
    
    try:
        import docker
        client = docker.from_env()
        client.ping()
        print("✅ Docker: Connected")
    except Exception as e:
        print(f"⚠️ Docker: {e}")
    
    # Initialize and run app
    app = CodeConverterApp()
    interface = app.create_interface()
    
    print("\n🌐 Starting Gradio interface...")
    print("📱 Access the app at: http://localhost:7860")
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()