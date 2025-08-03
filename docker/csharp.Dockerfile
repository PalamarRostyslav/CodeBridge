# Docker configuration for C# execution
FROM mcr.microsoft.com/dotnet/sdk:latest

# Install Mono for compatibility
RUN apt-get update && apt-get install -y \
    mono-complete \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /tmp

# Default command
CMD ["bash"]