from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class SummaryCrew():
    """Crew for creating service summaries"""
    agents: List[BaseAgent]
    tasks: List[Task]
    
    @agent
    def service_summarizer(self) -> Agent:
        return Agent(
            config=self.agents_config['service_summarizer'],
            verbose=True
        )
    
    @task
    def create_summary(self) -> Task:
        return Task(
            config=self.tasks_config['create_summary']
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the summary crew"""
        return Crew(
            agents=[self.service_summarizer()],
            tasks=[self.create_summary()],
            process=Process.sequential,
            verbose=True
        )
