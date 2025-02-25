# Sales Agent Crew - AI-Powered Sales Lead Generation - Backend

Sales Agent Crew is an intelligent lead generation platform designed to identify and generate personalized outreach for potential sales leads. By combining the power of AI with a modern web interface, it streamlines your sales prospecting process, saving time and maximizing efficiency.

## Features

- 🎯 **Targeted Lead Generation**: Generate leads based on your criteria.
- ✍️ **AI-Generated Email Templates**: Create personalized email templates with AI.
- 💼 **Company Research & Market Analysis**: Gain valuable insights for better decision-making.
- 🎨 **Modern UI**: Enjoy a responsive and user-friendly interface.
- ⚡ **Real-Time Analysis**: Generate and analyze leads instantly.

## Tech Stack

- **Backend**: FastAPI, CrewAI, Perplexity, OpenAI
- **AI/ML**: LangChain, SpaCy

## Prerequisites

Before starting, ensure you have the following installed:

- Python 3.8 or higher
- Perplexity API Key
- OpenAI API Key

## Installation

1. Clone the repository and navigate to the project directory:

With HTTPS:

```bash
git clone https://github.com/sambanova/samba-co-pilot.git
cd samba-co-pilot/backend
```

With SSH:

```bash
git clone git@github.com:sambanova/samba-co-pilot.git
cd samba-co-pilot/backend
```

2. Create a .env file and add your API keys:

```bash
TAVILY_API_KEY=your_tavily_api_key
LANGTRACE_API_KEY=your_langtrace_api_key
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Start Redis:

```bash
docker run --name test-redis -p 6379:6379 redis:7.0-alpine
```

## Running the Application

1. Start the FastAPI server:

```bash
uvicorn api.lead_generation_api:create_app --reload --env-file .env
```
