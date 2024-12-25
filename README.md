# Website Redesign and Optimization AI Team

This project implements an intelligent AI team for website redesign and optimization using [crewAI](https://crewai.com). The system employs multiple specialized AI agents working together to analyze, design, develop, and optimize websites.

## Features

- 🔍 **Automated Website Analysis**: Comprehensive analysis of existing websites for SEO, performance, and user experience
- 🎨 **Intelligent Design Proposals**: AI-driven design recommendations based on industry standards and brand guidelines
- 💻 **Automated Code Generation**: Creation of responsive, modern website code
- 🖼️ **Visual Asset Creation**: Generation and optimization of website visual elements
- 📝 **Content Optimization**: SEO-focused content refinement and optimization
- ✅ **Quality Assurance**: Automated testing and quality verification
- 📊 **Project Management**: Coordinated execution of the redesign process

## Prerequisites

- Python >=3.10 <=3.13
- OpenAI API Key
- Google Serper API Key (for web search capabilities)

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd crewai_team_development_for_website_redesign_and_optimization
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SERPER_API_KEY=your_serper_api_key
   ```

## Configuration

The project uses YAML files for configuration:

- `config/config.yaml`: Define website details and brand guidelines
- `config/agents.yaml`: Configure AI agent roles and capabilities
- `config/tasks.yaml`: Define tasks and their dependencies

### Customizing the Configuration

1. Update `config/config.yaml` with your website details:
   ```yaml
   current_website_url: "http://your-website.com"
   industry: "Your Industry"
   target_audience: "Your Target Audience"
   ```

2. Modify brand guidelines in `config/config.yaml`:
   ```yaml
   brand_guidelines:
     primary_colors:
       - "#your-color-1"
       - "#your-color-2"
     typography:
       headings: "Your Heading Font"
       body: "Your Body Font"
   ```

## Usage

1. Run the main script:
   ```bash
   python -m crewai_team_development_for_website_redesign_and_optimization.main
   ```

2. The system will:
   - Analyze the specified website
   - Generate design proposals
   - Create website code
   - Deploy to a local development server
   - Generate a comprehensive report

3. Access the results:
   - Redesigned website: `http://localhost:8000`
   - Project report: `output/report.md`
   - Website files: `output/redesigned_site/`

## Output Structure

```
output/
├── redesigned_site/        # Generated website files
│   ├── index.html         # Main HTML file
│   ├── css/              # Stylesheet directory
│   │   ├── styles.css
│   │   └── responsive.css
│   └── js/               # JavaScript directory
│       └── main.js
└── report.md             # Detailed project report
```

## Development

To contribute or modify the project:

1. Install in development mode:
   ```bash
   pip install -e .
   ```

2. Modify agent behaviors in `src/crewai_team_development_for_website_redesign_and_optimization/main.py`

3. Add new tools or capabilities in the tools directory

## Troubleshooting

- **Server Issues**: If the local server doesn't start, check port 8000 availability
- **API Errors**: Verify your API keys in the `.env` file
- **Module Errors**: Ensure you're using a compatible Python version and all dependencies are installed

## Support

For support and questions:
- Create an issue in the repository
- Visit [crewAI documentation](https://docs.crewai.com)
- Join the [crewAI Discord](https://discord.com/invite/X4JWnZnxPb)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
