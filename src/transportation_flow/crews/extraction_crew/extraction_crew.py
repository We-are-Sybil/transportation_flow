from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import Optional, Dict, Any, List

@CrewBase
class ExtractionCrew():
    """Crew for extracting and collecting transportation information"""
    agents: List[BaseAgent]
    tasks: List[Task]
    
    @agent
    def information_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['information_extractor'],
            verbose=True
        )
    
    @agent
    def conversation_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['conversation_manager'],
            verbose=True
        )
    
    @task
    def extract_information(self) -> Task:
        return Task(
            config=self.tasks_config['extract_information']
        )
    
    @task
    def request_missing_information(self) -> Task:
        return Task(
            config=self.tasks_config['request_missing_information']
        )
    
    @crew
    def extraction_crew(self) -> Crew:
        """Crew for information extraction only"""
        return Crew(
            agents=[self.information_extractor()],
            tasks=[self.extract_information()],
            process=Process.sequential,
            verbose=True
        )
    
    @crew
    def conversation_crew(self) -> Crew:
        """Crew for conversational information gathering"""
        return Crew(
            agents=[self.conversation_manager()],
            tasks=[self.request_missing_information()],
            process=Process.sequential,
            verbose=True
        )
