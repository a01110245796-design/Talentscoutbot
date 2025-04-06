import streamlit as st

def apply_custom_styles():
    """Apply custom styles to the Streamlit app."""
    # Define custom CSS for improved dark theme
    custom_css = """
    <style>
        /* General app styling */
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        
        /* Header styling */
        .header-row {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        
        /* Chat interface styling */
        .stChatMessage {
            background-color: #1f2937;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            max-width: 90%;
        }
        
        .stChatMessage.user {
            background-color: #1e3a8a;
            margin-left: auto;
            margin-right: 10px;
        }
        
        .stChatMessage.assistant {
            background-color: #374151;
            margin-right: auto;
            margin-left: 10px;
        }
        
        /* Section title styling */
        .section-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin: 20px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 1px solid #3b82f6;
            color: #60a5fa;
        }
        
        /* Footer styling */
        .footer {
            position: relative;
            bottom: 0;
            width: 100%;
            text-align: center;
            padding: 20px 0;
            margin-top: 40px;
            border-top: 1px solid #2d3748;
        }
        
        .footer-content {
            display: inline-block;
        }
        
        .footer-text {
            color: #9ca3af;
            margin-right: 5px;
        }
        
        .footer-highlight {
            color: #60a5fa;
            font-weight: bold;
        }
        
        /* Candidate profile card styling */
        .candidate-profile-card {
            background-color: #1f2937;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
            border-left: 4px solid #3b82f6;
        }
        
        .profile-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .profile-picture {
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
        
        .profile-info {
            flex: 1;
        }
        
        .profile-name {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 5px;
            color: #f9fafb;
        }
        
        .profile-position {
            font-size: 1rem;
            color: #d1d5db;
            margin-bottom: 5px;
        }
        
        .profile-location {
            font-size: 0.9rem;
            color: #9ca3af;
        }
        
        .profile-details {
            margin-bottom: 20px;
        }
        
        .detail-row {
            display: flex;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #374151;
        }
        
        .detail-row:last-child {
            border-bottom: none;
        }
        
        .detail-label {
            flex: 1;
            font-weight: 500;
            color: #9ca3af;
        }
        
        .detail-value {
            flex: 2;
            color: #f9fafb;
        }
        
        /* Skill tags styling */
        .skill-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }
        
        .skill-tag {
            background-color: #374151;
            color: #d1d5db;
            border-radius: 50px;
            padding: 6px 12px;
            font-size: 0.85rem;
            display: inline-block;
        }
        
        .skill-tag.match {
            background-color: #1e3a8a;
            color: #ffffff;
            border: 1px solid #3b82f6;
        }
        
        /* Match score styling */
        .match-score {
            margin-bottom: 20px;
        }
        
        .match-label {
            font-size: 1rem;
            font-weight: 500;
            margin-bottom: 5px;
            color: #d1d5db;
        }
        
        .match-value {
            font-size: 1.2rem;
            font-weight: bold;
            color: #3b82f6;
            margin-bottom: 5px;
        }
        
        .match-bar-container {
            width: 100%;
            height: 10px;
            background-color: #374151;
            border-radius: 5px;
            overflow: hidden;
        }
        
        .match-bar {
            height: 100%;
            background: linear-gradient(90deg, #2563eb, #60a5fa);
            border-radius: 5px;
            transition: width 1s ease-in-out;
        }
        
        /* Profile links styling */
        .profile-links {
            display: flex;
            gap: 15px;
            margin-top: 15px;
        }
        
        .profile-link {
            color: #60a5fa;
            text-decoration: none;
            display: flex;
            align-items: center;
            font-size: 0.9rem;
        }
        
        .profile-link-icon {
            margin-right: 5px;
        }
        
        /* Export button styling */
        .export-container {
            margin: 20px 0;
            padding: 20px;
            background-color: #1f2937;
            border-radius: 10px;
            border-left: 4px solid #3b82f6;
        }
        
        .download-button {
            display: inline-block;
            background-color: #2563eb;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            text-decoration: none;
            margin-top: 10px;
            transition: background-color 0.3s;
        }
        
        .download-button:hover {
            background-color: #1d4ed8;
        }
        
        /* Custom questions container */
        .custom-questions-container {
            margin: 20px 0;
            padding: 20px;
            background-color: #1f2937;
            border-radius: 10px;
            border-left: 4px solid #3b82f6;
        }
        
        /* Privacy notice styling */
        .privacy-notice {
            background-color: #1f2937;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #3b82f6;
            font-size: 0.9rem;
            color: #d1d5db;
        }
        
        .privacy-notice h3 {
            color: #60a5fa;
            margin-top: 15px;
        }
        
        .privacy-notice ul {
            margin-left: 20px;
        }
        
        /* Chat input styling */
        .stChatInputContainer {
            margin-top: 20px;
        }
    </style>
    """
    
    # Apply the custom CSS
    st.markdown(custom_css, unsafe_allow_html=True)