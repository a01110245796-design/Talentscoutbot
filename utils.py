"""
Utility functions for TalentScout AI Hiring Assistant
"""

import os
import re
import json
import random
import logging
import base64
from datetime import datetime
from typing import Tuple, List, Dict, Any

# Import prompts
from prompts import FALLBACK_RESPONSES, SYSTEM_PROMPTS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_input(field: str, value: str) -> Tuple[bool, str]:
    """
    Validate user input based on field type.
    
    Args:
        field: The field to validate (email, phone, experience, etc.)
        value: The value to validate
    
    Returns:
        Tuple of (is_valid, value_or_error_message)
    """
    if not value:
        return False, f"Please provide a valid {field}."
    
    # Email validation
    if field == "email":
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            return False, "Please provide a valid email address (e.g., name@example.com)."
        return True, value
    
    # Phone validation
    elif field == "phone":
        # Remove non-digit characters for validation
        digits = re.sub(r'\D', '', value)
        if len(digits) < 7 or len(digits) > 15:
            return False, "Please provide a valid phone number (e.g., 123-456-7890)."
        return True, value
    
    # Experience validation (should be a number)
    elif field == "experience":
        try:
            # Try to extract a number
            numeric_value = re.sub(r'[^\d\.]', '', value)
            experience = float(numeric_value)
            if experience < 0 or experience > 100:
                return False, "Please provide a valid number of years of experience."
            return True, str(experience)
        except ValueError:
            return False, "Please provide a valid number for your years of experience."
    
    # For other fields, just return the value
    return True, value

def format_chat_history(messages: List[Dict[str, str]]) -> str:
    """
    Format chat history for prompt context.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        
    Returns:
        Formatted chat history as a string
    """
    formatted = ""
    for msg in messages:
        speaker = "User" if msg["role"] == "user" else "Assistant"
        content = msg["content"]
        formatted += f"{speaker}: {content}\n\n"
    return formatted

def get_full_response(prompt: str, system_prompt: str = None) -> str:
    """
    Get a response from the Groq LLM API with comprehensive fallback mechanisms.
    
    Args:
        prompt: The prompt to send to the LLM
        system_prompt: Optional system prompt to use
        
    Returns:
        The generated response or a fallback response if the API fails
    """
    import os
    import time
    import groq
    
    try:
        # Try to use Groq API
        client = groq.Client(api_key=os.environ.get("GROQ_API_KEY", ""))
        
        # Add system role for better context
        system_message = system_prompt or SYSTEM_PROMPTS["screening"]
        
        # Create the completion with exponential backoff retry
        max_retries = 3
        backoff_factor = 2
        retry_delay = 1  # initial delay in seconds
        
        for attempt in range(max_retries):
            try:
                completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                
                return completion.choices[0].message.content
            
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {str(e)}")
                
                # If this is the last attempt, raise the exception
                if attempt == max_retries - 1:
                    raise
                
                # Otherwise, wait and retry with exponential backoff
                time.sleep(retry_delay)
                retry_delay *= backoff_factor
        
    except Exception as e:
        logger.error(f"Error getting response from Groq: {str(e)}")
        
        # Return a fallback response from predefined options
        return random.choice(FALLBACK_RESPONSES)

def export_chat_history_to_csv(chat_history: List[Dict[str, str]], candidate_info: Dict[str, str]) -> str:
    """
    Export the chat history to CSV format.
    
    Args:
        chat_history: List of message dictionaries with 'role' and 'content' keys
        candidate_info: Dictionary containing candidate information
        
    Returns:
        HTML string containing download link
    """
    from io import StringIO
    import csv
    
    csv_string = StringIO()
    writer = csv.writer(csv_string)
    
    # Add header information
    writer.writerow(['TalentScout AI Interview Export (CSV)'])
    writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Data Retention Policy:', '6 months from interview date'])
    writer.writerow([])
    
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
    
    # Create a download link with proper styling
    filename = f"talentscout_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    href = f'<a href="data:text/csv;base64,{b64}" download="{filename}" class="download-button">Download Interview (CSV)</a>'
    
    return href

