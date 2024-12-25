from typing import List, Dict, Any
import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from bs4 import BeautifulSoup
import requests
import os
import threading
from dotenv import load_dotenv
import json
from flask import Flask, send_from_directory

# Load environment variables
load_dotenv()

class Config(BaseModel):
    current_website_url: str
    industry: str
    target_audience: str
    brand_guidelines: Dict[str, Any]
    tools: Dict[str, List[str]]

# Global variables for server
PORT = 8000
server_thread = None
flask_app = Flask(__name__)
website_directory = None

@flask_app.route('/')
def serve_index():
    return send_from_directory(website_directory, 'index.html')

@flask_app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(website_directory, path)

def start_local_server(directory: str):
    """Start a Flask server in a separate thread."""
    global server_thread, website_directory
    
    # Stop existing server if running
    stop_local_server()
    
    # Set the website directory
    website_directory = directory
    
    def run_flask():
        flask_app.run(host='localhost', port=PORT, debug=False, use_reloader=False)
    
    # Start new server
    server_thread = threading.Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()
    print(f"\nFlask server started at http://localhost:{PORT}")

def stop_local_server():
    """Stop the Flask server if it's running."""
    global server_thread
    if server_thread:
        # Flask will be stopped when the thread is terminated
        server_thread = None
        print("\nFlask server stopped")

def generate_website_code(tool_input: str) -> str:
    """Generate the actual website code."""
    if "test" in tool_input.lower():
        return """
        // filename: tests/test_website.py
        import pytest
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        
        @pytest.fixture
        def browser():
            driver = webdriver.Firefox()
            yield driver
            driver.quit()
        
        def test_homepage(browser):
            browser.get('http://localhost:8000')
            assert 'MPAS Boston' in browser.title
            
            # Test responsive design
            browser.set_window_size(375, 667)  # Mobile size
            nav = browser.find_element(By.CLASS_NAME, 'nav-links')
            assert nav is not None
        """
    else:
        return """
        // filename: app.py
        from flask import Flask, render_template, send_from_directory
        import os
        
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return render_template('index.html')
        
        if __name__ == '__main__':
            app.run(host='localhost', port=8000)
        
        // filename: templates/index.html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MPAS Boston</title>
            <meta name="description" content="Massachusetts Police Accreditation Solutions - Professional services for police departments">
            <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
            <link rel="stylesheet" href="{{ url_for('static', filename='css/responsive.css') }}">
            <script defer src="{{ url_for('static', filename='js/main.js') }}"></script>
        </head>
        <body>
            <header class="site-header">
                <nav class="main-nav">
                    <div class="logo">
                        <img src="{{ url_for('static', filename='images/logo.svg') }}" alt="MPAS Boston Logo">
                    </div>
                    <ul class="nav-links">
                        <li><a href="#services">Services</a></li>
                        <li><a href="#about">About</a></li>
                        <li><a href="#contact">Contact</a></li>
                    </ul>
                </nav>
            </header>
            
            <main>
                <section id="hero" class="hero-section">
                    <h1>Massachusetts Police Accreditation Solutions</h1>
                    <p>Professional services for police departments</p>
                    <a href="#contact" class="cta-button">Get Started</a>
                </section>
            </main>

            <footer class="site-footer">
                <p>&copy; 2024 MPAS Boston. All rights reserved.</p>
            </footer>
        </body>
        </html>

        // filename: static/css/styles.css
        :root {
            --primary-color: #2C3E50;
            --secondary-color: #3498DB;
            --accent-color: #E74C3C;
            --text-color: #333;
            --background-color: #FFF;
        }

        body {
            font-family: 'Open Sans', sans-serif;
            color: var(--text-color);
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }

        .site-header {
            background: var(--background-color);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
        }

        .main-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        .nav-links {
            display: flex;
            gap: 2rem;
            list-style: none;
            margin: 0;
            padding: 0;
        }

        .nav-links a {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }

        .nav-links a:hover {
            color: var(--secondary-color);
        }

        .hero-section {
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 2rem;
            background: linear-gradient(rgba(44, 62, 80, 0.9), rgba(44, 62, 80, 0.9)),
                        url('../images/hero-bg.jpg') center/cover;
            color: var(--background-color);
            margin-top: 60px;
        }

        // filename: static/css/responsive.css
        @media (max-width: 768px) {
            .main-nav {
                flex-direction: column;
                padding: 1rem;
            }

            .nav-links {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
                width: 100%;
            }

            .hero-section {
                height: auto;
                min-height: 100vh;
                padding: 4rem 1rem;
            }
        }

        // filename: static/js/main.js
        document.addEventListener('DOMContentLoaded', function() {
            // Smooth scrolling for navigation links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });

            // Mobile navigation toggle
            const nav = document.querySelector('.nav-links');
            const toggleButton = document.createElement('button');
            toggleButton.classList.add('nav-toggle');
            toggleButton.innerHTML = '☰';
            toggleButton.addEventListener('click', () => {
                nav.classList.toggle('active');
            });
            document.querySelector('.main-nav').prepend(toggleButton);
        });
        
        // filename: requirements.txt
        flask==3.0.0
        pytest==8.0.0
        selenium==4.16.0
        """

