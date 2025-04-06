"""
TalentScout AI Hiring Assistant

A professional dark-themed AI-powered hiring assistant chatbot designed to 
streamline recruitment processes with intelligent conversation and a user-friendly interface.

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

# Import custom modules (with fallbacks if modules aren't fully initialized yet)
try:
    from models.llm_service import llm_service
    from services.conversation import conversation_manager
    from services.skill_assessor import skill_assessor
    from utils.security import gdpr_compliance, data_encryption, input_sanitizer
    from config.settings import get_config
    from styles import apply_custom_styles
    
    # Flag for modular version
    st.session_state.using_modular_version = True
except ImportError as e:
    # Fall back to local utility functions
    from utils import (
        validate_input, format_chat_history, get_full_response,
        export_chat_history_to_csv, export_chat_history_to_txt,
        get_initials, calculate_role_match, generate_custom_interview_questions
    )
    
    # Flag for modular version
    st.session_state.using_modular_version = False
    
    # Log the import error
    import logging
    logging.error(f"Error importing modular components: {str(e)}")
    st.error("Running in compatibility mode. Some advanced features may be unavailable.")

# Set page configuration
st.set_page_config(
    page_title="TalentScout AI Hiring Assistant",
    page_icon="👨‍💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apply custom styles if available, otherwise use basic styling
if st.session_state.using_modular_version:
    apply_custom_styles()
else:
    # Basic styling
    st.markdown("""
    <style>
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        
        .footer {
            position: relative;
            bottom: 0;
            width: 100%;
            text-align: center;
            padding: 20px 0;
            margin-top: 40px;
            border-top: 1px solid #2d3748;
        }
        
        .footer-highlight {
            color: #60a5fa;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

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

# Local implementation of functions for non-modular fallback mode
def local_get_initials(name):
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

def local_display_candidate_profile(candidate_info):
    """Display a rich candidate profile card with avatar, info, and match score."""
    # Get candidate information
    name = candidate_info.get('name', 'Candidate')
    position = candidate_info.get('position', 'Role not specified')
    experience = candidate_info.get('experience', '0')
    location = candidate_info.get('location', 'Location not specified')
    tech_stack = candidate_info.get('tech_stack', '')
    
    # Basic match calculation
    match_score = 50  # Default value
    
    if tech_stack and position:
        try:
            match_score, matching_skills = calculate_role_match(tech_stack, experience, position)
        except Exception as e:
            st.error(f"Error calculating match score: {str(e)}")
            matching_skills = []
    else:
        matching_skills = []
    
    # Get candidate initials for avatar
    initials = local_get_initials(name)
    
    # Create profile card
    st.markdown("<div style='margin-top: 30px; margin-bottom: 20px; font-weight: bold; color: #60a5fa; border-bottom: 1px solid #3b82f6; padding-bottom: 5px;'>Candidate Profile</div>", unsafe_allow_html=True)
    
    # Profile container
    st.markdown(f"""
    <div style='background-color: #1f2937; border-radius: 10px; padding: 20px; margin: 20px 0; border-left: 4px solid #3b82f6;'>
        <div style='display: flex; align-items: center; margin-bottom: 20px;'>
            <div style='width: 80px; height: 80px; background-color: #3b82f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; color: white; margin-right: 20px;'>{initials}</div>
            <div>
                <div style='font-size: 1.5rem; font-weight: bold; margin-bottom: 5px;'>{name}</div>
                <div style='font-size: 1rem; color: #d1d5db; margin-bottom: 5px;'>📌 {position}</div>
                <div style='font-size: 0.9rem; color: #9ca3af;'>📍 {location}</div>
            </div>
        </div>
        
        <div style='margin-bottom: 20px;'>
            <div style='display: flex; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #374151;'>
                <div style='flex: 1; font-weight: 500; color: #9ca3af;'>💼 Experience</div>
                <div style='flex: 2;'>{experience} years</div>
            </div>
    """, unsafe_allow_html=True)
    
    # Display email and phone if available
    if candidate_info.get('email'):
        email = candidate_info.get('email', '')
        st.markdown(f"""
        <div style='display: flex; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #374151;'>
            <div style='flex: 1; font-weight: 500; color: #9ca3af;'>📧 Email</div>
            <div style='flex: 2;'>{email}</div>
        </div>
        """, unsafe_allow_html=True)
    
    if candidate_info.get('phone'):
        phone = candidate_info.get('phone', '')
        st.markdown(f"""
        <div style='display: flex; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #374151;'>
            <div style='flex: 1; font-weight: 500; color: #9ca3af;'>📱 Phone</div>
            <div style='flex: 2;'>{phone}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Skills section - extract skills from tech_stack and display as tags
    if tech_stack:
        # Extract individual skills (split by commas, spaces, etc.)
        skills = [skill.strip() for skill in tech_stack.replace(',', ' ').split() if skill.strip()]
        
        # Display skills with coloring for matching skills
        st.markdown("<div style='display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        for skill in skills:
            if skill.lower() in [s.lower() for s in matching_skills]:
                st.markdown(f"<span style='background-color: #1e3a8a; color: #ffffff; border-radius: 50px; padding: 6px 12px; font-size: 0.85rem; display: inline-block; border: 1px solid #3b82f6;'>{skill}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='background-color: #374151; color: #d1d5db; border-radius: 50px; padding: 6px 12px; font-size: 0.85rem; display: inline-block;'>{skill}</span>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Match score indicator
    st.markdown(f"""
    <div style='margin-bottom: 20px;'>
        <div style='font-size: 1rem; font-weight: 500; margin-bottom: 5px; color: #d1d5db;'>Role Match</div>
        <div style='font-size: 1.2rem; font-weight: bold; color: #3b82f6; margin-bottom: 5px;'>{match_score}%</div>
        <div style='width: 100%; height: 10px; background-color: #374151; border-radius: 5px; overflow: hidden;'>
            <div style='height: 100%; width: {match_score}%; background: linear-gradient(90deg, #2563eb, #60a5fa); border-radius: 5px; transition: width 1s;'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Close profile card
    st.markdown("</div>", unsafe_allow_html=True)

def local_export_chat_history_to_csv(chat_history, candidate_info):
    """Export the chat history to CSV format."""
    from io import StringIO
    import csv
    
    csv_string = StringIO()
    writer = csv.writer(csv_string)
    
    # Add header information
    writer.writerow(['TalentScout AI Interview Export (CSV)'])
    writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
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
    
    # Create a download link
    filename = f"talentscout_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    href = f'<a href="data:text/csv;base64,{b64}" download="{filename}" style="display: inline-block; background-color: #2563eb; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; margin-top: 10px;">Download Interview (CSV)</a>'
    
    return href

def local_export_chat_history_to_txt(chat_history, candidate_info):
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
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}" style="display: inline-block; background-color: #2563eb; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; margin-top: 10px;">Download Interview (Text)</a>'
    
    return href

def local_show_privacy_notice():
    """Display a simple privacy notice and get consent."""
    st.markdown("<div style='margin-top: 30px; margin-bottom: 20px; font-weight: bold; color: #60a5fa; border-bottom: 1px solid #3b82f6; padding-bottom: 5px;'>Privacy Notice</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #1f2937; border-radius: 10px; padding: 20px; margin: 20px 0; border-left: 4px solid #3b82f6; font-size: 0.9rem;'>
        <h3 style='color: #60a5fa;'>Privacy Notice - TalentScout AI Hiring Assistant</h3>
        
        <p>TalentScout AI collects and processes your personal data to facilitate the hiring process. This notice explains how we handle your information.</p>
        
        <h3 style='color: #60a5fa;'>Data We Collect</h3>
        <ul style='margin-left: 20px;'>
            <li>Basic personal information (name, email, phone number)</li>
            <li>Professional information (experience, skills, position applying for)</li>
            <li>Your responses during the screening conversation</li>
        </ul>
        
        <h3 style='color: #60a5fa;'>How We Use Your Data</h3>
        <ul style='margin-left: 20px;'>
            <li>To assess your suitability for the position</li>
            <li>To generate relevant technical questions</li>
            <li>To provide hiring recommendations to employers</li>
        </ul>
        
        <h3 style='color: #60a5fa;'>Your Data Rights</h3>
        <ul style='margin-left: 20px;'>
            <li>Access your personal data</li>
            <li>Request correction of inaccurate data</li>
            <li>Request deletion of your data</li>
            <li>Export your conversation data</li>
        </ul>
        
        <h3 style='color: #60a5fa;'>Data Retention</h3>
        <p>We retain your data for 6 months after the interview, after which it will be anonymized or deleted.</p>
        
        <h3 style='color: #60a5fa;'>Contact Information</h3>
        <p>For privacy inquiries, please contact: privacy@talentscout.ai</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add checkbox for consent
    consent = st.checkbox("I understand and agree to the processing of my personal data as described above.")
    
    if consent:
        st.session_state.privacy_agreed = True
    
    return consent

def local_handle_conversation(user_input):
    """Basic conversation handler for compatibility mode."""
    current_state = st.session_state.conversation_state
    
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Different behavior based on conversation state
    if current_state == "initial":
        # If this is the first message, assume it's their name
        st.session_state.candidate_info["name"] = user_input
        response = f"Nice to meet you, {user_input}! Could you please provide your email address?"
        st.session_state.conversation_state = "collecting_email"
    
    elif current_state == "collecting_email":
        # Collect email
        if "@" in user_input and "." in user_input:
            st.session_state.candidate_info["email"] = user_input
            response = "Thank you! What's your phone number?"
            st.session_state.conversation_state = "collecting_phone"
        else:
            response = "That doesn't look like a valid email address. Please provide a valid email."
    
    elif current_state == "collecting_phone":
        # Collect phone number (basic check)
        st.session_state.candidate_info["phone"] = user_input
        response = "Great! How many years of experience do you have in your field?"
        st.session_state.conversation_state = "collecting_experience"
    
    elif current_state == "collecting_experience":
        # Collect years of experience
        st.session_state.candidate_info["experience"] = user_input
        response = "What position are you applying for?"
        st.session_state.conversation_state = "collecting_position"
    
    elif current_state == "collecting_position":
        # Collect position
        st.session_state.candidate_info["position"] = user_input
        response = "What is your current location?"
        st.session_state.conversation_state = "collecting_location"
    
    elif current_state == "collecting_location":
        # Collect location
        st.session_state.candidate_info["location"] = user_input
        response = "Please list your technical skills and technologies you're proficient in:"
        st.session_state.conversation_state = "collecting_skills"
    
    elif current_state == "collecting_skills":
        # Collect skills
        st.session_state.candidate_info["tech_stack"] = user_input
        
        # Mark collection as complete
        st.session_state.collection_complete = True
        
        # Summarize the information collected
        summary = f"Thank you for providing your information. I have the following details:\n\n"
        summary += f"- Name: {st.session_state.candidate_info['name']}\n"
        summary += f"- Email: {st.session_state.candidate_info['email']}\n"
        summary += f"- Phone: {st.session_state.candidate_info['phone']}\n"
        summary += f"- Experience: {st.session_state.candidate_info['experience']}\n"
        summary += f"- Position: {st.session_state.candidate_info['position']}\n"
        summary += f"- Location: {st.session_state.candidate_info['location']}\n"
        summary += f"- Skills: {st.session_state.candidate_info['tech_stack']}\n\n"
        summary += "Thank you for completing this initial screening. Our team will review your information and contact you soon."
        
        response = summary
        st.session_state.conversation_state = "completed"
        st.session_state.conversation_ended = True
    
    else:
        # General response for other states
        context = format_chat_history(st.session_state.chat_history[-10:])
        response = get_full_response(f"Respond to this message from a job candidate: '{user_input}'\n\nChat history:\n{context}")
    
    # Add assistant response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# Choose the appropriate function based on whether we're using the modular version
if st.session_state.using_modular_version:
    try:
        from app_improved import display_candidate_profile, export_chat_history_to_csv, export_chat_history_to_txt, show_privacy_notice
    except ImportError:
        display_candidate_profile = local_display_candidate_profile
        export_chat_history_to_csv = local_export_chat_history_to_csv
        export_chat_history_to_txt = local_export_chat_history_to_txt
        show_privacy_notice = local_show_privacy_notice
else:
    display_candidate_profile = local_display_candidate_profile
    export_chat_history_to_csv = local_export_chat_history_to_csv
    export_chat_history_to_txt = local_export_chat_history_to_txt
    show_privacy_notice = local_show_privacy_notice

# Header section with logo
st.markdown("<div style='display: flex; align-items: center; margin-bottom: 20px;'></div>", unsafe_allow_html=True)
try:
    col1, col2 = st.columns([1, 4])
    with col1:
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
                    
                    # Generate custom interview questions based on candidate's skills
                    if st.session_state.collection_complete and 'tech_stack' in st.session_state.candidate_info:
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
                                    
                                    # Use the appropriate function based on availability
                                    if st.session_state.using_modular_version:
                                        questions = skill_assessor.generate_technical_questions(skills, experience, position)
                                    else:
                                        questions = generate_custom_interview_questions(skills, experience, position)
                                    
                                    # Store in session state
                                    st.session_state.custom_questions = questions
                                    st.session_state.custom_questions_generated = True
                                    
                                    # Show the questions
                                    st.markdown(questions)
            else:
                user_input = st.chat_input("Type your message here...", disabled=st.session_state.conversation_ended)
                
                if user_input:
                    # Reset error count on each valid input
                    st.session_state.error_count = 0
                    
                    try:
                        # Use appropriate conversation handler based on availability
                        if st.session_state.using_modular_version:
                            # Add user message to chat history
                            st.session_state.chat_history.append({"role": "user", "content": user_input})
                            
                            # Use the conversation manager to handle
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
                        else:
                            # Use local handler for compatibility mode
                            local_handle_conversation(user_input)
                        
                    except Exception as e:
                        # Handle errors gracefully
                        import traceback
                        traceback.print_exc()
                        
                        st.session_state.error_count += 1
                        error_message = "I apologize, but I encountered a technical issue. Let's continue our conversation."
                        
                        if st.session_state.error_count >= 3:
                            error_message += " If you continue experiencing issues, please try refreshing the page."
                        
                        # Add error response to chat history
                        st.session_state.chat_history.append({"role": "assistant", "content": error_message})
                    
                    # Rerun to update UI
                    st.rerun()

# Footer section with creator's full name highlighted in blue
st.markdown("""
<div class='footer'>
    <div class='footer-content'>
        <span style='color: #9ca3af; margin-right: 5px;'>Created by</span>
        <span class='footer-highlight'>Goddati Bhavyasri</span>
    </div>
</div>
""", unsafe_allow_html=True)