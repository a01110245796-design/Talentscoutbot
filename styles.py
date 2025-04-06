import streamlit as st

def apply_custom_styles():
    """Apply custom styles to the Streamlit app."""
    # Custom CSS for dark theme and professional appearance
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Open+Sans:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Roboto', 'Open Sans', sans-serif;
    }
    
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #ffffff;
        border-color: #4b5563;
        border-radius: 8px;
        padding: 0.6rem;
        font-size: 15px;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #262730;
        color: #ffffff;
        border-color: #4b5563;
        border-radius: 8px;
        font-size: 15px;
    }
    
    .stButton > button {
        background-color: #3b82f6;
        color: #ffffff;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:hover {
        background-color: #2563eb;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Chat message styling */
    .css-1qrvfrg {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        word-wrap: break-word;
        overflow-wrap: break-word;
        max-width: 100%;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    /* Ensure chat messages wrap properly */
    .stChatMessage {
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: normal;
        width: 100%;
        max-width: 800px;
        line-height: 1.6;
    }
    
    /* Style all messages for better readability */
    .stChatMessage p {
        margin-bottom: 0.6rem;
        line-height: 1.6;
    }
    
    /* Accent colors for highlights */
    h1, h2, h3 {
        color: #60a5fa;
        margin-bottom: 0.8rem;
        font-weight: 500;
    }
    
    h1 {
        font-size: 28px;
    }
    
    h2 {
        font-size: 24px;
    }
    
    h3 {
        font-size: 20px;
    }
    
    /* Header logo styling */
    .element-container:has(img) {
        padding: 10px 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Style for the header row */
    .header-row {
        display: flex;
        align-items: center;
        padding: 15px 0;
        border-bottom: 1px solid #374151;
        margin-bottom: 25px;
        background: linear-gradient(to right, #1e293b, #111827);
        border-radius: 10px;
    }
    
    .highlight {
        color: #60a5fa;
        font-weight: bold;
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted #4b5563;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 220px;
        background-color: #374151;
        color: #ffffff;
        text-align: center;
        border-radius: 8px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -110px;
        opacity: 0;
        transition: opacity 0.3s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Container styling */
    .container {
        background-color: #1f2937;
        padding: 1.8rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .container:hover {
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
    }
    
    /* Chat input styling */
    .stChatInput {
        border-color: #4b5563;
        background-color: #262730;
        border-radius: 8px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1f2937;
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4b5563;
        border-radius: 6px;
        border: 2px solid #1f2937;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #60a5fa;
    }
    
    /* Export buttons styling */
    .download-button {
        display: inline-block;
        background-color: #3b82f6;
        color: white;
        padding: 10px 18px;
        margin: 8px;
        border-radius: 8px;
        text-decoration: none;
        font-size: 15px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .download-button:hover {
        background-color: #2563eb;
        text-decoration: none;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .export-container {
        margin-top: 25px;
        padding: 20px;
        background-color: #1f2937;
        border-radius: 12px;
        border: 1px solid #374151;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .custom-questions-container {
        margin-top: 25px;
        padding: 20px;
        background-color: #1f2937;
        border-radius: 12px;
        border: 1px solid #374151;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Candidate Profile Card Styling */
    .candidate-profile-card {
        background: linear-gradient(145deg, #1a2233, #1e293b);
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        border: 1px solid #2d3748;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-in-out;
    }
    
    .candidate-profile-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        border-color: #4a5568;
    }
    
    /* Profile header with name and picture */
    .profile-header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .profile-picture {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background-color: #3b82f6;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        font-weight: bold;
        margin-right: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 2px solid #4b5563;
    }
    
    .profile-info {
        flex: 1;
    }
    
    .profile-name {
        font-size: 22px;
        font-weight: 600;
        color: #fff;
        margin-bottom: 5px;
    }
    
    .profile-position {
        font-size: 16px;
        color: #a3aed0;
        margin-bottom: 5px;
    }
    
    .profile-location {
        font-size: 14px;
        color: #718096;
        display: flex;
        align-items: center;
    }
    
    /* Profile details */
    .profile-details {
        margin-top: 15px;
    }
    
    .detail-row {
        display: flex;
        margin-bottom: 12px;
        align-items: center;
    }
    
    .detail-label {
        min-width: 100px;
        color: #a0aec0;
        font-size: 14px;
    }
    
    .detail-value {
        color: #e2e8f0;
        font-size: 15px;
        flex: 1;
    }
    
    /* Skill tags */
    .skill-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 15px;
    }
    
    .skill-tag {
        background-color: #2d3748;
        color: #60a5fa;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 13px;
        font-weight: 500;
        transition: all 0.2s ease;
        border: 1px solid #4a5568;
    }
    
    .skill-tag:hover {
        background-color: #3b82f6;
        color: white;
        transform: translateY(-2px);
    }
    
    /* Match score indicator */
    .match-score {
        display: flex;
        align-items: center;
        margin-top: 20px;
        padding: 10px;
        background-color: #1a202c;
        border-radius: 8px;
        border: 1px solid #2d3748;
    }
    
    .match-label {
        color: #a0aec0;
        font-size: 14px;
        margin-right: 10px;
        min-width: 100px;
    }
    
    .match-value {
        font-weight: 600;
        font-size: 18px;
        color: #3b82f6;
        margin-right: 15px;
    }
    
    .match-bar-container {
        flex: 1;
        height: 10px;
        background-color: #2d3748;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .match-bar {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
        border-radius: 10px;
        transition: width 1s ease-in-out;
    }
    
    /* Expandable section */
    .expandable-section {
        margin-top: 20px;
        border-top: 1px solid #2d3748;
        padding-top: 15px;
    }
    
    .expandable-header {
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .expandable-title {
        font-size: 16px;
        font-weight: 500;
        color: #e2e8f0;
    }
    
    .expandable-icon {
        transition: transform 0.3s ease;
    }
    
    .expandable-icon.expanded {
        transform: rotate(180deg);
    }
    
    .expandable-content {
        padding: 10px;
        background-color: #1a202c;
        border-radius: 8px;
        margin-top: 10px;
        display: none;
    }
    
    .expandable-content.expanded {
        display: block;
        animation: fadeIn 0.3s ease-in-out;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Section title styling */
    .section-title {
        font-size: 20px;
        font-weight: 500;
        color: #60a5fa;
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid #2d3748;
    }
    
    /* Links styling */
    .profile-link {
        color: #60a5fa;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        margin-right: 15px;
        transition: all 0.2s ease;
    }
    
    .profile-link:hover {
        color: #3b82f6;
        text-decoration: underline;
    }
    
    .profile-link-icon {
        margin-right: 5px;
    }
    
    /* Profile links section */
    .profile-links {
        display: flex;
        margin-top: 15px;
    }
    
    /* Footer styling */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #0e1117;
        padding: 12px;
        text-align: center;
        font-size: 14px;
        color: #7f7f7f;
        border-top: 1px solid #2e3440;
        z-index: 1000;
    }
    
    .footer-content {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .footer-text {
        color: #7f7f7f;
    }
    
    .footer-highlight {
        color: #60a5fa;
        font-weight: 500;
        margin-left: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