def export_chat_history_to_txt(chat_history: List[Dict[str, str]], candidate_info: Dict[str, str]) -> str:
    """
    Export the chat history to text format.
    
    Args:
        chat_history: List of message dictionaries with 'role' and 'content' keys
        candidate_info: Dictionary containing candidate information
        
    Returns:
        HTML string containing download link
    """
    # Create a string to store the text data
    text_content = f"TalentScout AI Interview - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Add privacy notice
    text_content += "DATA PRIVACY NOTICE\n"
    text_content += "=================\n"
    text_content += "This interview transcript contains personal data protected under GDPR.\n"
    text_content += "Data retention period: 6 months from interview date\n"
    text_content += "For privacy concerns, contact: privacy@talentscout.ai\n\n"
    
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
    
    # Create a download link with proper styling
    filename = f"talentscout_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}" class="download-button">Download Interview (Text)</a>'
    
    return href

def get_initials(name: str) -> str:
    """
    Extract initials from a person's name.
    
    Args:
        name: The person's full name
    
    Returns:
        initials: 1-2 letters representing the person's initials
    """
    if not name or not isinstance(name, str):
        return "?"
    
    # Split the name and get initials (up to 2)
    parts = name.strip().split()
    if not parts:
        return "?"
    
    if len(parts) == 1:
        # Only one name, take the first letter
        return parts[0][0].upper()
    else:
        # Multiple names, take first letter of first and last name
        return (parts[0][0] + parts[-1][0]).upper()

def calculate_role_match(skills: str, experience: str, position: str) -> Tuple[int, List[str]]:
    """
    Calculate a role match score based on candidate skills and experience.
    
    Args:
        skills: String containing candidate's skills
        experience: String or numeric value representing years of experience
        position: The position they're applying for
    
    Returns:
        Tuple of (score, matching_skills)
    """
    # Parse skills list
    skill_list = [s.strip().lower() for s in re.split(r'[,;\s]+', skills) if s.strip()]
    
    # Define skill relevance to common roles
    role_skills = {
        "frontend": ["javascript", "typescript", "react", "vue", "angular", "html", "css", "responsive", "ui/ux", "frontend"],
        "backend": ["java", "python", "c#", "node.js", "php", "go", "rust", "sql", "nosql", "api", "backend"],
        "fullstack": ["javascript", "python", "java", "node.js", "react", "angular", "vue", "sql", "nosql", "fullstack"],
        "devops": ["docker", "kubernetes", "jenkins", "github actions", "aws", "azure", "gcp", "linux", "ci/cd", "devops"],
        "data": ["python", "r", "sql", "nosql", "pandas", "hadoop", "spark", "etl", "tableau", "power bi", "data"],
        "mobile": ["android", "ios", "swift", "kotlin", "react native", "flutter", "mobile"],
        "machine learning": ["python", "tensorflow", "pytorch", "scikit-learn", "nlp", "computer vision", "ml", "ai"]
    }
    
    # Match position to role
    position_lower = position.lower()
    matched_role = None
    max_match = 0
    
    for role, keywords in role_skills.items():
        match_score = 0
        for keyword in keywords:
            if keyword in position_lower:
                match_score += 1
        
        if match_score > max_match:
            max_match = match_score
            matched_role = role
    
    # If no role matched, default to a generic role
    if not matched_role:
        # Default to fullstack as a broad general role
        matched_role = "fullstack"
    
    # Find matching skills
    relevant_skills = role_skills[matched_role]
    matching_skills = []
    
    for skill in skill_list:
        if any(keyword in skill or skill in keyword for keyword in relevant_skills):
            matching_skills.append(skill)
    
    # Calculate match score
    if not skill_list:
        return 50, matching_skills  # Default score
    
    # Base match on % of skills that match the role
    match_percentage = min(100, (len(matching_skills) / len(relevant_skills) * 100))
    
    # Adjust based on experience (more experience = higher score)
    try:
        exp_value = float(re.sub(r'[^\d\.]', '', str(experience)))
        
        # Adjust for experience
        if exp_value < 2:
            experience_factor = 0.85  # Junior
        elif exp_value < 5:
            experience_factor = 1.0  # Mid-level
        else:
            experience_factor = 1.15  # Senior
            
        # Apply experience factor
        match_percentage = match_percentage * experience_factor
        
    except (ValueError, TypeError):
        # If experience can't be parsed, don't adjust
        pass
    
    # Ensure score is between 20-100
    score = max(20, min(100, int(match_percentage)))
    
    return score, matching_skills

