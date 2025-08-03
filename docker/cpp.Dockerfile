# Docker configuration for C++ execution
FROM gcc:latest

# Install additional tools if needed
RUN apt-get update && apt-get install -y \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /tmp

# Default command
CMD ["bash"]