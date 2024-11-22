# Testcontainers Demo Generator

A tool that generates production-quality demo applications showcasing Testcontainers integration testing patterns across different programming languages.

## Overview

This project uses AI agents to generate well-structured demo applications that demonstrate how to properly implement integration testing using Testcontainers. Each generated demo follows language-specific best practices and includes comprehensive test coverage.

The generator employs three specialized AI agents:
- Solution Architect: Designs the application architecture
- Documentation Researcher: Analyzes best practices and patterns
- Implementation Engineer: Creates the actual code and tests

## Requirements

- Python 3.11 or higher
- VS Code with Remote - Containers extension
- Docker Desktop

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/testcontainers-demo-generator.git
cd testcontainers-demo-generator
```

## Development Environment Setup

### Using VS Code Dev Containers (Recommended)

1. Install prerequisites:
   - [VS Code](https://code.visualstudio.com/)
   - [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. Open in Dev Container:
   - Open VS Code
   - Press F1 and select "Dev Containers: Open Folder in Container"
   - Select the project directory
   - Wait for the container to build and start

The dev container will automatically:
- Set up Python 3.11 environment
- Install all required dependencies
- Configure Python path and extensions
- Set up the development environment

### Manual Setup (Alternative)

If you prefer not to use dev containers:

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

2. Install dependencies:
```bash
pip install poetry
poetry install
```

## Configuration

1. Set up your environment:
   - Copy `.env.example` to `.env`
   - Add your `ANTHROPIC_API_KEY` to the `.env` file
   - Add your `OPENAI_API_KEY` to the `.env` file

2. Customize the generation:
   - Modify `src/testcontainers_demo_generator/config/agents.yaml` to configure the AI agents
   - Modify `src/testcontainers_demo_generator/config/tasks.yaml` to define generation tasks
   - Update `src/testcontainers_demo_generator/crew.py` to customize the generation logic
   - Adjust `src/testcontainers_demo_generator/main.py` for specific input parameters

## Usage

Run the demo generator:

```bash
python -m testcontainers_demo_generator.main -l java -s redis
```

Parameters:
- `-l, --language`: Target programming language (e.g., java, python, nodejs)
- `-s, --service`: Target service to demonstrate (e.g., redis, postgres, mongodb)

This will:
1. Generate a sample application with Testcontainers integration
2. Create test cases demonstrating Testcontainers usage
3. Generate documentation explaining the implementation
4. Output all files in the `demo_implementation.md` file

## Example Output

The generator creates:
- A working application with proper dependencies
- Test classes showing Testcontainers setup
- Docker configurations if needed
- README with setup and usage instructions

## Supported Technologies

Currently supports generating demos for:
- Java with JUnit
- Python with pytest
- Node.js with Jest
- (Add more as implemented)

## Contributing

Contributions are welcome! Please feel free to submit pull requests to add:
- Support for new languages/frameworks
- Additional demo scenarios
- Improvements to existing templates
- Documentation enhancements

## Support

For help and questions:
- Check our [documentation](https://docs.crewai.com)
- Visit the [Testcontainers documentation](https://testcontainers.com)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Open an issue](https://github.com/yourusername/testcontainers-demo-generator/issues)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
