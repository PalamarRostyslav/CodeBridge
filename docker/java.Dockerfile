# Docker configuration for Java execution
FROM openjdk:latest

# Install additional tools
RUN apt-get update && apt-get install -y \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /tmp

# Default command
CMD ["bash"]