from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Task, Crew, Process
from crewai_tools import CodeDocsSearchTool
import os


@CrewBase
class TestcontainersDemoGenerator():
    """TestcontainersDemoGenerator crew for creating demo projects"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    default_model = {
        "model": os.getenv("MODEL_NAME", "gpt-4"),
        "provider": os.getenv("MODEL_PROVIDER", "openai")
    }

    # Define documentation tools for each language
    DOCS_TOOLS = {
        'java': CodeDocsSearchTool(docs_url='https://java.testcontainers.org'),
        'csharp': CodeDocsSearchTool(docs_url='https://dotnet.testcontainers.org/'),
        'go': CodeDocsSearchTool(docs_url='https://golang.testcontainers.org/'),
        'python': CodeDocsSearchTool(docs_url='https://testcontainers-python.readthedocs.io/en/latest/#'),
        'node': CodeDocsSearchTool(docs_url='https://node.testcontainers.org/')
    }

    def __init__(self, language='Java', services='PostgreSQL'):
        super().__init__()
        self.language = language.lower()
        self.services = services
        self.docs_tool = self.DOCS_TOOLS.get(
            self.language, self.DOCS_TOOLS['java'])
        self.demo_app_output = None
        self.research_output = None

    def save_output(self, content: str, filename: str):
        """Save output to a file"""
        with open(filename, 'w') as f:
            f.write(
                f"# {self.language.upper()} Demo Application with {self.services}\n\n")
            f.write(content)

    def format_task_config(self, task_name: str) -> dict:
        """Format task configuration with proper variables"""
        config = dict(self.tasks_config[task_name])
        config['description'] = config['description'] % {
            'language': self.language,
            'services': self.services
        }
        config['expected_output'] = config['expected_output'] % {
            'language': self.language,
            'services': self.services
        } if '%(' in config['expected_output'] else config['expected_output']
        return config

    @agent
    def demo_developer(self) -> Agent:
        config = dict(self.agents_config['demo_developer'])
        config['role'] = config['role'] % {'language': self.language}
        config['backstory'] = config['backstory'] % {'language': self.language}

        return Agent(
            config=config,
            verbose=True,
            model=self.default_model["model"],
            provider=self.default_model["provider"],
            tools=[self.docs_tool]
        )

    @agent
    def test_engineer(self) -> Agent:
        config = dict(self.agents_config['test_engineer'])
        config['role'] = config['role'] % {'language': self.language}
        config['backstory'] = config['backstory'] % {'language': self.language}

        return Agent(
            config=config,
            verbose=True,
            model=self.default_model["model"],
            provider=self.default_model["provider"],
            tools=[self.docs_tool]
        )

    @agent
    def documentation_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['documentation_specialist'],
            verbose=True,
            model=self.default_model["model"],
            provider=self.default_model["provider"],
            tools=[self.docs_tool]
        )

    @task
    def create_demo_app(self) -> Task:
        config = self.format_task_config('create_demo_app')
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.demo_developer(),
            context=[],
            output_file="demo_app.md"
        )

    @task
    def research_testcontainers(self) -> Task:
        config = self.format_task_config('research_testcontainers')
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.test_engineer(),
            context=[
                f"Demo App Implementation:\n{self.demo_app_output}"] if self.demo_app_output else [],
            output_file="testcontainers_research.md"
        )

    @task
    def implement_tests(self) -> Task:
        config = self.format_task_config('implement_tests')
        context = []
        if self.demo_app_output:
            context.append(f"Demo App Implementation:\n{self.demo_app_output}")
        if self.research_output:
            context.append(f"Testcontainers Research:\n{self.research_output}")

        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.test_engineer(),
            context=context,
            output_file="test_demo_app.md"
        )

    @task
    def create_documentation(self) -> Task:
        config = self.format_task_config('create_documentation')
        context = []
        if self.demo_app_output:
            context.append(f"Demo App Implementation:\n{self.demo_app_output}")
        if self.research_output:
            context.append(f"Test Implementation:\n{self.research_output}")

        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.documentation_specialist(),
            context=context,
            output_file="documentation.md"
        )

    @crew
    def crew(self) -> Crew:
        """Creates the TestcontainersDemoGenerator crew"""
        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

        # Execute crew and handle task outputs
        result = crew.kickoff()

        # Store intermediate results and save outputs
        for task in self.tasks:
            if hasattr(task, 'output_file'):
                if task.output_file == "demo_app.md":
                    self.demo_app_output = task.output
                elif task.output_file == "testcontainers_research.md":
                    self.research_output = task.output
                self.save_output(task.output, task.output_file)

        return result
