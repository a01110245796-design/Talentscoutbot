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
    # Get API key from environment variables
    api_key = os.environ.get("GROQ_API_KEY")
    
    # Check if API key exists
    if not api_key:
        return "API key not found. Please set the GROQ_API_KEY environment variable."
    
    client = Groq(api_key=api_key)
    
    try:
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