def generate_image(tool_input: str) -> str:
    return f"Generated image based on: {tool_input}"

def analyze_content(tool_input: str) -> str:
    return f"Content analysis results for: {tool_input}"

def deploy_files(tool_input: str) -> str:
    """Deploy files to the local environment with Flask structure."""
    try:
        print(f"\nReceived deployment input:\n{tool_input}")
        
        # Parse the input as JSON
        data = json.loads(tool_input)
        
        # Handle error case from code generator
        if isinstance(data, dict):
            if "error" in data:
                return f"Cannot deploy: Code generator reported error: {data['error']}"
            elif "type" in data and data["type"] == "code_generation":
                files_data = data["files"]
            else:
                files_data = data
        else:
            files_data = data
        
        if not isinstance(files_data, list):
            return "Invalid input format: Expected a JSON array of files"
        
        output_dir = Path(__file__).parent / "output" / "redesigned_site"
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nDeploying files to: {output_dir}")
        
        # Create Flask directory structure
        (output_dir / "static").mkdir(exist_ok=True)
        (output_dir / "templates").mkdir(exist_ok=True)
        
        deployed_files = []
        for file_info in files_data:
            if not isinstance(file_info, dict) or "path" not in file_info or "content" not in file_info:
                print(f"Skipping invalid file info: {file_info}")
                continue
            
            # Determine the correct path based on file type
            file_path = output_dir
            if file_info['path'].startswith('static/'):
                file_path = output_dir / file_info['path']
            elif file_info['path'].startswith('templates/'):
                file_path = output_dir / file_info['path']
            elif file_info['path'] == 'app.py':
                file_path = output_dir / file_info['path']
            elif file_info['path'].endswith('.html'):
                file_path = output_dir / 'templates' / file_info['path']
            elif file_info['path'].endswith(('.css', '.js', '.svg', '.jpg', '.png')):
                file_path = output_dir / 'static' / file_info['path']
            else:
                file_path = output_dir / file_info['path']
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                with open(file_path, 'w') as f:
                    f.write(file_info['content'].strip())
                deployed_files.append(str(file_path))
                print(f"Successfully deployed: {file_path}")
            except Exception as e:
                print(f"Error deploying {file_path}: {str(e)}")
        
        if not deployed_files:
            return "No files were deployed. Check the input format."
        
        # Create requirements.txt if it doesn't exist
        requirements_path = output_dir / "requirements.txt"
        if not requirements_path.exists():
            with open(requirements_path, 'w') as f:
                f.write("flask==3.0.0\npytest==8.0.0\nselenium==4.16.0\n")
            deployed_files.append(str(requirements_path))
            print(f"Created requirements.txt")
        
        return f"Successfully deployed {len(deployed_files)} files:\n" + "\n".join(deployed_files)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON input: {str(e)}"
        print(f"\nJSON decode error: {error_msg}")
        print(f"Received input: {tool_input}")
        return error_msg
    except Exception as e:
        error_msg = f"Error deploying files: {str(e)}"
        print(f"\nDeployment error: {error_msg}")
        return error_msg