def get_experience_level(experience: str) -> str:
    """
    Determine experience level from years of experience.
    
    Args:
        experience: String or numeric value representing years of experience
    
    Returns:
        Experience level (beginner, intermediate, or advanced)
    """
    try:
        years = float(re.sub(r'[^\d\.]', '', experience))
        if years < 2:
            return "beginner"
        elif years < 5:
            return "intermediate"
        else:
            return "advanced"
    except (ValueError, TypeError):
        return "intermediate"  # Default if parsing fails

def generate_custom_interview_questions(skills: str, experience_level: str, position: str) -> str:
    """
    Generate custom interview questions based on candidate skills.
    
    Args:
        skills: String containing candidate's skills
        experience_level: String representing years of experience
        position: The position they're applying for
    
    Returns:
        Markdown formatted string with interview questions
    """
    import os
    import groq
    
    # Parse skills
    skill_list = [s.strip() for s in re.split(r'[,;\s]+', skills) if s.strip()]
    
    # Determine experience level
    level_description = get_experience_level(experience_level)
    
    try:
        # Try to use Groq API
        client = groq.Client(api_key=os.environ.get("GROQ_API_KEY", ""))
        
        system_prompt = SYSTEM_PROMPTS["question_generation"]
        
        user_prompt = f"""Generate a set of 3-5 custom technical interview questions for a {position} candidate 
with {level_description} experience level. The candidate has listed the following skills: {', '.join(skill_list)}.

The questions should:
1. Focus on the most relevant skills for the {position} position
2. Be appropriate for someone with {level_description} experience
3. Include a mix of technical knowledge and problem-solving questions
4. Be specific and detailed rather than generic
5. Be formatted as markdown with clear section headings

Format your response with:
1. A title section
2. A brief intro explaining the question set
3. Numbered questions with clear headings indicating the skill being tested
4. A closing interviewer note section with 2-3 tips for evaluating the responses
"""
        
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error generating interview questions: {str(e)}")
        
        # Create fallback questions if API is unavailable
        fallback_questions = f"""
## Technical Interview Questions for {position}

Based on the candidate's profile (experience level: {level_description}, position: {position}), here are customized technical questions:

### 1. General Experience
Can you describe your most challenging project related to {position} and how you approached it?

### 2. Problem Solving
What strategies do you use when debugging complex issues in your code or systems?

### 3. Technical Knowledge
"""
        
        # Add a skill-specific question for the top skills
        if skill_list:
            for i, skill in enumerate(skill_list[:2]):
                fallback_questions += f"\n### {i+3}. {skill.capitalize()} Experience\n"
                fallback_questions += f"Could you describe your experience with {skill} and how you've applied it in your work?\n"
        
        fallback_questions += """
### Interviewer Notes
- Focus on the candidate's problem-solving approach rather than specific syntax
- Evaluate depth of understanding rather than memorized answers
- Consider how the candidate's experiences align with your team's needs
"""
        
        return fallback_questions

def load_dotenv():
    """Load environment variables from .env file if python-dotenv is available."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Loaded environment variables from .env file")
    except ImportError:
        logger.info("python-dotenv not installed, skipping .env file loading")
    except Exception as e:
        logger.warning(f"Error loading .env file: {str(e)}")

def check_api_credentials():
    """Check if the Groq API key is available in the environment."""
    api_key = os.environ.get("GROQ_API_KEY")
    
    # For deployment instructions
    if not api_key:
        logger.warning("GROQ_API_KEY not found in environment variables")
        logger.info("Remember to set GROQ_API_KEY in your Streamlit Cloud settings during deployment.")
        return False
        
    logger.info("GROQ_API_KEY found in environment variables - API is available")
    return True