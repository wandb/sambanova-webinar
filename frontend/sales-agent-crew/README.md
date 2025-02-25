# Sales Agent Crew - AI-Powered Sales Lead Generation - Frontend

Sales Agent Crew is an intelligent lead generation platform designed to identify and generate personalized outreach for potential sales leads. By combining the power of AI with a modern web interface, it streamlines your sales prospecting process, saving time and maximizing efficiency.

## Features

- 🎯 **Targeted Lead Generation**: Generate leads based on your criteria.
- ✍️ **AI-Generated Email Templates**: Create personalized email templates with AI.
- 💼 **Company Research & Market Analysis**: Gain valuable insights for better decision-making.
- 🎨 **Modern UI**: Enjoy a responsive and user-friendly interface.
- ⚡ **Real-Time Analysis**: Generate and analyze leads instantly.

## Tech Stack

- **Frontend**: Vue.js, Tailwind CSS
- **AI/ML**: LangChain, SpaCy

## Prerequisites

Before starting, ensure you have the following installed:

- Node.js 16 or higher.
- Yarn package manager.
- Serper API Key.
- Clerk API Key.

## Installation

1. Clone the repository and navigate to the project directory:

With HTTPS:

```bash
git clone https://github.com/sambanova/samba-co-pilot.git
cd samba-co-pilot/frontend/sales-agent-crew
```

With SSH:

```bash
git clone git@github.com:sambanova/samba-co-pilot.git
cd samba-co-pilot/frontend/sales-agent-crew
```

2. Create a .env file and add the Vite API URL:

```bash
CLERK_SECRET_KEY=your_clerk_secret_key
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
VITE_API_URL=/api
```

3. Install Vue dependencies:

```bash
yarn install
```

## Running the Application

1. Start the Vue development server:

```bash
yarn dev
```

or

```bash
npm run dev
```

2. Open your browser and navigate to `http://localhost:5173` to access the application.