def create_agents(config: Config) -> Dict[str, Agent]:
    # Create tools
    web_analyzer = Tool(
        name="WebAnalyzer",
        func=analyze_website,
        description="Analyzes websites for layout, content structure, SEO, and performance."
    )
    
    design_research = Tool(
        name="DesignResearch",
        func=research_design,
        description="Researches modern design trends and best practices for specific industries."
    )
    
    code_generator = Tool(
        name="CodeGenerator",
        func=generate_code,
        description="Generates HTML, CSS, and JavaScript code based on design specifications."
    )
    
    deployment_tool = Tool(
        name="Deployment",
        func=deploy_files,
        description="Deploys files to the local environment, creating necessary directories and handling file operations."
    )
    
    image_generator = Tool(
        name="ImageGenerator",
        func=generate_image,
        description="Generates images based on descriptions."
    )
    
    content_analyzer = Tool(
        name="ContentAnalyzer",
        func=analyze_content,
        description="Analyzes and optimizes content for SEO and engagement."
    )
    
    # Default configuration for GPT-3.5-turbo
    default_llm_config = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    }
    
    # Only use GPT-4 for agents that really need it
    gpt4_llm_config = {
        "model": "gpt-4",
        "temperature": 0.7
    }
    
    agents = {
        "analysis_agent": Agent(
            role='Website Analyzer',
            goal='Analyze websites and provide detailed technical reports',
            backstory="""Expert in website analysis with deep knowledge of SEO, 
            performance optimization, and user experience.""",
            tools=[web_analyzer],
            verbose=True,
            allow_delegation=True,
            llm_config=default_llm_config
        ),
        "design_advisor_agent": Agent(
            role='Design Advisor',
            goal='Create modern and effective website designs',
            backstory="""Experienced UI/UX designer with expertise in modern web design 
            trends and user-centered design principles.""",
            tools=[design_research],
            verbose=True,
            allow_delegation=True,
            llm_config=gpt4_llm_config  # Design needs GPT-4's capabilities
        ),
        "code_generator_agent": Agent(
            role='Frontend Developer',
            goal='Develop high-quality, responsive frontend code',
            backstory="""Senior frontend developer with expertise in modern web 
            technologies and best practices. You write clean, maintainable code and ensure 
            cross-browser compatibility. You're skilled at implementing responsive designs 
            and optimizing website performance.""",
            tools=[code_generator],
            verbose=True,
            allow_delegation=True,
            llm_config=gpt4_llm_config  # Code generation needs GPT-4's capabilities
        ),
        "deployment_agent": Agent(
            role='Deployment Specialist',
            goal='Deploy and set up the website in the local environment',
            backstory="""DevOps engineer specialized in website deployment and environment setup. 
            You ensure all files are properly organized, permissions are set correctly, and the 
            local development environment is configured optimally.""",
            tools=[deployment_tool],
            verbose=True,
            allow_delegation=True,
            llm_config=default_llm_config
        ),
        "asset_creator_agent": Agent(
            role='Visual Asset Creator',
            goal='Create and optimize visual assets for the website',
            backstory="""Creative designer specialized in web graphics and brand 
            consistency.""",
            tools=[image_generator],
            verbose=True,
            allow_delegation=True,
            llm_config=default_llm_config
        ),
        "content_refinement_agent": Agent(
            role='Content Optimizer',
            goal='Optimize website content for engagement and SEO',
            backstory="""Content strategist with expertise in SEO and engaging 
            writing.""",
            tools=[content_analyzer],
            verbose=True,
            allow_delegation=True,
            llm_config=default_llm_config
        ),
        "quality_assurance_agent": Agent(
            role='QA Specialist',
            goal='Ensure website quality and performance across all platforms',
            backstory="""Detail-oriented QA engineer with extensive testing 
            experience. You're skilled at writing and executing test cases to verify 
            website functionality and performance.""",
            tools=[web_analyzer],
            verbose=True,
            allow_delegation=True,
            llm_config=default_llm_config
        ),
        "project_manager_agent": Agent(
            role='Project Manager',
            goal='Coordinate the website redesign project efficiently',
            backstory="""Experienced digital project manager with a track record of 
            successful website launches""",
            tools=[],
            verbose=True,
            allow_delegation=True,
            llm_config=default_llm_config
        )
    }
    return agents

