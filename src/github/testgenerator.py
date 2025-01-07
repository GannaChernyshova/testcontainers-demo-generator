import os
import git
from github import Github
import openai
import anthropic
import json
import re
from pathlib import Path
import glob


class AITestGenerator:
    def __init__(self, github_token, openai_key=None, anthropic_key=None, repo_url=None, debug=False):
        self.github_token = github_token
        self.debug = debug
        # Format repo URL with authentication token
        if repo_url.startswith('https://'):
            self.repo_url = repo_url.replace('https://', f'https://{github_token}@')
        else:
            self.repo_url = repo_url
        self.g = Github(github_token)
        self.local_path = "temp_repo"
        
        # Initialize AI clients based on provided keys
        self.ai_client = None
        if openai_key:
            openai.api_key = openai_key
            self.ai_client = "openai"
        elif anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
            self.ai_client = "anthropic"
        else:
            raise ValueError("Either OpenAI or Anthropic API key must be provided")

    def clone_repo(self):
        if os.path.exists(self.local_path):
            os.system(f"rm -rf {self.local_path}")
        self.repo = git.Repo.clone_from(self.repo_url, self.local_path)

    def create_branch(self, branch_name="feature/add-ai-testcontainers-eight"):
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
           - Spring Boot Testcontainers
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

        if self.ai_client == "openai":
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Return only Java code with proper package and imports"},
                    {"role": "user", "content": test_prompt}
                ],
                temperature=0
            )
            test_code = response.choices[0].message.content.strip()
        else:  # anthropic
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": "Return only Java code with proper package and imports.\n\n" + test_prompt
                    }
                ]
            )
            test_code = response.content[0].text.strip()

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
        
        Return only a Python list of service names that need Testcontainers.
        Example: ["postgresql", "redis", "mongodb"]
        Return empty list if no services found.
        The response must be a valid Python list syntax.
        """

        try:
            if self.ai_client == "openai":
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Return only a Python list of strings"},
                        {"role": "user", "content": f"{prompt}\n\nCode:\n{code}"}
                    ],
                    temperature=0
                )
                content = response.choices[0].message.content.strip()
            else:  # anthropic
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[
                        {
                            "role": "user",
                            "content": "Return only a Python list of strings.\n\n" + f"{prompt}\n\nCode:\n{code}"
                        }
                    ]
                )
                content = response.content[0].text.strip()

            if self.debug:
                print(f"Debug - Raw AI response for {file_path}:")
                print(content)
            
            # Clean up the response to ensure valid Python syntax
            content = content.replace('```python', '').replace('```', '').strip()
            if not (content.startswith('[') and content.endswith(']')):
                if self.debug:
                    print(f"Warning: Invalid list format received: {content}")
                return []
                
            try:
                deps = eval(content)
                if not isinstance(deps, list):
                    if self.debug:
                        print(f"Warning: Non-list result evaluated: {deps}")
                    return []
                return deps
            except SyntaxError as se:
                if self.debug:
                    print(f"Syntax error in AI response: {se}")
                    print(f"Problematic content: {content}")
                return []
            
        except Exception as e:
            if self.debug:
                print(f"Error detecting dependencies for {file_path}: {str(e)}")
                print(f"File content: {code[:200]}...")  # Print first 200 chars of file
            return []

    def update_dependencies(self, services):
        pom_path = Path(self.local_path) / "pom.xml"
        if not pom_path.exists():
            return

        # Read existing pom.xml
        pom_content = pom_path.read_text()
        
        # Check which dependencies we need to add
        needed_deps = set()
        if "postgresql" in services and "<artifactId>postgresql</artifactId>" not in pom_content:
            needed_deps.add("postgresql")
        if "mongodb" in services and "<artifactId>mongodb</artifactId>" not in pom_content:
            needed_deps.add("mongodb")
        if "redis" in services and "<artifactId>redis</artifactId>" not in pom_content:
            needed_deps.add("redis")
            
        # If no new dependencies needed, return early
        if not needed_deps:
            if self.debug:
                print("All required dependencies already present in pom.xml")
            return

        prompt = f"""
        Add ONLY the following Testcontainers dependencies that are missing: {list(needed_deps)}.
        Include ONLY dependencies that are not already in the pom.xml.
        Do not include any comments or explanations.
        Return only the XML dependency elements without any wrapper tags.
        Each dependency should include groupId, artifactId, version (if needed), and scope (if needed).
        
        Current pom.xml content for reference:
        {pom_content}
        """

        try:
            if self.ai_client == "openai":
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Return only XML dependency elements without comments or wrapper tags"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )
                new_deps = response.choices[0].message.content.strip()
            else:  # anthropic
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=[
                        {
                            "role": "user",
                            "content": "Return only XML dependency elements without comments or wrapper tags.\n\n" + prompt
                        }
                    ]
                )
                new_deps = response.content[0].text.strip()

            # Clean up the response
            new_deps = new_deps.replace('```xml', '').replace('```', '').strip()
            
            # Only proceed if we got valid dependency XML
            if "<dependency>" not in new_deps:
                print("No valid dependencies generated")
                return

            # Find the last </dependencies> tag
            last_deps_index = pom_content.rindex("</dependencies>")
            
            # Insert new dependencies before the closing tag
            updated_content = (
                pom_content[:last_deps_index] +
                "        " + new_deps + "\n    " +
                pom_content[last_deps_index:]
            )
            
            # Write updated content back to file
            pom_path.write_text(updated_content)
            print(f"Added new dependencies: {needed_deps}")
            
        except Exception as e:
            print(f"Error updating dependencies: {e}")
            print("Continuing without updating dependencies")

    def generate_tests(self):
        java_files = glob.glob(
            f"{self.local_path}/src/main/java/**/*.java", recursive=True)
        test_dir = f"{self.local_path}/src/test/java"
        os.makedirs(test_dir, exist_ok=True)

        print(f"Found {len(java_files)} Java files to process")
        
        for java_file in java_files:
            if "package-info.java" in java_file or "module-info.java" in java_file:
                continue

            if self.debug:
                print(f"\nProcessing file: {java_file}")
            try:
                test_content = self.analyze_code(java_file)
                if test_content:
                    if self.debug:
                        print(f"Generated test content for {java_file}")
                    dependencies = self.detect_dependencies(java_file)
                    if self.debug:
                        print(f"Detected dependencies: {dependencies}")
                    
                    relative_path = os.path.relpath(
                        java_file, f"{self.local_path}/src/main/java")
                    test_file = os.path.join(test_dir, relative_path.replace(
                        ".java", "IntegrationTest.java"))

                    os.makedirs(os.path.dirname(test_file), exist_ok=True)
                    with open(test_file, 'w') as f:
                        f.write(test_content)
                    print(f"Created test file: {test_file}")

                    if dependencies:
                        if self.debug:
                            print(f"Updating dependencies for: {dependencies}")
                        self.update_dependencies(dependencies)
                elif self.debug:
                    print(f"No test content generated for {java_file}")
            except Exception as e:
                if self.debug:
                    print(f"Error processing file {java_file}: {str(e)}")
                    print(f"Stack trace:", exc_info=True)
                else:
                    print(f"Error processing {os.path.basename(java_file)}")

    def commit_and_push(self):
        try:
            self.repo.index.add('*')
            self.repo.index.commit("Add AI-generated Testcontainers integration tests")
            current = self.repo.active_branch
            origin = self.repo.remote('origin')
            
            # Configure git to use credentials
            with self.repo.config_writer() as git_config:
                git_config.set_value('http', 'postBuffer', '524288000')
                
            # Push with token authentication
            origin.push(refspec=f'{current.name}:{current.name}', force=True)
        except Exception as e:
            print(f"Error committing and pushing: {e}")


def main():
    github_token = os.getenv("GITHUB_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    repo_url = os.getenv("REPO_URL")
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"

    if not github_token:
        raise ValueError("Missing required environment variable: GITHUB_TOKEN")
    
    if not repo_url:
        raise ValueError("Missing required environment variable: REPO_URL")
    
    if not (openai_key or anthropic_key):
        raise ValueError("Either OPENAI_API_KEY or ANTHROPIC_API_KEY must be provided")

    # Prioritize Anthropic if both keys are present
    if anthropic_key:
        generator = AITestGenerator(github_token, anthropic_key=anthropic_key, repo_url=repo_url, debug=debug_mode)
    else:
        generator = AITestGenerator(github_token, openai_key=openai_key, repo_url=repo_url, debug=debug_mode)

    generator.clone_repo()
    generator.create_branch()
    generator.generate_tests()
    generator.commit_and_push()


if __name__ == "__main__":
    main()
