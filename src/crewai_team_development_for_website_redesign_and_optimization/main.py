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
import http.server
import socketserver
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global variables for server
PORT = 8000
server_thread = None
httpd = None

class Config(BaseModel):
    current_website_url: str
    industry: str
    target_audience: str
    brand_guidelines: Dict[str, Any]
    tools: Dict[str, List[str]]

def start_local_server(directory: str):
    """Start a local HTTP server in a separate thread."""
    global server_thread, httpd
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
    
    # Stop existing server if running
    stop_local_server()
    
    # Start new server
    httpd = socketserver.TCPServer(("", PORT), Handler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print(f"\nLocal server started at http://localhost:{PORT}")

def stop_local_server():
    """Stop the local HTTP server if it's running."""
    global server_thread, httpd
    if httpd:
        httpd.shutdown()
        httpd.server_close()
        server_thread = None
        httpd = None
        print("\nLocal server stopped")

def save_website_files(content: str) -> Path:
    """
    Parse the generated code and save each file in the redesigned_site folder.
    Returns the path to the redesigned_site folder.
    """
    output_dir = Path(__file__).parent / "output" / "redesigned_site"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nSaving website files to: {output_dir}")
    
    # Split the content into separate files based on file markers
    files = {}
    current_file = None
    current_content = []
    
    for line in content.split('\n'):
        # Check for file markers like "// filename: example.html" or "/* filename: style.css */"
        if '// filename:' in line or '/* filename:' in line:
            # Save previous file if exists
            if current_file:
                files[current_file] = '\n'.join(current_content)
                print(f"Prepared content for: {current_file}")
            # Extract new filename
            current_file = line.split('filename:')[1].strip().strip('*/ ')
            current_content = []
        else:
            if current_file:
                current_content.append(line)
    
    # Save the last file
    if current_file and current_content:
        files[current_file] = '\n'.join(current_content)
        print(f"Prepared content for: {current_file}")
    
    # If no file markers found, assume it's a single HTML file
    if not files:
        files['index.html'] = content
        print("No file markers found, saving as index.html")
    
    # Save all files
    for filename, content in files.items():
        file_path = output_dir / filename
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Successfully saved: {file_path}")
        except Exception as e:
            print(f"Error saving {filename}: {str(e)}")
    
    return output_dir

def analyze_website(tool_input: str) -> str:
    try:
        url = tool_input.strip()
        # Check if it's a local URL
        if "localhost" in url or "127.0.0.1" in url:
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

def generate_code(tool_input: str) -> str:
    try:
        # Parse the input to determine what needs to be generated
        if "test" in tool_input.lower():
            # Generate test code
            return """
            // filename: tests/test_website.js
            const puppeteer = require('puppeteer');

            describe('Website Tests', () => {
                let browser;
                let page;

                beforeAll(async () => {
                    browser = await puppeteer.launch();
                    page = await browser.newPage();
                });

                afterAll(async () => {
                    await browser.close();
                });

                test('Homepage loads correctly', async () => {
                    await page.goto('http://localhost:8000');
                    const title = await page.title();
                    expect(title).toBe('MPAS Boston');
                });

                test('Responsive design', async () => {
                    await page.setViewport({ width: 375, height: 667 }); // Mobile
                    // Add responsive design tests
                });
            });
            """
        else:
            # Generate website code
            return """
            // filename: index.html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>MPAS Boston</title>
                <meta name="description" content="Massachusetts Police Accreditation Solutions - Professional services for police departments">
                <link rel="stylesheet" href="css/styles.css">
                <link rel="stylesheet" href="css/responsive.css">
                <script defer src="js/main.js"></script>
            </head>
            <body>
                <header class="site-header">
                    <nav class="main-nav">
                        <div class="logo">
                            <img src="images/logo.svg" alt="MPAS Boston Logo">
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

            // filename: css/styles.css
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
            }

            // filename: css/responsive.css
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

            // filename: js/main.js
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
            """
    except Exception as e:
        return f"Error generating code: {str(e)}"

def generate_image(tool_input: str) -> str:
    return f"Generated image based on: {tool_input}"

def analyze_content(tool_input: str) -> str:
    return f"Content analysis results for: {tool_input}"

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
    
    agents = {
        "analysis_agent": Agent(
            role='Website Analyzer',
            goal='Analyze websites and provide detailed technical reports',
            backstory="""Expert in website analysis with deep knowledge of SEO, 
            performance optimization, and user experience.""",
            tools=[web_analyzer],
            verbose=True,
            allow_delegation=True
        ),
        "design_advisor_agent": Agent(
            role='Design Advisor',
            goal='Create modern and effective website designs',
            backstory="""Experienced UI/UX designer with expertise in modern web design 
            trends and user-centered design principles.""",
            tools=[design_research],
            verbose=True,
            allow_delegation=True
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
            allow_code_execution=True,
            max_retry_limit=3
        ),
        "asset_creator_agent": Agent(
            role='Visual Asset Creator',
            goal='Create and optimize visual assets for the website',
            backstory="""Creative designer specialized in web graphics and brand 
            consistency.""",
            tools=[image_generator],
            verbose=True,
            allow_delegation=True
        ),
        "content_refinement_agent": Agent(
            role='Content Optimizer',
            goal='Optimize website content for engagement and SEO',
            backstory="""Content strategist with expertise in SEO and engaging 
            writing.""",
            tools=[content_analyzer],
            verbose=True,
            allow_delegation=True
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
            allow_code_execution=True
        ),
        "project_manager_agent": Agent(
            role='Project Manager',
            goal='Coordinate the website redesign project efficiently',
            backstory="""Experienced digital project manager with a track record of 
            successful website launches""",
            tools=[],
            verbose=True,
            allow_delegation=True
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
        
        # Extract HTML content from frontend developer's output
        frontend_result = next((r for r in results if isinstance(r, str) and "<!DOCTYPE html>" in r), None)
        if frontend_result:
            website_dir = save_website_files(frontend_result)
            print(f"\nWebsite files saved to: {website_dir}")
            
            # Start local server
            start_local_server(str(website_dir))
            print("\nYou can now view the redesigned website at:")
            print(f"http://localhost:{PORT}")
        else:
            print("\nWarning: No website content found in the results")
        
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
