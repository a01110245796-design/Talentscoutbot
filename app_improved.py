"""
TalentScout AI Hiring Assistant
Enhanced version with improved architecture, security, and technical assessment

Created by: Goddati Bhavyasri
"""

import os
import time
import json
import random
import streamlit as st
import base64
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

# Import custom modules
from models.llm_service import llm_service
from services.conversation import conversation_manager
from services.skill_assessor import skill_assessor
from utils.security import gdpr_compliance, data_encryption, input_sanitizer
from config.settings import get_config
from styles import apply_custom_styles

# Set page configuration
st.set_page_config(
    page_title="TalentScout AI Hiring Assistant",
    page_icon="👨‍💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apply custom styles
apply_custom_styles()

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {
        "name": "",
        "email": "",
        "phone": "",
        "experience": "",
        "position": "",
        "location": "",
        "tech_stack": ""
    }
if "collection_complete" not in st.session_state:
    st.session_state.collection_complete = False
if "conversation_state" not in st.session_state:
    st.session_state.conversation_state = "initial"
if "conversation_ended" not in st.session_state:
    st.session_state.conversation_ended = False
if "custom_questions" not in st.session_state:
    st.session_state.custom_questions = ""
if "custom_questions_generated" not in st.session_state:
    st.session_state.custom_questions_generated = False
if "privacy_agreed" not in st.session_state:
    st.session_state.privacy_agreed = False
if "candidate_id" not in st.session_state:
    # Generate a unique ID for this candidate session
    st.session_state.candidate_id = f"candidate_{int(time.time())}_{random.randint(1000, 9999)}"
if "error_count" not in st.session_state:
    st.session_state.error_count = 0

def get_initials(name: str) -> str:
    """Extract initials from a person's name."""
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

def display_candidate_profile(candidate_info: Dict[str, str]):
    """
    Display a rich candidate profile card with avatar, info, and match score.
    
    Parameters:
    - candidate_info: Dictionary containing candidate information
    """
    # Get candidate information
    name = candidate_info.get('name', 'Candidate')
    position = candidate_info.get('position', 'Role not specified')
    experience = candidate_info.get('experience', '0')
    location = candidate_info.get('location', 'Location not specified')
    tech_stack = candidate_info.get('tech_stack', '')
    
    # Enhanced role match calculation with explanation
    skill_evaluation = None
    matching_skills = []
    match_score = 0
    
    if tech_stack and position:
        # Extract individual skills
        skills = [skill.strip() for skill in tech_stack.replace(',', ' ').split() if skill.strip()]
        
        # Evaluate each skill and calculate average score
        if skills:
            evaluations = []
            total_score = 0
            for skill in skills:
                evaluation = skill_assessor.evaluate_technical_skill(skill, experience, position)
                evaluations.append(evaluation)
                total_score += evaluation["score"]
                if evaluation["score"] >= 70:  # Consider high-scoring skills as matches
                    matching_skills.append(skill)
            
            # Store the most relevant evaluation
            evaluations.sort(key=lambda x: x["score"], reverse=True)
            if evaluations:
                skill_evaluation = evaluations[0]
                
            # Calculate overall match score
            match_score = int(total_score / len(skills)) if skills else 50
    else:
        match_score = 50  # Default value
    
    # Get candidate initials for avatar
    initials = get_initials(name)
    
    # Create profile card
    st.markdown("<div class='section-title'>Candidate Profile</div>", unsafe_allow_html=True)
    st.markdown("<div class='candidate-profile-card'>", unsafe_allow_html=True)
    
    # Profile header with picture/initials and name
    st.markdown(f"""
    <div class='profile-header'>
        <div class='profile-picture'>{initials}</div>
        <div class='profile-info'>
            <div class='profile-name'>{name}</div>
            <div class='profile-position'>📌 {position}</div>
            <div class='profile-location'>📍 {location}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Profile details
    st.markdown("<div class='profile-details'>", unsafe_allow_html=True)
    
    # Experience
    st.markdown(f"""
    <div class='detail-row'>
        <div class='detail-label'>💼 Experience</div>
        <div class='detail-value'>{experience} years</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display email and phone if available
    if candidate_info.get('email'):
        # Secure masking of email for display
        email = candidate_info.get('email', '')
        if '@' in email:
            username, domain = email.split('@')
            if len(username) > 3:
                masked_email = f"{username[:3]}{'*' * (len(username)-3)}@{domain}"
            else:
                masked_email = f"{'*' * len(username)}@{domain}"
        else:
            masked_email = email  # Use as is if it doesn't contain @
            
        st.markdown(f"""
        <div class='detail-row'>
            <div class='detail-label'>📧 Email</div>
            <div class='detail-value'>{masked_email}</div>
        </div>
        """, unsafe_allow_html=True)
    
    if candidate_info.get('phone'):
        # Secure masking of phone for display
        phone = candidate_info.get('phone', '')
        if len(phone) > 4:
            masked_phone = f"{'*' * (len(phone)-4)}{phone[-4:]}"
        else:
            masked_phone = phone
            
        st.markdown(f"""
        <div class='detail-row'>
            <div class='detail-label'>📱 Phone</div>
            <div class='detail-value'>{masked_phone}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # End profile details
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Skills section - extract skills from tech_stack and display as tags
    if tech_stack:
        # Extract individual skills (split by commas, spaces, etc.)
        skills = [skill.strip() for skill in tech_stack.replace(',', ' ').split() if skill.strip()]
        
        # Display skills with improved visualization for matches
        st.markdown("<div class='skill-tags'>", unsafe_allow_html=True)
        for skill in skills:
            skill_class = "skill-tag match" if skill.lower() in [s.lower() for s in matching_skills] else "skill-tag"
            st.markdown(f"<span class='{skill_class}'>{skill}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Match score indicator with animation
    st.markdown(f"""
    <div class='match-score'>
        <div class='match-label'>Role Match</div>
        <div class='match-value'>{match_score}%</div>
        <div class='match-bar-container'>
            <div class='match-bar' style='width: {match_score}%;'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add LinkedIn/GitHub profile links - these are placeholders since we don't collect them
    st.markdown("""
    <div class='profile-links'>
        <a href='#' class='profile-link'>
            <span class='profile-link-icon'>🔗</span> LinkedIn
        </a>
        <a href='#' class='profile-link'>
            <span class='profile-link-icon'>💻</span> GitHub
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # Expandable content section with match explanation
    if skill_evaluation:
        assessment_expander = st.expander("Skill Assessment")
        with assessment_expander:
            st.markdown(f"### Key Skill Assessment")
            st.markdown(f"**{skill_evaluation['skill']}**: {skill_evaluation['recommendation']}")
            
            experience_descriptions = {
                "beginner": "early-career level (0-2 years)",
                "intermediate": "mid-level (2-5 years)",
                "advanced": "senior level (5+ years)"
            }
            
            st.markdown(f"Based on the candidate's {experience} years of experience, they have {experience_descriptions.get(skill_evaluation['experience_level'], 'various')} expertise.")
            
            # Add skill development suggestions
            if skill_evaluation['score'] < 70:
                st.markdown("### Suggested Areas for Development")
                st.markdown("To better match this role, the candidate might consider:")
                
                # Generate suggestions based on position
                position_lower = position.lower()
                if "frontend" in position_lower:
                    st.markdown("- Developing expertise in modern JavaScript frameworks (React, Vue, or Angular)")
                    st.markdown("- Strengthening UI/UX design skills")
                    st.markdown("- Learning state management patterns")
                elif "backend" in position_lower:
                    st.markdown("- Enhancing knowledge of API design and implementation")
                    st.markdown("- Developing database optimization skills")
                    st.markdown("- Learning microservices architecture patterns")
                elif "fullstack" in position_lower:
                    st.markdown("- Balancing frontend and backend skills")
                    st.markdown("- Learning deployment and DevOps practices")
                    st.markdown("- Developing end-to-end testing strategies")
                else:
                    st.markdown("- Further specialization in relevant technologies")
                    st.markdown("- Contributing to open-source projects")
                    st.markdown("- Pursuing relevant certifications or advanced training")
    
    # Expandable content section for resume summary
    resume_expander = st.expander("Resume Summary")
    with resume_expander:
        st.markdown("This is a placeholder for the candidate's resume summary, which would typically include a brief overview of their career, key achievements, and professional goals.")
    
    # Close profile card
    st.markdown("</div>", unsafe_allow_html=True)

def export_chat_history_to_csv(chat_history: List[Dict[str, str]], candidate_info: Dict[str, str]) -> str:
    """
    Export the chat history to CSV format with enhanced GDPR compliance.
    
    Returns:
        Download link HTML
    """
    # Create a StringIO object to store CSV data
    from io import StringIO
    import csv
    
    csv_string = StringIO()
    writer = csv.writer(csv_string)
    
    # Add GDPR and privacy information
    writer.writerow(['TalentScout AI Interview Export (CSV)'])
    writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Data Retention Policy:', '6 months from interview date'])
    writer.writerow([])
    
    # Write the header
    writer.writerow(['Time', 'Role', 'Content'])
    
    # Write the candidate info as the first entry
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Anonymize data for export based on user preference
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
    
    # Create a download link with improved styling
    filename = f"talentscout_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    href = f'<a download="{filename}" href="data:text/csv;base64,{b64}" class="download-button">Download Interview (CSV)</a>'
    
    return href

def export_chat_history_to_txt(chat_history: List[Dict[str, str]], candidate_info: Dict[str, str]) -> str:
    """
    Export the chat history to text format with enhanced GDPR compliance.
    
    Returns:
        Download link HTML
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
    
    # Create a download link with improved styling
    filename = f"talentscout_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    href = f'<a download="{filename}" href="data:text/plain;base64,{b64}" class="download-button">Download Interview (Text)</a>'
    
    return href

def generate_custom_interview_questions(skills: str, experience_level: str, position: str) -> str:
    """
    Generate custom interview questions using advanced skill assessment.
    
    This uses a more sophisticated approach to generate questions appropriate
    for the candidate's experience level and skill set.
    """
    return skill_assessor.generate_technical_questions(skills, experience_level, position)

def show_privacy_notice():
    """Display GDPR-compliant privacy notice and get consent."""
    st.markdown("<div class='section-title'>Privacy Notice</div>", unsafe_allow_html=True)
    st.markdown("<div class='privacy-notice'>", unsafe_allow_html=True)
    
    st.markdown(gdpr_compliance.get_privacy_notice(), unsafe_allow_html=True)
    
    # Add checkbox for consent
    consent = st.checkbox("I understand and agree to the processing of my personal data as described above.")
    
    if consent:
        st.session_state.privacy_agreed = True
        # Log consent for GDPR compliance
        gdpr_compliance.log_consent(st.session_state.candidate_id, datetime.now())
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return consent

# Header section with logo
st.markdown("<div class='header-row'></div>", unsafe_allow_html=True)
try:
    col1, col2 = st.columns([1, 4])
    with col1:
        # Add padding and use larger image for better quality
        st.image("assets/logo.jpg", width=150)
    with col2:
        st.title("TalentScout AI Hiring Assistant")
        st.subheader("Initial Candidate Screening")
except Exception as e:
    st.title("TalentScout AI Hiring Assistant")
    st.subheader("Initial Candidate Screening")

# Main app container
main_container = st.container()
with main_container:
    # First show privacy notice if not agreed yet
    if not st.session_state.privacy_agreed and not st.session_state.conversation_ended:
        if show_privacy_notice():
            st.rerun()
    
    if st.session_state.privacy_agreed:
        # Display chat history
        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history:
                # Use a static greeting to avoid API call on initial load
                static_greeting = "Welcome to TalentScout AI! I'm your hiring assistant, here to help with the initial screening process. To get started, could you please tell me your full name?"
                st.session_state.chat_history.append({"role": "assistant", "content": static_greeting})
            
            # Display chat messages with proper formatting
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.chat_message("user").markdown(message["content"])
                else:
                    # Use markdown for better formatting and word wrapping
                    container = st.chat_message("assistant", avatar="👨‍💼")
                    container.markdown(message["content"], unsafe_allow_html=False)
        
        # User input section
        input_container = st.container()
        with input_container:
            # Process different stages of conversation
            if st.session_state.conversation_ended:
                st.info("Thank you for completing the initial screening. Our hiring team will review your information and contact you soon!")
                
                # Display candidate profile
                if st.session_state.collection_complete:
                    display_candidate_profile(st.session_state.candidate_info)
                
                # Export options for completed conversations
                export_container = st.container()
                with export_container:
                    st.markdown("<div class='export-container'>", unsafe_allow_html=True)
                    st.subheader("Interview Transcript Export")
                    st.markdown("Download the interview transcript in your preferred format:")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        # Export to CSV
                        csv_link = export_chat_history_to_csv(st.session_state.chat_history, st.session_state.candidate_info)
                        st.markdown(csv_link, unsafe_allow_html=True)
                    
                    with col2:
                        # Export to TXT
                        txt_link = export_chat_history_to_txt(st.session_state.chat_history, st.session_state.candidate_info)
                        st.markdown(txt_link, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Generate custom interview questions based on candidate's skills
                    if st.session_state.collection_complete and 'tech_stack' in st.session_state.candidate_info:
                        st.markdown("<div class='custom-questions-container'>", unsafe_allow_html=True)
                        st.subheader("AI-Powered Interview Questions Generator")
                        
                        # Display existing questions if already generated
                        if st.session_state.custom_questions_generated:
                            st.markdown(st.session_state.custom_questions)
                            
                            # Option to regenerate
                            if st.button("Generate New Questions"):
                                st.session_state.custom_questions_generated = False
                                st.rerun()
                        else:
                            # Button to generate questions
                            generate_btn = st.button("Generate Custom Interview Questions")
                            if generate_btn:
                                with st.spinner("Generating custom interview questions based on candidate's skills..."):
                                    skills = st.session_state.candidate_info.get('tech_stack', '')
                                    experience = st.session_state.candidate_info.get('experience', '1-2')
                                    position = st.session_state.candidate_info.get('position', 'Software Developer')
                                    
                                    # Generate questions using improved algorithm
                                    questions = generate_custom_interview_questions(skills, experience, position)
                                    
                                    # Store in session state
                                    st.session_state.custom_questions = questions
                                    st.session_state.custom_questions_generated = True
                                    
                                    # Show the questions
                                    st.markdown(questions)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                user_input = st.chat_input("Type your message here...", disabled=st.session_state.conversation_ended)
                
                if user_input:
                    # Reset error count on each valid input
                    st.session_state.error_count = 0
                    
                    # Add user message to chat history
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    
                    # Use the conversation manager to handle user message
                    response, next_state = conversation_manager.handle_user_message(
                        user_input, 
                        st.session_state.chat_history,
                        st.session_state.candidate_info,
                        st.session_state.conversation_state
                    )
                    
                    # Update conversation state
                    st.session_state.conversation_state = next_state
                    
                    # Check if data collection is complete
                    required_fields = ["name", "email", "phone", "experience", "position", "tech_stack"]
                    if all(field in st.session_state.candidate_info and st.session_state.candidate_info[field] 
                          for field in required_fields):
                        st.session_state.collection_complete = True
                    
                    # Check if conversation has ended
                    if next_state == "completion":
                        st.session_state.conversation_ended = True
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                    # Rerun to update UI
                    st.rerun()

# Footer section with creator's full name highlighted in blue
st.markdown("""
<div class='footer'>
    <div class='footer-content'>
        <span class='footer-text'>Created by</span>
        <span class='footer-highlight'>Goddati Bhavyasri</span>
    </div>
</div>
""", unsafe_allow_html=True)