from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Task, Crew, Process
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

    def __init__(self, language='Java', services='PostgreSQL'):
        super().__init__()
        self.language = language
        self.services = services

    @agent
    def documentation_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['documentation_researcher'],
            verbose=True,
            model=self.default_model["model"],
            provider=self.default_model["provider"]
        )

    @agent
    def solution_architect(self) -> Agent:
        return Agent(
            config=self.agents_config['solution_architect'],
            verbose=True,
            model=self.default_model["model"],
            provider=self.default_model["provider"]
        )

    @agent
    def implementation_engineer(self) -> Agent:
        config = dict(self.agents_config['implementation_engineer'])
        config['role'] = config['role'] % {'language': self.language}
        config['backstory'] = config['backstory'] % {'language': self.language}

        return Agent(
            config=config,
            verbose=True,
            model=self.default_model["model"],
            provider=self.default_model["provider"]
        )

    @task
    def analyze_requirements(self) -> Task:
        task_config = dict(self.tasks_config['analyze_requirements'])
        task_config['description'] = task_config['description'] % {
            'language': self.language,
            'services': self.services
        }

        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.documentation_researcher()
        )

    @task
    def design_solution(self) -> Task:
        task_config = dict(self.tasks_config['design_solution'])
        task_config['description'] = task_config['description'] % {
            'language': self.language,
            'services': self.services
        }

        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.solution_architect()
        )

    @task
    def generate_implementation(self) -> Task:
        task_config = dict(self.tasks_config['generate_implementation'])

        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.implementation_engineer()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the TestcontainersDemoGenerator crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
