import streamlit as st
import requests
import json
import time
import os
from utils import validate_input, format_chat_history, get_full_response
from styles import apply_custom_styles
from prompts import (
    INITIAL_GREETING_PROMPT,
    TECH_QUESTIONS_PROMPT,
    CONTEXT_PROMPT,
    GENERAL_FALLBACK_PROMPT,
    COMPLETION_PROMPT
)

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
if "questions_generated" not in st.session_state:
    st.session_state.questions_generated = False
if "conversation_ended" not in st.session_state:
    st.session_state.conversation_ended = False
if "current_field" not in st.session_state:
    st.session_state.current_field = "name"

# Header section with logo
try:
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("assets/logo.svg", width=100)
    with col2:
        st.title("TalentScout AI Hiring Assistant")
        st.subheader("Initial Candidate Screening")
except Exception as e:
    st.title("TalentScout AI Hiring Assistant")
    st.subheader("Initial Candidate Screening")

# Main app container
main_container = st.container()
with main_container:
    # Display chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            # Initialize with greeting
            assistant_greeting = get_full_response(INITIAL_GREETING_PROMPT)
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_greeting})
        
        # Display chat messages
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant", avatar="👨‍💼").write(message["content"])
    
    # User input section
    input_container = st.container()
    with input_container:
        # Process different stages of conversation
        if st.session_state.conversation_ended:
            st.info("Thank you for completing the initial screening. Our hiring team will review your information and contact you soon!")
        else:
            user_input = st.chat_input("Type your message here...", disabled=st.session_state.conversation_ended)
            
            if user_input:
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # Handle information collection if not complete
                if not st.session_state.collection_complete:
                    field = st.session_state.current_field
                    is_valid, message = validate_input(field, user_input)
                    
                    if is_valid:
                        st.session_state.candidate_info[field] = user_input
                        
                        # Move to next field
                        fields = ["name", "email", "phone", "experience", "position", "location", "tech_stack"]
                        current_index = fields.index(field)
                        
                        if current_index < len(fields) - 1:
                            st.session_state.current_field = fields[current_index + 1]
                            field_prompts = {
                                "email": f"Thank you, {st.session_state.candidate_info['name']}! Could you please provide your email address?",
                                "phone": "Great! Now, what's your phone number?",
                                "experience": "How many years of experience do you have in your field?",
                                "position": "What position are you applying for?",
                                "location": "What is your current location?",
                                "tech_stack": "Please list your tech stack (programming languages, frameworks, databases, tools you're proficient in):"
                            }
                            
                            next_field = fields[current_index + 1]
                            st.session_state.chat_history.append({"role": "assistant", "content": field_prompts[next_field]})
                        else:
                            # All information collected
                            st.session_state.collection_complete = True
                            confirmation_message = f"""
                            Thank you for providing your information. Here's what I have:
                            
                            - Name: {st.session_state.candidate_info['name']}
                            - Email: {st.session_state.candidate_info['email']}
                            - Phone: {st.session_state.candidate_info['phone']}
                            - Experience: {st.session_state.candidate_info['experience']} years
                            - Position: {st.session_state.candidate_info['position']}
                            - Location: {st.session_state.candidate_info['location']}
                            - Tech Stack: {st.session_state.candidate_info['tech_stack']}
                            
                            Now, I'll ask you a few technical questions based on your tech stack to understand your expertise better.
                            """
                            st.session_state.chat_history.append({"role": "assistant", "content": confirmation_message})
                            
                            # Generate technical questions
                            tech_stack = st.session_state.candidate_info['tech_stack']
                            experience = st.session_state.candidate_info['experience']
                            prompt = TECH_QUESTIONS_PROMPT.format(tech_stack=tech_stack, experience=experience)
                            
                            with st.spinner("Generating technical questions based on your profile..."):
                                questions = get_full_response(prompt)
                                st.session_state.chat_history.append({"role": "assistant", "content": questions})
                                st.session_state.questions_generated = True
                    else:
                        # Invalid input
                        st.session_state.chat_history.append({"role": "assistant", "content": message})
                
                # Handle conversation after information collection
                elif st.session_state.collection_complete:
                    # Prepare conversation context
                    formatted_history = format_chat_history(st.session_state.chat_history[-10:])
                    candidate_info = st.session_state.candidate_info
                    
                    # Check if this is the end of the conversation
                    if "thank you" in user_input.lower() or "goodbye" in user_input.lower() or "bye" in user_input.lower():
                        prompt = COMPLETION_PROMPT.format(
                            name=candidate_info["name"],
                            position=candidate_info["position"],
                            chat_history=formatted_history
                        )
                        response = get_full_response(prompt)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                        st.session_state.conversation_ended = True
                    else:
                        # Continue conversation with context
                        prompt = CONTEXT_PROMPT.format(
                            name=candidate_info["name"],
                            experience=candidate_info["experience"],
                            position=candidate_info["position"],
                            tech_stack=candidate_info["tech_stack"],
                            chat_history=formatted_history,
                            user_message=user_input
                        )
                        
                        # Handle unexpected inputs with fallback
                        try:
                            response = get_full_response(prompt)
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
                        except Exception as e:
                            fallback_response = get_full_response(GENERAL_FALLBACK_PROMPT.format(
                                name=candidate_info["name"],
                                user_message=user_input
                            ))
                            st.session_state.chat_history.append({"role": "assistant", "content": fallback_response})
                
                # Rerun to update UI
                st.rerun()

# Footer section
st.markdown("""
<div style='position: fixed; bottom: 0; left: 0; width: 100%; background-color: #0e1117; padding: 10px; text-align: center; font-size: 12px; color: #7f7f7f;'>
    Created by Goddati bhavyasri
</div>
""", unsafe_allow_html=True)
