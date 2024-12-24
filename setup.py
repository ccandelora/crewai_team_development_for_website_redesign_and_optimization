from setuptools import setup, find_packages

setup(
    name="crewai_team_development_for_website_redesign_and_optimization",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "crewai[tools]>=0.11.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "pydantic>=2.5.2",
        "PyYAML>=6.0.1",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "selenium>=4.15.2",
        "playwright>=1.40.0",
        "python-dotenv>=1.0.0",
        "openai>=1.12.0",
        "google-search-results>=2.4.2",
        "docker>=7.0.0"
    ],
) 