def load_config() -> Config:
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
    return Config(**config_data)

def load_tasks() -> Dict[str, Dict[str, Any]]:
    tasks_path = Path(__file__).parent / "config" / "tasks.yaml"
    with open(tasks_path, "r") as f:
        return yaml.safe_load(f)

def create_tasks(config: Config, task_configs: Dict[str, Dict[str, Any]], agents: Dict[str, Agent]) -> List[Task]:
    # First create all tasks without context
    tasks_dict = {}
    for task_id, task_config in task_configs.items():
        # Replace template variables in description
        description = task_config["description"].format(
            current_website_url=config.current_website_url,
            industry=config.industry,
            target_audience=config.target_audience,
            brand_guidelines=config.brand_guidelines
        )
        
        task = Task(
            description=description,
            agent=agents[task_config["agent"]],
            expected_output=task_config["expected_output"],
            async_execution=task_config.get("async_execution", False)
        )
        tasks_dict[task_id] = task
    
    # Now add context/dependencies
    for task_id, task_config in task_configs.items():
        if "context" in task_config:
            context_tasks = [tasks_dict[context_id] for context_id in task_config["context"]]
            tasks_dict[task_id].context = context_tasks
    
    return list(tasks_dict.values())

def save_report(report_content: str):
    output_path = Path(__file__).parent / "output" / "report.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report_content)
    return output_path

def format_report(results: List[Any]) -> str:
    report = "# Website Redesign Project Report\n\n"
    
    # Website Analysis
    report += "## Website Analysis\n"
    analysis_result = next((r for r in results if isinstance(r, str) and "Website Analysis" in r), None)
    if analysis_result:
        report += analysis_result + "\n\n"
    
    # Design Proposal
    report += "## Design Proposal\n"
    design_result = next((r for r in results if isinstance(r, str) and "Design Proposal" in r), None)
    if design_result:
        report += design_result + "\n\n"
    
    # Visual Assets
    report += "## Visual Assets\n"
    assets_result = next((r for r in results if isinstance(r, str) and "logo design" in r.lower()), None)
    if assets_result:
        report += assets_result + "\n\n"
    
    # Content Optimization
    report += "## Content Optimization\n"
    content_result = next((r for r in results if isinstance(r, str) and "content" in r.lower()), None)
    if content_result:
        report += content_result + "\n\n"
    
    # QA Report
    report += "## Quality Assurance Report\n"
    qa_result = next((r for r in results if isinstance(r, str) and "QA" in r), None)
    if qa_result:
        report += qa_result + "\n\n"
    
    # Project Timeline
    report += "## Project Timeline\n"
    timeline_result = next((r for r in results if isinstance(r, str) and "Project Timeline" in r), None)
    if timeline_result:
        report += timeline_result + "\n\n"
    
    return report

