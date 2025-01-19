# Sales Agent Crew - AI-Powered Sales Lead Generation

Sales Agent Crew is an intelligent lead generation platform designed to identify and generate personalized outreach for potential sales leads. By combining the power of AI with a modern web interface, it streamlines your sales prospecting process, saving time and maximizing efficiency.

## Features
- 🎯 **Targeted Lead Generation**: Generate leads based on your criteria.
- ✍️ **AI-Generated Email Templates**: Create personalized email templates with AI.
- 💼 **Company Research & Market Analysis**: Gain valuable insights for better decision-making.
- 🎨 **Modern UI**: Enjoy a responsive and user-friendly interface.
- ⚡ **Real-Time Analysis**: Generate and analyze leads instantly.
## Tech Stack
- **Frontend**: Vue.js, Tailwind CSS
- **API Layer** : Fast API
- **Agent Frmeworks**: CrewAI
- **LLM**: OpenAI, Perplexity
- **NLP**: Spacy

## Prerequisites
Before starting, ensure you have the following installed:
- Python 3.8 or higher
- Node.js and npm
- Perplexity API Key
- OpenAI API Key

## Installation
1. Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/yourusername/sales-sphere.git
cd sales-sphere
```
2. Create a .env file in the backend folder and add your API keys:
```bash
PERPLEXITY_API_KEY=your_perplexity_api_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL_NAME=openai_model_name
PERPLEXITY_MODEL_NAME=perplexity model name
```
3. Install Python dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```
4. Install Vue.js dependencies
```bash
cd frontend
npm install
```
## Running the Application
1. Start the FastAPI backend server:
```bash
# From the project root
cd backend
uvicorn api.main:app --reload
```
2. Start the Vue.js frontend development server:
```bash
# From the frontend directory
cd frontend
npm run dev
```

3. Open your browser and navigate to:
```bash
 http://localhost:5174/
 Note : Check for actual url in the log of npm run dev
```
## Contributing
Feel free to fork the repository and submit pull requests




