# Testcontainers Demo Generator

A tool that generates production-quality Testcontainers integration tests for Java applications using AI assistance.

## Overview

This project uses AI (OpenAI's GPT-4o or Anthropic's Claude-3.5-sonnet) to analyze Java source code and automatically generate comprehensive Testcontainers integration tests. It can:
- Analyze Java source files for service dependencies
- Generate appropriate integration tests
- Update pom.xml with required Testcontainers dependencies
- Create a pull request with the generated tests

## Requirements

- Python 3.11 or higher
- VS Code with Remote - Containers extension
- Docker Desktop
- GitHub Personal Access Token with repo permissions
- OpenAI API Key or Anthropic API Key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/GannaChernyshova/testcontainers-demo-generator.git
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

3. After container starts, set up required environment variables:
   ```bash
   # Required:
   export GITHUB_TOKEN='your-github-personal-access-token'
   export REPO_URL='https://github.com/user/repo-to-generate-tests-for'
   
   # Choose one of:
   export OPENAI_API_KEY='your-openai-api-key'
   # OR
   export ANTHROPIC_API_KEY='your-anthropic-api-key'
   
   # Optional:
   export DEBUG='true'  # Enable verbose debug output
   ```

## Usage

### Target Repository Configuration

The target repository URL is defined in `src/github/testgenerator.py`:

```python
repo_url = "https://github.com/GannaChernyshova/test-gen-demo"
```

You can modify this URL to generate tests for any other Java repository that you want to experiment with.

### Running the Generator

Run the test generator:

```bash
python src/github/testgenerator.py
```

### Debug Mode

You can enable debug mode to see detailed output about the test generation process:
- AI responses
- File processing details
- Dependency detection
- Error details and stack traces

To enable debug mode, set the DEBUG environment variable:
```bash
export DEBUG=true
```

Or run with debug mode for a single execution:
```bash
DEBUG=true python src/github/testgenerator.py
```

The generator will:
1. Clone the target repository (specified in testgenerator.py)
2. Create a new feature branch
3. Scan Java source files for:
   - Service dependencies
   - Database connections
   - Message queues
   - Cache configurations
   - External API clients
4. Generate integration tests with:
   - Proper package structure
   - Required imports
   - Testcontainers configuration
   - Test data initialization
   - Cleanup procedures
5. Update pom.xml with necessary dependencies
6. Commit changes and create a pull request

## Generated Test Features

The generated tests include:
- Proper package and import statements
- JUnit Jupiter integration
- Spring Boot Test configuration
- Testcontainers setup for detected services
- Database connection management
- Test data initialization
- Resource cleanup
- Comprehensive assertions

## Supported Services

Currently detects and generates tests for:
- PostgreSQL databases
- Redis caches
- MongoDB databases
- Message queues
- External services

## Test Generation Rules

The generator follows these rules:
1. Maintains original package structure
2. Uses Testcontainers for all external services
3. Properly configures Spring Boot test environment
4. Initializes test data in @BeforeEach
5. Cleans up resources in @AfterEach
6. Uses TestRestTemplate for controller tests
7. Avoids mocking in favor of real service containers
8. Includes proper assertions and verifications

## Contributing

Contributions are welcome! Please feel free to submit pull requests to add:
- Support for additional services
- Improved test generation patterns
- Better dependency detection
- Documentation enhancements

## Support

For help and questions:
- Visit the [Testcontainers documentation](https://testcontainers.com)
- [Open an issue](https://github.com/GannaChernyshova/testcontainers-demo-generator/issues)

## License

This project is licensed under the Apache Software License - see the LICENSE file for details.