def analyze_website(tool_input: str) -> str:
    try:
        url = tool_input.strip()
        # Check if it's a local URL
        if "localhost" in url:
            if not server_thread:
                return "Error: Local server is not running. Please start the server first."
        
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Basic analysis
        title = soup.title.string if soup.title else "No title found"
        meta_desc = soup.find('meta', {'name': 'description'})
        meta_desc = meta_desc['content'] if meta_desc else "No meta description found"
        
        # Structure analysis
        headings = len(soup.find_all(['h1', 'h2', 'h3']))
        images = len(soup.find_all('img'))
        links = len(soup.find_all('a'))
        
        analysis = f"""
        Website Analysis for {url}:
        Title: {title}
        Meta Description: {meta_desc}
        Structure:
        - {headings} headings found
        - {images} images found
        - {links} links found
        Performance: Response time was {response.elapsed.total_seconds():.2f} seconds
        """
        return analysis
    except Exception as e:
        return f"Error analyzing website: {str(e)}"

def research_design(tool_input: str) -> str:
    return f"Design research results for: {tool_input}"

def parse_code_output(code_content: str) -> List[Dict[str, str]]:
    """Parse code output with file markers into a list of file objects."""
    files = []
    current_file = None
    current_content = []
    
    for line in code_content.split('\n'):
        # Check for file markers
        if '// filename:' in line or '/* filename:' in line:
            # Save previous file if exists
            if current_file:
                files.append({
                    'path': current_file,
                    'content': '\n'.join(current_content)
                })
            # Extract new filename
            current_file = line.split('filename:')[1].strip().strip('*/ ')
            current_content = []
        else:
            if current_file:
                current_content.append(line)
    
    # Save the last file
    if current_file and current_content:
        files.append({
            'path': current_file,
            'content': '\n'.join(current_content)
        })
    
    # If no file markers found, assume it's a single HTML file
    if not files:
        files.append({
            'path': 'index.html',
            'content': code_content
        })
    
    return files

def generate_code(tool_input: str) -> str:
    """Generate website code and return it as a JSON array of files."""
    try:
        # Generate the code as before
        code_content = generate_website_code(tool_input)
        
        # Parse the code into file objects
        files = parse_code_output(code_content)
        
        # Convert to JSON for the deployment agent
        json_output = json.dumps(files, indent=2)
        print(f"\nGenerated JSON output for deployment:\n{json_output}")
        
        # Return a properly formatted task result that includes both the JSON and a description
        result = {
            "type": "code_generation",
            "files": files,
            "message": f"Generated {len(files)} files for deployment"
        }
        return json.dumps(result)
    except Exception as e:
        error_msg = f"Error generating code: {str(e)}"
        print(f"\nError in generate_code: {error_msg}")
        return json.dumps({"error": error_msg})

def main():
    print("\nStarting Website Redesign Project...")
    
    # Load configuration
    print("Loading configuration...")
    config = load_config()
    task_configs = load_tasks()
    
    # Create agents and tasks
    print("\nCreating agents and tasks...")
    agents = create_agents(config)
    tasks = create_tasks(config, task_configs, agents)
    
    print(f"\nTotal tasks to be executed: {len(tasks)}")
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task.description[:100]}...")
    
    # Create and run the crew
    print("\nInitializing crew and starting tasks...")
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )
    
    try:
        results = crew.kickoff()
        print("\nAll tasks completed. Processing results...")
        
        # The deployment agent will handle file creation, so we just need to start the server
        website_dir = Path(__file__).parent / "output" / "redesigned_site"
        if website_dir.exists():
            # Start local server
            start_local_server(str(website_dir))
            print("\nYou can now view the redesigned website at:")
            print(f"http://localhost:{PORT}")
        else:
            print("\nWarning: Website directory not found. Check the deployment agent's logs for details.")
        
        # Generate and save the report
        report_content = format_report(results)
        report_path = save_report(report_content)
        print(f"Report saved to: {report_path}")
        
        print("\nProject completed successfully!")
        
        # Keep the server running until user interrupts
        try:
            while True:
                input("\nPress Ctrl+C to stop the server and exit...")
        except KeyboardInterrupt:
            print("\nStopping server...")
            stop_local_server()
        
        return results
        
    except Exception as e:
        print(f"\nError during execution: {str(e)}")
        print("Please check the logs above for more details about which task failed.")
        stop_local_server()
        raise

if __name__ == "__main__":
    main()
