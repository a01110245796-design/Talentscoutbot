# TalentScout AI Hiring Assistant

A professional dark-themed AI-powered hiring assistant chatbot for TalentScout built with Streamlit and Groq LLM API.

## Features

- AI-powered interview assistant for initial candidate screening
- Professional dark-themed interface
- Intelligent conversation handling
- Data collection from candidates (name, email, experience, etc.)
- Technical question generation based on candidate skills
- Export functionality for saving conversation history (CSV and TXT)
- Custom AI-powered interview questions generator

## Deployment Instructions

### Local Setup

1. Clone this repository
2. Install the dependencies: `pip install -r requirements.txt`
3. Set up your Groq API key as an environment variable: `export GROQ_API_KEY=your-api-key`
4. Run the app: `streamlit run app.py`

### Streamlit Cloud Deployment

1. Create a new app in Streamlit Cloud pointing to this repository
2. In the Streamlit Cloud settings for your app, add your Groq API key as a secret with the name `GROQ_API_KEY`
3. Deploy the app

## Created by

Goddati Bhavyasri