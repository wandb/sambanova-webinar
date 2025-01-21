![Samba Sales Co-Pilot Logo](https://sambanova.ai/hubfs/sambanova-logo-black.png)

# Sales Agent Co-Pilot

**Powered by [SambaNova Cloud](https://cloud.sambanova.ai/)**

An AI-Powered Sales Lead Generation Platform

## Introduction

**Sales Agent Co-Pilot** is an intelligent lead generation platform designed to identify and generate personalized outreach for potential sales leads. By combining the power of AI with a modern web interface, it streamlines your sales prospecting process, saving time and maximizing efficiency.

## Features

- 🎯 **Targeted Lead Generation**: Generate leads based on your specific criteria.
- ✍️ **AI-Generated Email Templates**: Craft personalized outreach emails with the assistance of AI.
- 💼 **Detailed Company Insights**: Access comprehensive information about potential leads, including products, services, opportunities, and challenges.
- 🎤 **Voice Search**: Utilize voice commands to search for leads effortlessly.
- 📜 **Chat History**: Keep track of your past searches with an integrated chat history feature.
- 📥 **Download Results**: Export your search results as JSON files for further analysis or record-keeping.
- 🔐 **Secure API Key Management**: Store your API keys securely on the front end, ensuring they remain private.
- ⚡ **Real-Time Analysis**: Generate and analyze leads instantly without delays.
- 🌐 **OAuth Authentication**: Secure login and authentication through OAuth protocol, keeping your data protected.

## Tech Stack

- **Backend**: FastAPI, CrewAI, **SambaNova Agentic Cloud**, **Exa Search**
- **Frontend**: Vue.js, Tailwind CSS
- **AI/ML**: LangChain, SpaCy

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

- [Node.js](https://nodejs.org/en/) (v14 or above)
- [Python](https://www.python.org/downloads/) (v3.8 or above)
- [npm](https://www.npmjs.com/get-npm) (usually comes with Node.js)
- [SambaNova API Key](https://cloud.sambanova.ai/)
- [Exa API Key](https://exa.ai/)

### Installation

#### Backend Setup

1. **Clone the repository**

    ```bash
    git clone https://github.com/yourusername/sales-agent-co-pilot.git
    cd sales-agent-co-pilot/backend
    ```

2. **Create and activate a virtual environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required Python packages**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the backend server**

    ```bash
    uvicorn api.lead_generation_api:app --host 127.0.0.1 --port 8000
    ```

#### Frontend Setup

1. **Navigate to the frontend directory**

    ```bash
    cd ../frontend/sales-agent-crew
    ```

2. **Install the required npm packages**

    ```bash
    npm install
    ```

3. **Run the frontend development server**

    ```bash
    npm run dev
    ```

4. **Open your browser and navigate to**

    ```bash
    http://localhost:5173/
    ```

## Usage

### API Key Setup

- **Secure Key Storage**: API keys are managed securely on the front end. Upon first launching the app, you will be prompted to enter your **SambaNova** and **Exa** API keys. These keys are stored securely in your browser's local storage and are not shared with the backend.

### Authentication

- **OAuth Authentication**: The app uses OAuth for secure login and authentication. Your past searches and API keys are stored locally on your device and are not shared or stored on the server.

### Generating Leads

1. **Voice Search**

    - Click on the microphone icon to input your search query via voice command.
    - Allow the browser to access your microphone when prompted.

2. **Text Search**

    - Enter your search criteria directly into the search bar.
    - Example query: *"Find AI hardware startups in Silicon Valley focusing on edge computing."*

3. **Viewing Results**

    - Detailed company information will be displayed, including:
        - **Company Name**
        - **Website**
        - **Headquarters**
        - **Funding Status**
        - **Product List**
        - **Key Contacts**
        - **Relevant Trends**
        - **Opportunities**
        - **Challenges**

4. **Downloading Results**

    - Click the download icon to export your search results as a JSON file.

5. **Chat History**

    - Access your past searches through the sidebar.
    - Search history is saved locally and is not shared with other users.

### Direct API Access

You can call the lead generation service directly via the API.

#### Endpoint

```http
POST http://127.0.0.1:8000/generate_leads
```

#### Headers

- `Content-Type: application/json`
- `x-sambanova-key: YOUR_SAMBANOVA_API_KEY`
- `x-exa-key: YOUR_EXA_API_KEY`

#### Body

```json
{
  "prompt": "Generate leads for AI hardware startups in Silicon Valley interested in edge computing"
}
```

#### Sample Response

```json
[
  {
    "company_name": "EdgeAI Tech",
    "website": "www.edgeaitech.com",
    "headquarters": "San Jose, USA",
    "funding_status": "Series B",
    "product_list": ["Edge AI Processors", "Smart Sensors"],
    "key_contacts": [
      {"name": "John Doe", "title": "CEO"},
      {"name": "Jane Smith", "title": "CTO"}
    ],
    "relevant_trends": "Growing demand for real-time processing on edge devices.",
    "opportunities": "Expansion into wearables and IoT devices.",
    "challenges": "Competition from established semiconductor companies.",
    "email_subject": "Driving Edge Computing with AI at EdgeAI Tech",
    "email_body": "Dear EdgeAI Tech,\n\nAs a pioneer in edge computing, integrating advanced AI solutions can elevate your products to new heights. We have identified key market trends and opportunities that align with your company's vision..."
  }
  // Additional company entries...
]
```

**Note**: When calling the API directly, ensure that you handle your API keys securely and avoid exposing them publicly.

## Contributing

We welcome contributions to enhance the **Sales Agent Co-Pilot**. To contribute:

1. **Fork the repository** to your own GitHub account.
2. **Clone the project** to your local machine.

    ```bash
    git clone https://github.com/yourusername/sales-agent-co-pilot.git
    ```

3. **Create a new branch** for your feature or bug fix.

    ```bash
    git checkout -b feature/your-feature-name
    ```

4. **Commit your changes** with descriptive messages.

    ```bash
    git commit -m "Add new feature XYZ"
    ```

5. **Push to your branch** on GitHub.

    ```bash
    git push origin feature/your-feature-name
    ```

6. **Submit a Pull Request** describing your changes.

Please ensure that your code adheres to the existing style guidelines and that all tests pass.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

Thank you for using **Sales Agent Co-Pilot**! If you have any questions or need assistance, feel free to open an issue or reach out to the maintainers.

