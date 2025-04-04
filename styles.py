import streamlit as st

def apply_custom_styles():
    """Apply custom styles to the Streamlit app."""
    # Custom CSS for dark theme and professional appearance
    st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #ffffff;
        border-color: #4b5563;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #262730;
        color: #ffffff;
        border-color: #4b5563;
    }
    
    .stButton > button {
        background-color: #3b82f6;
        color: #ffffff;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
    }
    
    .stButton > button:hover {
        background-color: #2563eb;
    }
    
    /* Chat message styling */
    .css-1qrvfrg {
        background-color: #1e293b;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 0.5rem;
        word-wrap: break-word;
        overflow-wrap: break-word;
        max-width: 100%;
    }
    
    /* Ensure chat messages wrap properly */
    .stChatMessage {
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: normal;
        width: 100%;
        max-width: 800px;
    }
    
    /* Style all messages for better readability */
    .stChatMessage p {
        margin-bottom: 0.5rem;
        line-height: 1.5;
    }
    
    /* Accent colors for highlights */
    h1, h2, h3 {
        color: #60a5fa;
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
        margin-bottom: 20px;
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
        width: 200px;
        background-color: #374151;
        color: #ffffff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Container styling */
    .container {
        background-color: #1f2937;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Chat input styling */
    .stChatInput {
        border-color: #4b5563;
        background-color: #262730;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1f2937;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4b5563;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #60a5fa;
    }
    </style>
    """, unsafe_allow_html=True)
