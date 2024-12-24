from crewai import Agent, Crew, Process, Task
from langchain_community.tools import Tool
from langchain_community.utilities import SerpAPIWrapper
from langchain_openai import ChatOpenAI
from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WebsiteRedesignCrew:
    """Website Redesign and Optimization crew"""

    def __init__(self, website_url=None):
        if website_url:
            website_url = website_url.replace("www.", "")
            if not website_url.startswith("http"):
                website_url = "https://" + website_url
        self.website_url = website_url or "https://example.com"
        self.agents = []
        self.tasks = []
        self._setup_agents()
        self._setup_tasks()

    def _setup_agents(self):
        # Create tools
        search = SerpAPIWrapper(serpapi_api_key=os.getenv('SERPER_API_KEY'))
        self.tools = [
            Tool(
                name="search",
                func=search.run,
                description="Search the internet for information about websites, design trends, and best practices."
            )
        ]

        # Create the LLM
        llm = ChatOpenAI(
            temperature=0.7,
            model="gpt-3.5-turbo",
            max_tokens=2000
        )

        self.agents = [
            Agent(
                role="Website Analyzer",
                goal="Analyze the current website and provide comprehensive insights for improvement",
                backstory="Expert in website analysis with 10+ years of experience in UX evaluation, performance optimization, and conversion rate optimization.",
                tools=self.tools,
                llm=llm,
                verbose=True
            ),
            Agent(
                role="Design Advisor",
                goal="Create modern, user-centric design solutions that enhance user experience and brand identity",
                backstory="Award-winning UI/UX designer with expertise in creating engaging web experiences.",
                tools=self.tools,
                llm=llm,
                verbose=True
            ),
            Agent(
                role="Frontend Developer",
                goal="Implement pixel-perfect, performant, and maintainable frontend code",
                backstory="Senior frontend developer with deep expertise in modern frameworks and best practices.",
                tools=self.tools,
                llm=llm,
                verbose=True,
                allow_code_execution=True
            )
        ]

    def _setup_tasks(self):
        self.tasks = [
            Task(
                description=f"""
                Analyze the website at {self.website_url}:
                1. Research and analyze the current website structure and content
                2. Evaluate user experience and performance metrics
                3. Identify technical issues and areas for improvement
                4. Create a detailed report with specific recommendations
                """,
                agent=self.agents[0]  # Website Analyzer
            ),
            Task(
                description=f"""
                1. Review the current website at {self.website_url}
                2. Research modern design trends and best practices
                3. Create wireframes for key pages and user flows
                4. Develop a modern, responsive design system
                """,
                agent=self.agents[1]  # Design Advisor
            ),
            Task(
                description=f"""
                1. Review the current website at {self.website_url}
                2. Research modern frontend technologies
                3. Implement approved designs
                4. Optimize performance and loading times
                """,
                agent=self.agents[2]  # Frontend Developer
            )
        ]

    def crew(self) -> Crew:
        """Create the website redesign crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
