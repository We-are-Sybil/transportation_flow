from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from transportation_flow.schemas.transportation_models import (
    PartialRequest, ValidationResult
)
from crewai.agents.agent_builder.base_agent import BaseAgent
import json

@CrewBase
class RequestCrew():
    """Crew for processing transportation requests"""
    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def request_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['request_analyzer'],
            verbose=True
        )

    @agent 
    def information_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['information_validator'],
            verbose=True
        )

    @task
    def analyze_request(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_request']
        )

    @task
    def validate_information(self) -> Task:
        return Task(
            config=self.tasks_config['validate_information']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Request processing crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
