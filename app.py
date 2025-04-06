import streamlit as st
import requests
import json
import time
import os
import random

# Debug print statements
print("Starting TalentScout AI Hiring Assistant...")
print(f"Running on Python version: {os.sys.version}")
print(f"Current working directory: {os.getcwd()}")
from utils import (
    validate_input, 
    format_chat_history, 
    get_full_response, 
    export_chat_history_to_csv, 
    export_chat_history_to_txt,
    generate_custom_interview_questions,
    calculate_role_match,
    get_initials
)
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

def display_candidate_profile(candidate_info):
    """Display a rich candidate profile card with avatar, info, and match score.
    
    Parameters:
    - candidate_info: Dictionary containing candidate information
    """
    # Get candidate information
    name = candidate_info.get('name', 'Candidate')
    position = candidate_info.get('position', 'Role not specified')
    experience = candidate_info.get('experience', '0')
    location = candidate_info.get('location', 'Location not specified')
    tech_stack = candidate_info.get('tech_stack', '')
    
    # Calculate match score and get relevant skills
    match_score, matching_skills = calculate_role_match(tech_stack, experience, position)
    
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
        st.markdown(f"""
        <div class='detail-row'>
            <div class='detail-label'>📧 Email</div>
            <div class='detail-value'>{candidate_info.get('email')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    if candidate_info.get('phone'):
        st.markdown(f"""
        <div class='detail-row'>
            <div class='detail-label'>📱 Phone</div>
            <div class='detail-value'>{candidate_info.get('phone')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # End profile details
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Skills section - extract skills from tech_stack and display as tags
    if tech_stack:
        # Extract individual skills (split by commas, spaces, etc.)
        skills = [skill.strip() for skill in tech_stack.replace(',', ' ').split() if skill.strip()]
        
        # Highlight matching skills
        st.markdown("<div class='skill-tags'>", unsafe_allow_html=True)
        for skill in skills:
            skill_class = "skill-tag match" if skill.lower() in [s.lower() for s in matching_skills] else "skill-tag"
            st.markdown(f"<span class='{skill_class}'>{skill}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Match score indicator
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
    
    # Expandable content section for resume summary with interactive functionality
    resume_expander = st.expander("Resume Summary")
    with resume_expander:
        st.markdown("This is a placeholder for the candidate's resume summary, which would typically include a brief overview of their career, key achievements, and professional goals.")
    
    # Close profile card
    st.markdown("</div>", unsafe_allow_html=True)

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
if "custom_questions" not in st.session_state:
    st.session_state.custom_questions = ""
if "custom_questions_generated" not in st.session_state:
    st.session_state.custom_questions_generated = False

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
    # Display chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            # Use a static greeting to avoid API call on initial load
            static_greeting = "Welcome to TalentScout AI! I'm your hiring assistant, here to help with the initial screening process. To get started, could you please tell me your full name?"
            st.session_state.chat_history.append({"role": "assistant", "content": static_greeting})
            # Log a message to help with debugging
            print("Initialized chat with static greeting to avoid initial API call")
        
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
                        st.markdown("### Recommended Interview Questions")
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
                                
                                # Generate questions
                                questions = generate_custom_interview_questions(skills, experience, position)
                                
                                # Store in session state
                                st.session_state.custom_questions = questions
                                st.session_state.custom_questions_generated = True
                                
                                # Display the questions
                                st.markdown("### Recommended Interview Questions")
                                st.markdown(questions)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
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
                            confirmation_message = f"Thank you for your information. I have: Name: {st.session_state.candidate_info['name']}, Email: {st.session_state.candidate_info['email']}, Phone: {st.session_state.candidate_info['phone']}, Experience: {st.session_state.candidate_info['experience']} years, Position: {st.session_state.candidate_info['position']}, Location: {st.session_state.candidate_info['location']}, Tech Stack: {st.session_state.candidate_info['tech_stack']}. Now I'll ask a few technical questions."
                            st.session_state.chat_history.append({"role": "assistant", "content": confirmation_message})
                            
                            # Generate technical questions
                            tech_stack = st.session_state.candidate_info['tech_stack']
                            experience = st.session_state.candidate_info['experience']
                            prompt = TECH_QUESTIONS_PROMPT.format(tech_stack=tech_stack, experience=experience)
                            
                            with st.spinner("Generating technical questions based on your profile..."):
                                try:
                                    questions = get_full_response(prompt)
                                    # Check if we got the error message
                                    if "API key" in questions:
                                        # Fallback to static questions
                                        print("Using fallback static questions due to API issues")
                                        skills = tech_stack.lower()
                                        if "python" in skills:
                                            questions = """
                                            1. Explain Python's GIL and its impact on multithreaded applications.
                                            2. How would you optimize a slow-performing Python script?
                                            3. Describe how you've implemented error handling in a recent Python project.
                                            4. What's your approach to testing Python code?
                                            5. Tell me about a challenging Python project you worked on.
                                            """
                                        elif "javascript" in skills or "react" in skills or "angular" in skills or "vue" in skills:
                                            questions = """
                                            1. Explain closure in JavaScript and provide a practical example.
                                            2. How do you handle state management in complex front-end applications?
                                            3. Describe your experience with asynchronous programming.
                                            4. What's your approach to optimizing web performance?
                                            5. Tell me about a challenging front-end issue you solved recently.
                                            """
                                        else:
                                            questions = """
                                            1. Describe your approach to learning new technologies quickly.
                                            2. How do you ensure code quality in your projects?
                                            3. Tell me about a challenging technical problem you solved recently.
                                            4. How do you handle tight deadlines while maintaining code quality?
                                            5. What's your experience with collaboration tools and processes?
                                            """
                                except Exception as e:
                                    print(f"Error generating questions: {str(e)}")
                                    # Fallback questions if API fails
                                    questions = """
                                    1. Tell me about your experience with the technologies you've mentioned.
                                    2. How do you approach learning new technologies or frameworks?
                                    3. Describe a challenging project you worked on recently.
                                    4. How do you ensure code quality in your work?
                                    5. What's your preferred development methodology and why?
                                    """
                                
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

# Footer section with creator's full name
st.markdown("""
<div class='footer'>
    <div class='footer-content'>
        <span class='footer-text'>Created by</span>
        <span class='footer-highlight'>Goddati Bhavyasri</span>
    </div>
</div>
""", unsafe_allow_html=True)
