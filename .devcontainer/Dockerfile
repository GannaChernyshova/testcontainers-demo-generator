FROM mcr.microsoft.com/vscode/devcontainers/python:3.11

# Install additional tools (optional)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && apt-get clean

# Set the working directory
WORKDIR /workspace
