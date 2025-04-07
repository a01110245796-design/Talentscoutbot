"""
Styles for TalentScout AI Hiring Assistant
This module contains custom styles for the Streamlit app.
"""

import streamlit as st

def apply_custom_styles():
    """Apply custom styles to the Streamlit app."""
    st.markdown("""
    <style>
        /* Main application theme */
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        
        /* Navigation and header styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #1e293b;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #3b82f6;
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
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .footer-highlight {
            color: #60a5fa;
            font-weight: bold;
            margin-left: 5px;
        }
        
        /* Candidate profile card styling */
        .section-title {
            margin-top: 30px;
            margin-bottom: 20px;
            font-weight: bold;
            color: #60a5fa;
            border-bottom: 1px solid #3b82f6;
            padding-bottom: 5px;
        }
        
        .candidate-profile-card {
            background-color: #1f2937;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #3b82f6;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .candidate-profile-card:hover {
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
            transform: translateY(-2px);
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
        
        .detail-label {
            flex: 1;
            font-weight: 500;
            color: #9ca3af;
        }
        
        .detail-value {
            flex: 2;
        }
        
        /* Skills and tags styling */
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
        
        /* Match score indicator */
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
        
        /* Download buttons */
        .download-button {
            display: inline-block;
            background-color: #2563eb;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            text-decoration: none;
            margin-top: 10px;
            transition: background-color 0.3s ease;
        }
        
        .download-button:hover {
            background-color: #1d4ed8;
        }
        
        /* Chat container styling */
        .chat-container {
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        /* Override Streamlit's default chat styling */
        .stChatMessage {
            background-color: #1f2937;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        }
        
        .stChatMessageContent {
            color: #e5e7eb;
            font-size: 16px;
            line-height: 1.6;
        }
        
        /* Input area styling */
        .stTextInput>div>div>input {
            background-color: #1f2937;
            border: 1px solid #374151;
            color: #e5e7eb;
            border-radius: 8px;
            padding: 10px 15px;
        }
        
        .stTextInput>div>div>input:focus {
            border-color: #3b82f6;
        }
        
        /* Button styling */
        .stButton>button {
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: #1d4ed8;
            transform: translateY(-2px);
        }
        
        /* Primary button (used for important actions) */
        .stButton button[data-baseweb="button"][kind="primary"] {
            background-color: #2563eb;
        }
        
        /* Privacy notice styling */
        .privacy-notice {
            background-color: #1f2937;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #3b82f6;
        }
        
        .privacy-notice h2 {
            color: #60a5fa;
            margin-bottom: 15px;
        }
        
        .privacy-notice h3 {
            color: #60a5fa;
            font-size: 1rem;
            margin-top: 15px;
            margin-bottom: 5px;
        }
        
        .privacy-notice ul {
            margin-left: 20px;
        }
    </style>
    """, unsafe_allow_html=True)