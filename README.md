## # 🐍➡️💻 Python Code Converter

A sophisticated Python application that converts Python code to C#, C++, or Java using AI models, with integrated code execution and validation.

## ✨ Features

- **Multiple AI Models**: 
  - Qwen2.5-7B-Instruct (Local CUDA model)
  - OpenAI GPT-4o-mini (API)
  - Claude Sonnet 4 (API)

- **Code Conversion**: Convert Python algorithms to C#, C++, or Java to compare performance.

- **Safe Code Execution**: 
  - Python code execution with restricted environment
  - Compiled language execution using Docker containers for isolation

- **User-Friendly Interface**: Clean Gradio web interface with syntax validation and error handling

- **File Management**: Save converted code to desired folder with appropriate file extensions

## UI Example

<img width="1734" height="1271" alt="image" src="https://github.com/user-attachments/assets/6677f7c9-3adb-4482-8f62-06b89c9d1f51" />
<img width="1669" height="1155" alt="image" src="https://github.com/user-attachments/assets/9457a343-377f-4197-837f-da04f5dd1ef7" />
<img width="1450" height="637" alt="image" src="https://github.com/user-attachments/assets/93c24296-2e30-404a-bf95-4fd4fdee1fc3" />

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** with pip
2. **Docker Desktop** (for executing converted code)
3. **CUDA-compatible GPU** (optional, for local Qwen model)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd python-code-converter
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Docker installation**:
   ```bash
   docker --version
   docker run hello-world
   ```

### Running the Application

```bash
python app.py
```

The application will start on `http://localhost:7860`

## 🏗️ Architecture

The application follows clean architecture principles with clear separation of concerns:

```
python-code-converter/
├── app.py                 # Main Gradio application
├── core/
│   ├── models/           # AI model implementations
│   │   ├── base_model.py     # Abstract base class
│   │   ├── qwen_model.py     # Local Qwen model
│   │   ├── openai_model.py   # OpenAI API integration
│   │   └── claude_model.py   # Claude API integration
│   ├── executors/        # Code execution engines
│   │   ├── base_executor.py  # Abstract executor
│   │   ├── base_docker_executor.py  # Abstract docker executor
│   │   ├── language_strategy.py  # strategy for models
│   │   ├── python_executor.py # Python code execution
│   │   └── docker_executor.py # Docker-based execution
│   └── utils/           # Utility functions
│       ├── validators.py     # Input validation
│       └── file_utils.py     # File operations
├── docker/              # Docker configurations
│   ├── cpp.Dockerfile
│   ├── csharp.Dockerfile
│   └── java.Dockerfile
└── requirements.txt
```

### Design Patterns

- **Strategy Pattern**: Interchangeable AI models and executors
- **Template Method**: Base classes with standardized interfaces
- **Factory Pattern**: Model and executor instantiation
- **Single Responsibility**: Each class has one clear purpose
- **Dependency Inversion**: Abstractions don't depend on details

## 🔧 Configuration

### API Keys

For OpenAI and Claude models, you'll need API keys:

1. **OpenAI**
2. **Claude**

Enter API keys in the interface when selecting these models.

### Local Model Setup

For the Qwen model:

1. Ensure you have a CUDA-compatible GPU
2. Install PyTorch with CUDA support:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

## 🐳 Docker Execution

The application uses Docker containers to safely execute compiled code:

- **C++**: Uses `gcc:latest` image
- **C#**: Uses `mcr.microsoft.com/dotnet/sdk:8.0` image  
- **Java**: Uses `openjdk:11` image

### Security Features

- **Isolated Execution**: Code runs in disposable containers
- **Resource Limits**: Memory and CPU constraints
- **Network Disabled**: No internet access during execution
- **Temporary Files**: Automatic cleanup after execution

## 💡 Usage Examples

### Basic Conversion

1. Enter Python code in the input box
2. Select target language (C#, C++, Java)
3. Choose AI model
4. Click "Convert Code"

### Example Input

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

numbers = [64, 34, 25, 12, 22, 11, 90]
print("Original array:", numbers)
sorted_numbers = bubble_sort(numbers.copy())
print("Sorted array:", sorted_numbers)
```

### Code Execution

- **Python Execution**: Click "Execute Python Code" to run original code
- **Converted Execution**: Click "Execute Converted" to run the generated code in Docker

## 🚨 Troubleshooting

### Common Issues

1. **Docker not available**: Ensure Docker Desktop is running
2. **CUDA not detected**: Check GPU drivers and PyTorch CUDA installation
3. **API key errors**: Verify API keys are correct and have sufficient credits
4. **Model loading fails**: Check internet connection and disk space

### Debug Mode

Run with debug output:
```bash
PYTHONPATH=. python app.py --debug
```
