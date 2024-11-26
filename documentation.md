# Comprehensive Documentation for Demo Application and Testcontainers Tests

This document provides a detailed guide for setting up and running the demo application, which integrates with Kafka using Spring, as well as testing using Testcontainers.

## 1. Demo Application Documentation

### 1.1 Architecture and Design

The demo application follows a microservices architecture where the components communicate through Kafka. The application enables message publishing and subscribing for a specific topic. Spring Boot acts as the main framework to manage various application's configurations and supports Kafka messaging.

### 1.2 Code Structure

The project structure is organized as follows:
```
src/
 └─ main/
     ├─ java/
     │   └─ com/
     │       └─ example/
     │           └─ service/
     │               └─ MessageService.java
     └─ resources/
         └─ application.yml
 └─ test/
     └─ java/
         └─ com/
             └─ example/
                 └─ service/
                     └─ MessageServiceTest.java
```
- `MessageService.java`: Contains logic for publishing messages to Kafka.
- `MessageServiceTest.java`: Contains JUnit tests for the MessageService class.

### 1.3 Kafka Integration

The application leverages Spring Kafka for interaction with Kafka. It sends and receives messages through defined topics. The KafkaProducer is used to send messages, while KafkaConsumer is employed to consume messages.

## 2. Testcontainers Tests Documentation

### 2.1 Test Approach

The tests utilize Testcontainers to provide a lightweight, isolated environment for running Kafka in a Docker container. This allows testing message sending and receiving functionality without needing a local Kafka installation.

### 2.2 Container Setup

Using Testcontainers, a Kafka container is configured and started before each test. The lifecycle is handled automatically through Spring's JUnit integration.

- In the `MessageServiceTest.java`, the Kafka container is defined with:
   ```java
   private static final KafkaContainer kafkaContainer = new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:latest"));
   ```

### 2.3 Test Data Management

Data for tests is created and consumed dynamically. For example, messages are sent to a specific topic (`demo_topic`), and the tests verify that the message received matches what was sent.

## 3. Setup Guide

### 3.1 Prerequisites

- Java Development Kit (JDK) 11 or higher
- Maven (for dependency management)
- Docker (to run Testcontainers)
  
### 3.2 Dependencies

Add the following dependencies to your `pom.xml` to use Testcontainers and Spring Kafka features:

```xml
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers</artifactId>
    <version>1.17.2</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>kafka</artifactId>
    <version>1.17.2</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka-test</artifactId>
    <version>2.7.6</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.7.1</version>
    <scope>test</scope>
</dependency>
```

### 3.3 Configuration Steps

1. Clone the repository containing the demo application code.
2. Navigate to the project directory.
3. Ensure Maven is installed and setup properly.
4. If using an IDE, import the Maven project.
5. Update the `application.yml` file as per your configuration needs (if applicable).

### 3.4 Build Commands

Use the following command to build the application:

```bash
mvn clean install
```

## 4. Running Instructions

### 4.1 How to Build

To build the application, use:

```bash
mvn clean package
```

### 4.2 How to Run the Application

To run the application, you can either run it from your IDE or use the following Maven command:

```bash
mvn spring-boot:run
```

### 4.3 How to Run the Tests

To run the tests with Testcontainers, execute:

```bash
mvn test
```

### 4.4 Expected Output

The expected output for successful tests will be similar to:
```
-------------------------------------------------------
 T E S T S
-------------------------------------------------------
[INFO] Running com.example.service.MessageServiceTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 2.123 s - in com.example.service.MessageServiceTest
[INFO]
-------------------------------------------------------
```

## 5. Troubleshooting Tips

- **Docker Daemon Not Running**: Ensure Docker is running on your machine before executing tests.
- **Container Startup Issues**: If the Kafka container fails to start, check Docker logs for error messages.
- **Test Failures**: Verify the setup of your environment, especially the versions of dependencies in `pom.xml`.

Ensure that you have followed all the steps closely, and refer to this documentation when needed for setting up and testing the demo application effectively.