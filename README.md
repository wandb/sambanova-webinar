![Samba Agents Logo](https://sambanova.ai/hubfs/sambanova-logo-black.png)

<p align="center">
  <img src="./assets/wandb_logo-dark.svg#gh-dark-mode-only" width="600" alt="Weights & Biases" />
  <img src="./assets/wandb_logo-light.svg#gh-light-mode-only" width="600" alt="Weights & Biases" />
</p>

<h1 style="font-size: 3em;">Agents</h1>

This repo is used for Weight and Biases and SambaNova Webniar. You can find the related blog here: LINK TBD 

This Agent application routes requests to four different agents: General assistant agent, Sales leads agent, Deep research agent, and a Finance analysis agent. The agents process tens of thousands of tokens that generates lightning fast and accurate results. 

The basic process of the Agents application is described below.

1. User query processing
   - User submits a query via text or voice input.
   - The application analyzes the query to determine its category (general assistance, sales leads, research, or financial analysis).

1. Agent assignment
   - The query is routed to the appropriate agent based on content and intent.
   - If the query spans multiple domains, agents collaborate to provide a comprehensive response.
   
1. Data retrieval and processing
   - The selected agent fetches relevant data from available APIs and knowledge bases.
   - AI models process and structure the information for clarity and accuracy.
   
1. Response generation
   - The application generates a structured response.
   - The response is formatted based on the query type (e.g., report format for research, tabular format for financial analysis).

1. User interaction and feedback
   - The user reviews the response and may refine the query.
   - The system continuously learns from interactions to improve future responses.

> **Note**: View the **Agent Reasoning** panel on the right side of the application to see the real-time thought output.

# Prerequisites

Ensure to install the prerequisites.
   - [Python 3.11](https://www.python.org/downloads/release/python-31111/) (exact version required)
   - [Node.js 18.17.0 or later](https://nodejs.org/en/download)
   - [Yarn](https://classic.yarnpkg.com/en/docs/install)
   - [Redis](https://redis.io/download) (via Docker or Homebrew)
     
      ```bash
      # Install Redis with Docker
      docker run --name redis -p 6379:6379 -d redis
      ```
      ```bash
      # Install Redis with Homebrew on macOS
      brew install redis
      brew services start redis
      ```

Get the following API keys to setup the Agents application.
   - [SambaNova API key](https://cloud.sambanova.ai/)
   - [Weights and Baises API key]((https://wandb.ai))
   - [Exa API key](https://exa.co/) for company data
   - [Tavily API key](https://tavily.com/) for deep research capabilities
   - [Clerk](https://clerk.com/) for authentication (you'll need both publishable and secret keys)

### Clerk authentication setup

1. Sign up for a Clerk account at [clerk.com](https://clerk.com/).
1. Create a new application in the Clerk dashboard.
1. Get your publishable key and secret key.
1. Configure your JWT issuer URL.
1. Add these values to your environment variables as shown above.

>**Note**: The DeepSeek-R1-8K model is supported in the application provided.

# Application and Environment variables Setup

## Environment variables setup

#### Frontend environment variables

> **Note**: For the frontend environment variables, go to `/frontend/sales-agent-crew/`.

1. Create a `.env` file with the following variables.
   ```bash
   VITE_API_URL=/api
   VITE_WEBSOCKET_URL=ws://localhost:8000
   VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
   ```

#### Backend environment variables

> **Note**: For the backend environment variables, go to `/backend/`.

1. Create a `.env` file with the following required variables.
   ```bash
   # Authentication
   CLERK_SECRET_KEY=your_clerk_secret_key
   CLERK_JWT_ISSUER=https://your-clerk-instance.clerk.accounts.dev/.well-known/jwks.json
   
   # API Keys for Services
   EXA_API_KEY=your_serper_api_key
   TAVILY_API_KEY=your_tavily_api_key  # Required for Deep Research agent
   
   WANDB_API_KEY=your_wandb_key
   WANDB_PROJECT=your_unique_project_name

   ```
## Application Setup
   
### Frontend setup

Follow the steps below to install the frontend for the Agents application.

> **Note**: For the following commands, go to `/frontend/sales-agent-crew/` directory.

1. Install Vue.js dependencies.

   ```bash
   yarn install
   ```

1. Run a local development environment.

   ```bash
   yarn dev
   ```

1. Create a production build.

   ```bash
   yarn build
   ```

### Backend setup

Follow the steps below to install the backend for the Agents application.

> **Note**: For the following commands, go to `/backend/` directory.

1. Install Python dependencies: Create and activate a virtual environment (for example with venv) and install the project dependencies inside it. Make sure to use Python 3.11.

   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the application.

   ```bash
   uvicorn api.lead_generation_api:create_app --reload --host 127.0.0.1 --port 8000
   ```
   
# Lauching the application 

1. Start Redis

   ```bash
   # From the project root
   brew services start redis
   ```

2. Start the FastAPI backend server.

   ```bash
   # From the project root
   cd backend
   uvicorn api.lead_generation_api:create_app --reload
   ```

3. Start the Vue.js frontend development server.

   ```bash
   # From the project root
   cd frontend/sales-agent-crew/
   yarn dev
   ```

4. Open your browser and navigate to:

   ```bash
   http://localhost:5174/
   ```

# Architecture

![Agents Architecture Diagram](backend/images/architecture-diagram.jpg)

This application is built with:

- Vue 3 + Composition API
- Vite
- TailwindCSS
- Clerk for authentication
- Axios for API calls

# Technology stack

The stack is designed to offer high-performance and scalability for both frontend and backend needs. See the frontend and backend technology stack listed in the table below.

<table style="width:40%; border: 1px solid #000; border-collapse: collapse;">
  <thead>
      <tr style="background-color: #f0f0f0;"> <!-- Shading applied here -->
      <th style="border: 1px solid #000; width: 30%; text-align: left; vertical-align: top;">Category</th>
      <th style="border: 1px solid #000; width: 80%; text-align: left; vertical-align: top;">Technologies used</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid #000; width: 30%; text-align: left; vertical-align: top;"><strong>Frontend</strong></td>
      <td style="border: 1px solid #000; width: 80%; text-align: left; vertical-align: top;">
        <ul>
          <li>Vue.js 3 (Composition API)</li>
          <li>TailwindCSS for styling</li>
          <li>Vite for build tooling</li>
          <li>Clerk for authentication</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td style="border: 1px solid #000; width: 30%; text-align: left; vertical-align: top;"><strong>Backend</strong></td>
      <td style="border: 1px solid #000; width: 80%; text-align: left; vertical-align: top;">
        <ul>
          <li>FastAPI</li>
          <li>CrewAI</li>
          <li>SambaNova Agentic Cloud</li>
          <li>Exa Search API</li>
          <li>Tavily API for research</li>
          <li>Redis for caching</li>
          <li>Financial Data APIs</li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>


# Features

This section describes the agents and feature capabilities of the application. 

## General assistant

The General assistant agent helps with:

- Answering basic questions and queries.
- Providing explanations and clarifications.
- Offering technical support.
- Assisting with general research tasks.

### Example queries

Example queries for general assistance are listed below.

- "What's the difference between supervised and unsupervised learning?"
- "Can you explain how REST APIs work?"
- "What are the best practices for data visualization?"
- "How do I optimize database queries?"
- "Explain the concept of containerization"

## Sales leads

The application uses the Sales leads agent to:

- Find relevant companies matching your criteria.
- Extract key company information.
- Provide funding status and insights.
- Generate customized sales approaches.

### Example queries

Example queries for sales leads information are listed below.

- "Find AI startups in Silicon Valley with Series B funding"
- "Which healthcare companies in Boston are working on drug discovery?"
- "Show me cybersecurity companies in Israel with enterprise clients"
- "Find sustainable energy startups in Nordic countries"
- "Show me B2B SaaS companies in Singapore with over 100 employees"

## Deep research

For research queries, the application uses the Deep research agent to:

- Analyze topics in-depth.
- Create structured research reports.
- Provide educational content.
- Include relevant citations and sources.

### Example queries

Example queries for research and content generation are listed below.

- "Explain quantum computing and its applications in cryptography"
- "How does CRISPR gene editing work in modern medicine?"
- "What's the relationship between AI and neuromorphic computing?"
- "Explain the impact of blockchain on supply chain management"
- "How do machine learning algorithms handle natural language processing?"
- "What are the latest developments in fusion energy research?"

## Financial analysis

For financial queries, the application uses the Financial analysis agent to:

- Analyze company financial performance.
- Track market trends and competitive positioning.
- Evaluate stock performance and valuation metrics.
- Generate investment insights.
- Monitor industry-specific metrics.
- Compare companies within sectors.

### Example queries

Example queries for financial analysis and market research are listed below.

- "Analyze Tesla's recent performance and future growth prospects"
- "How is the semiconductor industry performing this quarter?"
- "Compare cloud revenue growth between Microsoft Azure and AWS"
- "What's the market outlook for AI chip manufacturers?"
- "Evaluate Apple's financial health considering recent product launches"
- "Compare profitability metrics between major EV manufacturers"

## Intelligent query routing

The application automatically determines the best category for your query, ensuring efficient processing. Query routing is automatically done for use-cases such as:

- Sales lead information gathering
- Educational content/research creation
- Financial analysis and market research

## Voice input support

The application allows you to make queries using audio input. Simply click the microphone icon to start speaking. It also offers:

- Automatic speech-to-text transcription
- Hands-free operation for convenience

## Additional features

Additional features of the application are listed below.

- 🔐 Secure API key management – Encrypted for maximum protection
- 📜 Chat history tracking – Easily access past conversations
- 📥 Results export functionality – Download and share insights effortlessly
- 🔄 Real-time query routing – Instant categorization for accurate responses
- 📊 Detailed company insights – In-depth business data at your fingertips
- 💹 Financial analysis and market trends – Stay ahead with real-time analytics
- ✍ AI-generated outreach templates – Craft professional messages instantly


# Usage

1. **Configure API keys**

   - Open settings
   - Enter your API keys
   - Keys are securely encrypted

1. **Start searching**

   - Type your query or use voice input
   - System automatically determines query type
   - Receive structured results

1. **View results**
   - Sales information displayed as cards
   - Research shown as structured reports
   - Export functionality available
   - Save important searches

# License

[MIT License](LICENSE)
