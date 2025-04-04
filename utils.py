import re
import os
import json
import requests
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
    # Initialize the Groq client
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        # For testing purposes, message indicating API key is missing
        return "API key missing. Please set the GROQ_API_KEY environment variable."
    
    client = Groq(api_key=api_key)
    
    try:
        # Call Groq API
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Use Llama 3 model
            messages=[
                {"role": "system", "content": "You are TalentScout AI, a professional AI hiring assistant designed to help with candidate screening. You're helpful, informative, and focused on collecting candidate information and assessing their technical skills."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        # Handle API errors
        return f"I'm having trouble connecting to my knowledge base. Please try again in a moment. Technical details: {str(e)}"
