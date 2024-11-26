# Testcontainers Demo Implementation

Generated for JAVA with kafka

# Demo Application and Tests Documentation

This document provides comprehensive setup instructions, running instructions, configuration details, and troubleshooting tips for the demo application using Testcontainers with Kafka.

## 1. Setup Instructions

### Prerequisites
- **Java JDK 11+**: Ensure that you have Java Development Kit version 11 or higher installed on your machine.
- **Maven 3.6+**: Apache Maven must be installed to manage dependencies and run the application.
- **Docker**: You need Docker installed and running to create containerized instances of services needed for tests.

### Dependencies
Add the following dependencies to your `pom.xml` within the `<dependencies>` section:

```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka-test</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>junit-jupiter</artifactId>
    <scope>test</scope>
</dependency>
```

### Configuration Steps
1. Ensure you have a working Kafka broker setup. You can use Testcontainers to pull and run a Kafka instance automatically if you are running tests.
2. Create a new Java class file named `MessageControllerTest.java` and place it in the directory `src/test/java/com/example/`.

### Build Commands
Execute the following command in the terminal from the project root directory to build the application and resolve the dependencies:
```bash
mvn clean install
```

## 2. Running Instructions

### How to Build
To build the project, run the following command:
```bash
mvn package
```

### How to Run the Application
Ensure the Kafka broker is running (either set up externally or via Testcontainers when executing tests). To run the application, use:
```bash
mvn spring-boot:run
```

### How to Run the Tests
To execute the tests including the `MessageControllerTest`, use:
```bash
mvn test
```

### Expected Output
When running tests, you should see output indicating successful execution similar to:
```
-------------------------------------------------------
 T E S T S
-------------------------------------------------------
Running com.example.MessageControllerTest
Test run finished after 123 milliseconds
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
-------------------------------------------------------
```

## 3. Configuration Details
- **Kafka topic**: The test uses an embedded Kafka broker that automatically creates the topic `demo_topic`.
- **MockMvc**: Used for testing the HTTP endpoints without launching a server.
  
## 4. Troubleshooting Guide

### Common Issues and Solutions

1. **Docker Not Running**: 
   - **Issue**: Tests fail due to Docker not being accessible.
   - **Solution**: Ensure Docker is installed and running. Verify by executing `docker ps`.

2. **Java Version Issues**:
   - **Issue**: Wrong Java version being used.
   - **Solution**: Check Java version with `java -version` and ensure it is 11 or higher.

3. **Missing Dependencies**:
   - **Issue**: Dependency resolution fails.
   - **Solution**: Run `mvn clean install` to force Maven to resolve and download all required dependencies.

4. **Issues with MockMvc**:
   - **Issue**: MockMvc setup fails or produces errors.
   - **Solution**: Ensure the correct Spring Boot and JUnit dependencies are included and the context is properly configured.

5. **Kafka Not Available**:
   - **Issue**: Encountering "topic not found" or similar errors during tests.
   - **Solution**: Verify that the embedded Kafka has started and the topic exists; check Docker logs for the Kafka container.

This detailed documentation should enable developers to set up and run the demo application and tests without any uncertainty.