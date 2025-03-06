![Samba Sales Co-Pilot Logo](https://sambanova.ai/hubfs/sambanova-logo-black.png)

<h1 style="font-size: 3em;">Agents</h1>

# Overview

The Agents application helps sales teams and researchers by:

- Generating qualified sales information with company insights.
- Creating detailed research reports and educational content.
- Intelligently routing queries to the appropriate service.
- Supporting voice input for natural interaction.

This application has four agents (AI-powered assistants)

1. General Assistant
1. Sales Leads
1. Deep Research
1. Finance Analysis

# Architecture

![Co-Pilot Architecture Diagram](backend/images/architecture-diagram.jpg)

This application is built with:

- Vue 3 + Composition API
- Vite
- TailwindCSS
- Clerk for authentication
- Axios for API calls

# Technology stack

This application is built using the following technologies. The stack is designed to offer high-performance and scalability for both frontend and backend needs.

See the frontend and backend technology stack listed in the table below.

<table style="width:40%; border: 1px solid #000; border-collapse: collapse;">
  <thead>
      <tr style="background-color: #f0f0f0;"> <!-- Shading applied here -->
      <th style="border: 1px solid #000; width: 30%;">Category</th>
      <th style="border: 1px solid #000; width: 80%;">Technologies used</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid #000; width: 30%;"><strong>Frontend</strong></td>
      <td style="border: 1px solid #000; width: 80%;">
        <ul>
          <li>Vue.js 3 (Composition API)</li>
          <li>TailwindCSS for styling</li>
          <li>Vite for build tooling</li>
          <li>Clerk for authentication</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td style="border: 1px solid #000; width: 30%;"><strong>Backend</strong></td>
      <td style="border: 1px solid #000; width: 80%;">
        <ul>
          <li>FastAPI</li>
          <li>CrewAI</li>
          <li>SambaNova Agentic Cloud</li>
          <li>Exa Search API</li>
          <li>Financial Data APIs</li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>

# Features

This section describes the features and capabilities of the application. 

## General assistance

The **General Assistant** agent helps with:

- Answering basic questions and queries.
- Providing explanations and clarifications.
- Offering technical support.
- Assisting with general research tasks.

### Example queries

See example queries for general assistance.

- "What's the difference between supervised and unsupervised learning?"
- "Can you explain how REST APIs work?"
- "What are the best practices for data visualization?"
- "How do I optimize database queries?"
- "Explain the concept of containerization"

## Sales lead information

The application uses the **Sales Lead** agent to:

- Find relevant companies matching your criteria.
- Extract key company information.
- Provide funding status and insights.
- Generate customized sales approaches.

### Example queries

See example queries for Sales lead information.

- "Find AI startups in Silicon Valley with Series B funding"
- "Which healthcare companies in Boston are working on drug discovery?"
- "Show me cybersecurity companies in Israel with enterprise clients"
- "Find sustainable energy startups in Nordic countries"
- "Show me B2B SaaS companies in Singapore with over 100 employees"

## Research and content generation

For research queries, the application uses the **Deep Research** agent to:

- Analyze topics in-depth
- Create structured research reports
- Provide educational content
- Include relevant citations and sources

### Example queries

See example queries for research and content generation.

- "Explain quantum computing and its applications in cryptography"
- "How does CRISPR gene editing work in modern medicine?"
- "What's the relationship between AI and neuromorphic computing?"
- "Explain the impact of blockchain on supply chain management"
- "How do machine learning algorithms handle natural language processing?"
- "What are the latest developments in fusion energy research?"

## Financial analysis and market research

For financial queries, the application uses the **Financial Analysis** agent to:

- Analyze company financial performance
- Track market trends and competitive positioning
- Evaluate stock performance and valuation metrics
- Generate investment insights
- Monitor industry-specific metrics
- Compare companies within sectors

### Example queries

See example queries for financial analysis and market research.

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

Additional features of the application are:

- 🔐 Secure API key management – Encrypted for maximum protection
- 📜 Chat history tracking – Easily access past conversations
- 📥 Results export functionality – Download and share insights effortlessly
- 🔄 Real-time query routing – Instant categorization for accurate responses
- 📊 Detailed company insights – In-depth business data at your fingertips
- 💹 Financial analysis and market trends – Stay ahead with real-time analytics
- ✍ AI-generated outreach templates – Craft professional messages instantly

# Technical setup

## Prerequisites

Ensure to install the prerequisites.

- [Python 3.8 or later](https://www.python.org/downloads/)
- [Node.js 16 or later](https://nodejs.org/en/download)
- [Yarn](https://classic.yarnpkg.com/en/docs/install)

## API keys

Get the following API keys to setup the Agent application.

  - [SambaNova API key](https://cloud.sambanova.ai/)
  - [Serper API key](https://serper.dev/) for web search
  - [Exa API key](https://exa.co/) for company data
  - [Fireworks API key](https://fireworks.ai/) 

> **Note**: After logging in, click the settings gear icon ⚙️ (located next to your user photo) to configure your API keys. The application requires these keys to function properly.

# Running the application

You can run the application in two ways

## Cloud hosted version

This version is hosted on SambaNova Cloud. It eliminates the need for local installation.

1. To access the platform, go to the [Agents application](https://aiskagents.cloud.snova.ai/) login page.
1. When you create a login using available options, the following screen shows the sign-in authentication via **Clerk**, a third-party authentication service.
1. You will receive an email from the Clerk application with login instructions. Follow the steps to log in to the Agent application. This is a one-time setup process required during initial login.
1. Once you login, go to settings and add the API keys.
1. You can now use the application to enhance sales workflows, conduct research, and gain actionable insights.

## Locally hosted version

### Frontend setup

Follow the steps below to install the frontend for the Agent application.

> **Note**: For the following commands, go to `/frontend/sales-agent-crew/` directory.

1. Install Vue.js dependencies

   ```bash
   yarn install
   ```

1. Run a local development environment

   ```bash
   yarn dev
   ```

1. Create a production build

   ```bash
   yarn build
   ```

### Backend setup

Follow the steps below to install the backend for the Agent application.

> **Note**: For the following commands, go to `/backend/` directory.

1. **Install Python dependencies** - Create and activate a virtual environment (for example with venv) and install the project dependencies inside it.

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the application**

   ```bash
   uvicorn api.main:app --reload
   ```

### Setup environment variables

> **Note**: For the frontend environment variables, go to `/frontend/sales-agent-crew/`.

1. Create a `.env` file.
   ```bash
   VITE_API_URL=your_api_url
   ```

1. Start the FastAPI backend server.

   ```bash
   # From the project root
   cd backend
   uvicorn api.main:app --reload
   ```

2. Start the Vue.js frontend development server.

   ```bash
   # From the project root
   cd frontend/sales-agent-crew/
   yarn dev
   ```

3. Open your browser and navigate to:

   ```bash
   http://localhost:5174/
   ```

> **Note**: Update the URL in the LeadGenerationAPI CORS API if it's different.

### API keys setup

Access the settings modal to configure your:

- SambaNova API key
- Serper API key
- Exa API key
- Fireworks API key

Ensure that API keys are encrypted before storing them in localStorage.

## Usage

1. **Configure API Keys**

   - Open settings
   - Enter your API keys
   - Keys are securely encrypted

2. **Start Searching**

   - Type your query or use voice input
   - System automatically determines query type
   - Receive structured results

3. **View Results**
   - Sales information displayed as cards
   - Research shown as structured reports
   - Export functionality available
   - Save important searches

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[MIT License](LICENSE)
