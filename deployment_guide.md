# Deployment Guide: TalentScout AI Hiring Assistant

This guide will help you deploy the TalentScout AI Hiring Assistant to Streamlit Cloud.

## Pre-Deployment Checklist

1. Make sure you have a [Streamlit Cloud](https://streamlit.io/cloud) account
2. Ensure you have a [Groq API key](https://console.groq.com/) for the LLM integration
3. Verify all files are committed to your GitHub repository

## Deployment Steps

### 1. Connect Your Repository to Streamlit Cloud

1. Log in to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click "New app" button
3. Select your repository with the TalentScout AI application
4. Choose the main branch
5. Enter "app.py" as the main file path

### 2. Configure Environment Variables

**Important**: The application requires a Groq API key to function correctly. You'll need to add this as a secret in Streamlit Cloud:

1. In your app settings, navigate to the "Secrets" section
2. Add the following secret:
   ```
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
3. Replace `your_groq_api_key_here` with your actual Groq API key

### 3. Deploy the Application

1. Click "Deploy!" to launch your application
2. Streamlit Cloud will build and deploy your app
3. Once complete, you'll be provided with a URL where your app is hosted

## Post-Deployment Verification

After deployment, verify the following:

1. The application loads without errors
2. You can see the TalentScout AI logo and title
3. The chatbot conversation starts correctly
4. The candidate information collection works
5. The profile card displays properly after information collection

## Troubleshooting

If you encounter any issues during deployment:

1. Check the application logs in Streamlit Cloud
2. Verify the GROQ_API_KEY environment variable is set correctly
3. Make sure all required packages are listed in the requirements.txt file
4. Confirm the assets folder with logo.jpg is present in your repository

## Help and Support

If you need further assistance, please contact:
- Email: support@talentscout.ai
- GitHub: Create an issue in the repository

## Created By

Goddati Bhavyasri