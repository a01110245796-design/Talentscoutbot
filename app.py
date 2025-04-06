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

# Set page configuration
st.set_page_config(
    page_title="TalentScout AI Hiring Assistant",
    page_icon="👨‍💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apply custom styling
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
    
    .candidate-card {
        background-color: #1f2937;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        border-left: 4px solid #3b82f6;
    }
    
    .avatar {
        width: 80px;
        height: 80px;
        background-color: #3b82f6;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        color: white;
        margin-right: 20px;
    }
    
    .skill-tag {
        background-color: #374151;
        color: #d1d5db;
        border-radius: 50px;
        padding: 6px 12px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 4px;
    }
    
    .skill-tag.match {
        background-color: #1e3a8a;
        color: #ffffff;
        border: 1px solid #3b82f6;
    }
    
    .match-bar {
        height: 10px;
        background: linear-gradient(90deg, #2563eb, #60a5fa);
        border-radius: 5px;
        transition: width 1s;
    }
    
    .match-container {
        width: 100%;
        height: 10px;
        background-color: #374151;
        border-radius: 5px;
        overflow: hidden;
    }
    
    .download-button {
        display: inline-block;
        background-color: #2563eb;
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        text-decoration: none;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Import utils from same directory
import utils

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

def get_initials(name):
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

def display_candidate_profile(candidate_info):
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
            match_score, matching_skills = utils.calculate_role_match(tech_stack, experience, position)
        except Exception as e:
            st.error(f"Error calculating match score: {str(e)}")
            matching_skills = []
    else:
        matching_skills = []
    
    # Get candidate initials for avatar
    initials = get_initials(name)
    
    # Create profile card
    st.markdown("<div style='margin-top: 30px; margin-bottom: 20px; font-weight: bold; color: #60a5fa; border-bottom: 1px solid #3b82f6; padding-bottom: 5px;'>Candidate Profile</div>", unsafe_allow_html=True)
    
    # Profile container
    st.markdown(f"""
    <div class="candidate-card">
        <div style='display: flex; align-items: center; margin-bottom: 20px;'>
            <div class="avatar">{initials}</div>
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
            skill_class = "skill-tag match" if skill.lower() in [s.lower() for s in matching_skills] else "skill-tag"
            st.markdown(f"<span class='{skill_class}'>{skill}</span>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Match score indicator
    st.markdown(f"""
    <div style='margin-bottom: 20px;'>
        <div style='font-size: 1rem; font-weight: 500; margin-bottom: 5px; color: #d1d5db;'>Role Match</div>
        <div style='font-size: 1.2rem; font-weight: bold; color: #3b82f6; margin-bottom: 5px;'>{match_score}%</div>
        <div class="match-container">
            <div class="match-bar" style='width: {match_score}%;'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Close profile card
    st.markdown("</div>", unsafe_allow_html=True)

def export_chat_history_to_csv(chat_history, candidate_info):
    """Export the chat history to CSV format."""
    return utils.export_chat_history_to_csv(chat_history, candidate_info)

def export_chat_history_to_txt(chat_history, candidate_info):
    """Export the chat history to text format."""
    return utils.export_chat_history_to_txt(chat_history, candidate_info)

def show_privacy_notice():
    """Display a simple privacy notice and get consent."""
    st.markdown("""
    ## Privacy Notice
    
    TalentScout AI collects and processes candidate information for recruitment purposes only. 
    By continuing, you agree to the collection and processing of your personal information.
    
    ### Information We Collect:
    - Your name, contact details, and location
    - Professional experience and technical skills
    - Your responses during this conversation
    
    ### How We Use This Information:
    - To assess your suitability for the position
    - To generate personalized interview questions
    - To provide hiring managers with initial screening results
    
    Your information will be stored securely and will not be shared with third parties.
    """)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("I Agree", type="primary"):
            st.session_state.privacy_agreed = True
            return True
    
    return False

def handle_conversation(user_input):
    """Basic conversation handler."""
    current_state = st.session_state.conversation_state
    
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Different behavior based on conversation state
    if current_state == "initial":
        # If this is the first message, assume it's their name
        st.session_state.candidate_info["name"] = user_input
        response = f"Nice to meet you, {user_input}! I'm TalentScout, an AI hiring assistant. Could you please provide your email address for our records?"
        st.session_state.conversation_state = "asking_email"
    
    elif current_state == "asking_email":
        # Validate and store email
        is_valid, value_or_error = utils.validate_input("email", user_input)
        if is_valid:
            st.session_state.candidate_info["email"] = value_or_error
            response = "Great! Now, could you please share your phone number?"
            st.session_state.conversation_state = "asking_phone"
        else:
            response = f"{value_or_error} Could you please provide a valid email address?"
    
    elif current_state == "asking_phone":
        # Validate and store phone
        is_valid, value_or_error = utils.validate_input("phone", user_input)
        if is_valid:
            st.session_state.candidate_info["phone"] = value_or_error
            response = "Thank you! How many years of professional experience do you have in your field?"
            st.session_state.conversation_state = "asking_experience"
        else:
            response = f"{value_or_error} Could you please provide a valid phone number?"
    
    elif current_state == "asking_experience":
        # Validate and store experience
        is_valid, value_or_error = utils.validate_input("experience", user_input)
        if is_valid:
            st.session_state.candidate_info["experience"] = value_or_error
            response = "Thanks for sharing your experience. What position are you applying for?"
            st.session_state.conversation_state = "asking_position"
        else:
            response = f"{value_or_error} Could you please provide your years of experience as a number?"
    
    elif current_state == "asking_position":
        # Store position
        st.session_state.candidate_info["position"] = user_input
        response = "Where are you located or willing to work? (city, remote, etc.)"
        st.session_state.conversation_state = "asking_location"
    
    elif current_state == "asking_location":
        # Store location
        st.session_state.candidate_info["location"] = user_input
        response = "Could you list your key technical skills or tech stack? (e.g., Python, React, AWS)"
        st.session_state.conversation_state = "asking_tech_stack"
    
    elif current_state == "asking_tech_stack":
        # Store tech stack
        st.session_state.candidate_info["tech_stack"] = user_input
        
        # Indicate that we've collected all required information
        st.session_state.collection_complete = True
        
        # Craft a personalized response based on collected information
        name = st.session_state.candidate_info.get("name", "")
        position = st.session_state.candidate_info.get("position", "the position")
        
        response = f"Thank you, {name}! We've completed the initial screening for {position}. "
        response += "I've prepared a summary of your profile, and our team will review your information. "
        response += "Is there anything specific you'd like to know about the next steps in the hiring process?"
        
        # Move to open conversation mode where we use the LLM
        st.session_state.conversation_state = "open_conversation"
    
    elif current_state == "open_conversation":
        # Use the API for open-ended conversation
        conversation_context = utils.format_chat_history(st.session_state.chat_history[-5:])
        prompt = f"""
        The candidate's name is {st.session_state.candidate_info.get('name')}.
        They are applying for a {st.session_state.candidate_info.get('position')} position.
        They have {st.session_state.candidate_info.get('experience')} years of experience.
        Their skills include: {st.session_state.candidate_info.get('tech_stack')}.
        
        Recent conversation:
        {conversation_context}
        
        The candidate just said: "{user_input}"
        
        Respond as a professional AI hiring assistant. If they ask about next steps,
        explain that their profile will be reviewed and they'll be contacted for a follow-up interview if selected.
        If they want to end the conversation, thank them and confirm the conversation is complete.
        """
        
        response = utils.get_full_response(prompt)
        
        # Check if the conversation should end
        end_phrases = [
            "thank you for your time",
            "have a great day",
            "goodbye",
            "bye",
            "end",
            "exit"
        ]
        
        if any(phrase in user_input.lower() for phrase in end_phrases):
            response += "\n\nThank you for completing this screening. Your profile has been saved, and our team will contact you if there's a match!"
            st.session_state.conversation_ended = True
    
    else:
        # Fallback for unknown states
        response = "I'm sorry, there was an issue with our conversation flow. Could we restart the interview process?"
        st.session_state.conversation_state = "initial"
    
    # Add assistant response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": response})

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
                                    
                                    questions = utils.generate_custom_interview_questions(skills, experience, position)
                                    
                                    # Store in session state
                                    st.session_state.custom_questions = questions
                                    st.session_state.custom_questions_generated = True
                                    
                                    # Show the questions
                                    st.markdown(questions)
            else:
                user_input = st.chat_input("Type your message here...", disabled=st.session_state.conversation_ended)
                
                if user_input:
                    # Process the user input
                    try:
                        handle_conversation(user_input)
                        # Rerun to update UI
                        st.rerun()
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        
                        st.session_state.error_count += 1
                        error_message = "I apologize, but I encountered a technical issue. Let's continue our conversation."
                        
                        if st.session_state.error_count >= 3:
                            error_message += " If you continue experiencing issues, please try refreshing the page."
                        
                        # Add error response to chat history
                        st.session_state.chat_history.append({"role": "assistant", "content": error_message})
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