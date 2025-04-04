import re
import os
import json
import base64
import csv
import requests
from io import StringIO
from datetime import datetime
from groq import Groq

def validate_input(field, value):
    """Validate user input based on field type."""
    if not value.strip():
        return False, "This field cannot be empty. Please provide a valid response."
    
    if field == "email":
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, value):
            return False, "Please enter a valid email address (example: name@domain.com)."
    
    elif field == "phone":
        # Simplified phone validation - accepts digits, spaces, dashes, and parentheses
        phone_pattern = r'^[\d\s\(\)\-\+]{7,20}$'
        if not re.match(phone_pattern, value):
            return False, "Please enter a valid phone number."
    
    elif field == "experience":
        try:
            exp = float(value.replace('years', '').replace('year', '').strip())
            if exp < 0 or exp > 50:
                return False, "Please enter a realistic value for your years of experience."
        except:
            return False, "Please enter your experience in years (e.g., '5' or '5 years')."
    
    return True, "Valid input"

def format_chat_history(messages):
    """Format chat history for prompt context."""
    formatted = ""
    for msg in messages:
        speaker = "User" if msg["role"] == "user" else "Assistant"
        formatted += f"{speaker}: {msg['content']}\n\n"
    return formatted

def get_full_response(prompt):
    """Get a response from the Groq LLM API."""
    # Get API key from environment variables or Streamlit secrets if deployed
    api_key = None
    
    # Try to get from environment variables first
    api_key = os.environ.get("GROQ_API_KEY")
    
    # If not found and in Streamlit Cloud environment, try to get from st.secrets
    if not api_key:
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
        except Exception as e:
            print(f"Error accessing Streamlit secrets: {str(e)}")
    
    # Check if API key exists
    if not api_key:
        print("API key not found. Please set the GROQ_API_KEY in environment variables or Streamlit secrets.")
        return "I'm unable to respond at the moment. Please ensure the API key is configured correctly."
    
    try:
        client = Groq(api_key=api_key)
        
        # Call Groq API
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Use Llama 3 model
            messages=[
                {"role": "system", "content": "You are TalentScout AI, a professional AI hiring assistant designed to help with candidate screening. Keep responses concise under 40 words. Be direct, clear, and professional. Use simple sentences and avoid lengthy explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300,  # Reduced token count for shorter responses
        )
        
        # Format response to ensure it fits within screen
        content = response.choices[0].message.content
        
        # Break very long words if necessary (over 40 chars)
        words = content.split()
        for i, word in enumerate(words):
            if len(word) > 40:
                # Insert a zero-width space every 40 characters for long words
                words[i] = "".join([word[j:j+40] + "\u200B" for j in range(0, len(word), 40)])
        
        formatted_content = " ".join(words)
        return formatted_content
    except Exception as e:
        # Handle API errors
        return "I'm having trouble connecting. Please try again in a moment."

def export_chat_history_to_csv(chat_history, candidate_info):
    """Export the chat history to CSV format."""
    # Create a StringIO object to store CSV data
    csv_string = StringIO()
    writer = csv.writer(csv_string)
    
    # Write the header
    writer.writerow(['Time', 'Role', 'Content'])
    
    # Write the candidate info as the first entry
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    candidate_summary = f"Candidate: {candidate_info.get('name', 'N/A')}\n"
    candidate_summary += f"Email: {candidate_info.get('email', 'N/A')}\n"
    candidate_summary += f"Phone: {candidate_info.get('phone', 'N/A')}\n"
    candidate_summary += f"Experience: {candidate_info.get('experience', 'N/A')} years\n"
    candidate_summary += f"Position: {candidate_info.get('position', 'N/A')}\n"
    candidate_summary += f"Location: {candidate_info.get('location', 'N/A')}\n"
    candidate_summary += f"Tech Stack: {candidate_info.get('tech_stack', 'N/A')}"
    
    writer.writerow([timestamp, 'System', candidate_summary])
    
    # Write each chat message with a timestamp
    for message in chat_history:
        writer.writerow([timestamp, message["role"].capitalize(), message["content"]])
    
    # Get the CSV data as a string
    csv_data = csv_string.getvalue()
    csv_string.close()
    
    # Encode as base64 for download link
    b64 = base64.b64encode(csv_data.encode()).decode()
    
    # Create a download link
    filename = f"talentscout_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    href = f'<a download="{filename}" href="data:text/csv;base64,{b64}" class="download-button">Download Interview (CSV)</a>'
    
    return href

def export_chat_history_to_txt(chat_history, candidate_info):
    """Export the chat history to text format."""
    # Create a string to store the text data
    text_content = f"TalentScout AI Interview - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Add the candidate info
    text_content += "CANDIDATE INFORMATION\n"
    text_content += "=====================\n"
    text_content += f"Name: {candidate_info.get('name', 'N/A')}\n"
    text_content += f"Email: {candidate_info.get('email', 'N/A')}\n"
    text_content += f"Phone: {candidate_info.get('phone', 'N/A')}\n"
    text_content += f"Experience: {candidate_info.get('experience', 'N/A')} years\n"
    text_content += f"Position: {candidate_info.get('position', 'N/A')}\n"
    text_content += f"Location: {candidate_info.get('location', 'N/A')}\n"
    text_content += f"Tech Stack: {candidate_info.get('tech_stack', 'N/A')}\n\n"
    
    # Add the interview conversation
    text_content += "INTERVIEW TRANSCRIPT\n"
    text_content += "===================\n\n"
    
    for message in chat_history:
        role = "TalentScout AI:" if message["role"] == "assistant" else f"{candidate_info.get('name', 'Candidate')}:"
        text_content += f"{role}\n{message['content']}\n\n"
    
    # Encode as base64 for download link
    b64 = base64.b64encode(text_content.encode()).decode()
    
    # Create a download link
    filename = f"talentscout_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    href = f'<a download="{filename}" href="data:text/plain;base64,{b64}" class="download-button">Download Interview (Text)</a>'
    
    return href

def generate_custom_interview_questions(skills, experience_level, position):
    """Generate custom interview questions based on candidate skills."""
    # Prepare the prompt for the AI to generate questions
    prompt = f"""
    Generate 5 professional interview questions for a {position} candidate with {experience_level} years of experience who has the following skills: {skills}.
    
    The questions should:
    1. Be challenging but appropriate for their experience level
    2. Include at least one behavioral question related to their skills
    3. Include at least one technical question specific to their technology stack
    4. Include at least one question about problem-solving in their domain
    5. Be concise and clear
    
    Format each question as a numbered list item, starting with "Question 1:" etc.
    Do not include answers to the questions. Just list the 5 questions.
    """
    
    try:
        return get_full_response(prompt)
    except Exception as e:
        return "Unable to generate custom interview questions at this time. Please try again later."
