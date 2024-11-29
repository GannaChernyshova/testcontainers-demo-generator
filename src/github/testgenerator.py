import os
import git
from github import Github
import openai
import json
import re
from pathlib import Path
import glob


class AITestGenerator:
    def __init__(self, github_token, openai_key, repo_url):
        self.github_token = github_token
        self.repo_url = repo_url
        self.g = Github(github_token)
        self.local_path = "temp_repo"
        openai.api_key = openai_key

    def clone_repo(self):
        if os.path.exists(self.local_path):
            os.system(f"rm -rf {self.local_path}")
        self.repo = git.Repo.clone_from(self.repo_url, self.local_path)

    def create_branch(self, branch_name="feature/add-ai-testcontainers-seven"):
        current = self.repo.create_head(branch_name)
        current.checkout()

    def analyze_code(self, file_path):
        if any(x in file_path for x in ["config", "entity", "/model/"]):
            return ""

        with open(file_path, 'r') as f:
            code = f.read()

        if "@Entity" in code or "@Configuration" in code:
            return ""

        package_match = re.search(r'package\s+(.*?);', code)
        package_name = package_match.group(1) if package_match else None

        if not package_name:
            return ""

        test_prompt = f"""
        Generate TestContainers integration test.
        Original code: {code}
        Test package name must be: {package_name}
        
        Requirements:
        1. Use exactly the same package as original class
        2. Include all required imports for:
           - JUnit Jupiter annotations (@Test, @BeforeEach, etc)
           - Testcontainers annotations and classes
           - Spring Boot Test annotations
           - Spring Boot TestContainers
           - Your actual domain classes from src/main
           - AssertJ for assertions
        3. For DB tests:
           - Use static PostgreSQLContainer with TC_REUSABLE
           - Add @DynamicPropertySource for container properties
           - Initialize test data properly in @BeforeEach
           - Dynamic properties:
             @DynamicPropertySource
             static void postgresProperties(DynamicPropertyRegistry registry) {{
                 registry.add("spring.datasource.url", postgres::getJdbcUrl);
                 registry.add("spring.datasource.username", postgres::getUsername);
                 registry.add("spring.datasource.password", postgres::getPassword);
             }}
        4. For controllers:
           - Use @SpringBootTest(webEnvironment = RANDOM_PORT)
           - Use TestRestTemplate instead of MockMvc
        5. Use @Autowired for Spring components
        6. No empty methods
        7. Initialize all required entities before tests
        8. Test only using classes that exist in src/main
        9. No mock objects or mock frameworks
        10. Clean test data in @AfterEach if needed
        
        Return only Java test class code.
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                    "content": "Return only Java code with proper package and imports"},
                {"role": "user", "content": test_prompt}
            ],
            temperature=0
        )

        test_code = response.choices[0].message.content.strip()
        return test_code.replace("```java", "").replace("```", "").strip()

    def detect_dependencies(self, file_path):
        with open(file_path, 'r') as f:
            code = f.read()

        prompt = """
        Analyze this Java code and pom.xml for external service dependencies.
        Look for:
        - @Entity annotations and JPA repositories
        - Database connection properties
        - Service connection strings
        - Message queue connections
        - Cache configurations
        - External API clients
        
        Return only a Python list of service names that need TestContainers.
        Example: ["postgresql", "redis", "mongodb"]
        Return empty list if no services found.
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Return only a Python list of strings"},
                    {"role": "user", "content": f"{prompt}\n\nCode:\n{code}"}
                ],
                temperature=0
            )

            content = response.choices[0].message.content.strip()
            deps = eval(content)
            return deps if isinstance(deps, list) else []
        except Exception as e:
            print(f"Error detecting dependencies: {e}")
            return []

    def update_dependencies(self, services):
        pom_path = Path(self.local_path) / "pom.xml"
        if not pom_path.exists():
            return

        prompt = f"""
        Add these TestContainers dependencies to pom.xml for services {services}.
        Also include:
        1. JUnit Jupiter dependency
        2. Testcontainers JUnit Jupiter dependency
        3. Testcontainers BOM
        4. Spring Boot Test dependency
        
        Current pom.xml content:
        {pom_path.read_text()}
        
        Return only the new dependencies XML section.
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        deps = response.choices[0].message.content
        pom_content = pom_path.read_text()
        if "<dependencies>" not in pom_content:
            pom_content = pom_content.replace(
                "</project>", "<dependencies>\n</dependencies>\n</project>")
        updated_content = pom_content.replace(
            "</dependencies>",
            f"{deps}\n    </dependencies>"
        )
        pom_path.write_text(updated_content)

    def generate_tests(self):
        java_files = glob.glob(
            f"{self.local_path}/src/main/java/**/*.java", recursive=True)
        test_dir = f"{self.local_path}/src/test/java"
        os.makedirs(test_dir, exist_ok=True)

        for java_file in java_files:
            if "package-info.java" in java_file or "module-info.java" in java_file:
                continue

            try:
                test_content = self.analyze_code(java_file)
                if test_content:
                    dependencies = self.detect_dependencies(java_file)
                    relative_path = os.path.relpath(
                        java_file, f"{self.local_path}/src/main/java")
                    test_file = os.path.join(test_dir, relative_path.replace(
                        ".java", "IntegrationTest.java"))

                    os.makedirs(os.path.dirname(test_file), exist_ok=True)
                    with open(test_file, 'w') as f:
                        f.write(test_content)

                    if dependencies:
                        self.update_dependencies(dependencies)
            except Exception as e:
                print(f"Error processing file {java_file}: {str(e)}")

    def commit_and_push(self):
        self.repo.index.add('*')
        self.repo.index.commit(
            "Add AI-generated Testcontainers integration tests")
        current = self.repo.active_branch
        origin = self.repo.remote('origin')
        origin.push(
            refspec=f'{current.name}:{current.name}', set_upstream=True)


def main():
    github_token = os.getenv("GITHUB_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    repo_url = "https://github.com/GannaChernyshova/test-gen-demo"

    if not all([github_token, openai_key, repo_url]):
        raise ValueError(
            "Missing required environment variables: GITHUB_TOKEN, OPENAI_API_KEY, REPO_URL")

    generator = AITestGenerator(github_token, openai_key, repo_url)
    generator.clone_repo()
    generator.create_branch()
    generator.generate_tests()
    generator.commit_and_push()


if __name__ == "__main__":
    main()
