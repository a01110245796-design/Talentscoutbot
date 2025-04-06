"""
Conversation Management Service for TalentScout AI

This module handles conversation flow, context management, and 
intelligent fallback strategies for the chatbot.
"""

import re
import json
import logging
import os
import time
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

from models.llm_service import llm_service
from utils.security import input_sanitizer, gdpr_compliance
from config.settings import get_config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConversationManager:
    """Advanced conversation management with context awareness and intelligent fallbacks."""
    
    def __init__(self):
        """Initialize the conversation manager."""
        self.conversation_states = {
            "initial": {
                "next_states": ["data_collection", "general_chat"],
                "required_fields": []
            },
            "data_collection": {
                "next_states": ["technical_assessment", "general_chat"],
                "required_fields": ["name", "email", "phone", "experience", "position", "tech_stack"]
            },
            "technical_assessment": {
                "next_states": ["feedback", "general_chat"],
                "required_fields": []
            },
            "feedback": {
                "next_states": ["completion", "general_chat"],
                "required_fields": []
            },
            "completion": {
                "next_states": ["follow_up", "general_chat"],
                "required_fields": []
            },
            "follow_up": {
                "next_states": ["general_chat"],
                "required_fields": []
            },
            "general_chat": {
                "next_states": ["initial", "data_collection", "technical_assessment", "feedback", "completion"],
                "required_fields": []
            }
        }
        
        self.field_prompts = {
            "name": "Welcome to TalentScout AI! I'm your hiring assistant, here to help with the initial screening process. To get started, could you please tell me your full name?",
            "email": "Thank you, {name}! Could you please provide your email address?",
            "phone": "Great! Now, what's your phone number?",
            "experience": "How many years of experience do you have in your field?",
            "position": "What position are you applying for?",
            "location": "What is your current location?",
            "tech_stack": "Please list your tech stack (programming languages, frameworks, databases, tools you're proficient in):"
        }
        
        # Patterns for identifying user intent
        self.intent_patterns = {
            "greeting": [
                r"(?i)^(hi|hello|hey|greetings|howdy)[\s\.,!]*$",
                r"(?i)^good\s(morning|afternoon|evening|day)[\s\.,!]*$"
            ],
            "goodbye": [
                r"(?i)^(bye|goodbye|see\syou|farewell)[\s\.,!]*$",
                r"(?i)^(end|finish|complete)\s(chat|conversation|interview)[\s\.,!]*$"
            ],
            "help": [
                r"(?i)^(help|assist|guidance|support|how\s.+\swork)[\s\.,?!]*$",
                r"(?i)^what\scan\syou\sdo[\s\.,?!]*$",
                r"(?i)^how\s(does\sthis|do\syou)\swork[\s\.,?!]*$"
            ],
            "restart": [
                r"(?i)^(restart|start\sover|reset|begin\sagain)[\s\.,!]*$"
            ],
            "gibberish": [
                r"^[a-z]{1,2}$",  # Single or double letter
                r"^[a-z]{20,}$",  # Very long single word
                r"^[\W_]+$",      # Only symbols
                r"(.)\1{4,}"      # Repeated character (aaaaa)
            ]
        }
    
    def detect_intent(self, user_input: str) -> str:
        """Detect user intent from input text."""
        sanitized_input = input_sanitizer.sanitize_input(user_input)
        
        # Check against intent patterns
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, sanitized_input):
                    logger.info(f"Detected intent: {intent} from input: {sanitized_input[:20]}...")
                    return intent
        
        return "unknown"
    
    def is_valid_input_for_state(self, current_state: str, field: str, value: str) -> Tuple[bool, str]:
        """Validate input based on current state and field requirements."""
        # Special handling for data collection state
        if current_state == "data_collection":
            return input_sanitizer.validate_input_safe(field, value)
        
        # For other states, use basic validation
        sanitized = input_sanitizer.sanitize_input(value)
        if not sanitized.strip():
            return False, "Please provide a valid response."
        
        return True, sanitized
    
    def get_next_state(self, current_state: str, candidate_info: Dict[str, str], 
                       user_input: str = None) -> Tuple[str, str]:
        """
        Determine the next conversation state based on current state and user input.
        
        Returns:
            Tuple of (next_state, next_prompt)
        """
        # Check if all required fields for current state are complete
        required_fields = self.conversation_states[current_state]["required_fields"]
        all_required_complete = all(field in candidate_info and candidate_info[field] for field in required_fields)
        
        # Data collection state: move through fields sequentially
        if current_state == "data_collection":
            fields = ["name", "email", "phone", "experience", "position", "location", "tech_stack"]
            
            # Find the first missing field
            for field in fields:
                if field not in candidate_info or not candidate_info[field]:
                    # Get the prompt for this field
                    prompt = self.field_prompts[field]
                    # Format with available info
                    if "{name}" in prompt and "name" in candidate_info:
                        prompt = prompt.format(name=candidate_info["name"])
                    return current_state, prompt
            
            # If all fields are complete, move to technical assessment
            if all_required_complete:
                confirmation = f"Thank you for your information. I have: Name: {candidate_info['name']}, Email: {candidate_info['email']}, Phone: {candidate_info['phone']}, Experience: {candidate_info['experience']} years, Position: {candidate_info['position']}"
                if "location" in candidate_info:
                    confirmation += f", Location: {candidate_info['location']}"
                confirmation += f", Tech Stack: {candidate_info['tech_stack']}. Now I'll ask a few technical questions."
                
                return "technical_assessment", confirmation
        
        # Handle intent-based transitions
        if user_input:
            intent = self.detect_intent(user_input)
            
            if intent == "greeting" and current_state != "initial":
                return current_state, "Hello again! Let's continue with the screening process."
            
            elif intent == "help":
                help_message = "I'm TalentScout AI, your hiring assistant. I'll guide you through the screening process by asking about your background, experience, and skills. Just answer each question as it comes up. If you need to correct any information, just let me know."
                return current_state, help_message
            
            elif intent == "restart":
                return "initial", "I've reset our conversation. Let's start again. Could you please tell me your full name?"
            
            elif intent == "goodbye" and current_state != "completion":
                return "completion", "Thank you for your time today. Your application has been recorded. Our hiring team will review your information and contact you within 5-7 business days."
            
            elif intent == "gibberish":
                return current_state, "I didn't quite understand that. Could you please provide a clearer response? We're currently discussing your job application."
        
        # Default transitions
        if all_required_complete:
            possible_next_states = self.conversation_states[current_state]["next_states"]
            if "technical_assessment" in possible_next_states and current_state == "data_collection":
                return "technical_assessment", "Now I'll ask you some technical questions based on your experience and skills."
            elif "feedback" in possible_next_states and current_state == "technical_assessment":
                return "feedback", "Thank you for your responses to the technical questions. Your answers will help us evaluate your fit for this role."
            elif "completion" in possible_next_states:
                return "completion", "Thank you for completing this screening. Our team will review your application and contact you soon."
        
        # Stay in current state if no clear transition
        return current_state, None
    
    def format_chat_history(self, messages: List[Dict[str, str]], max_context: int = 10) -> str:
        """Format chat history for prompt context with truncation."""
        # Take only the most recent messages to avoid context overflow
        recent_messages = messages[-max_context:] if len(messages) > max_context else messages
        
        formatted = ""
        for msg in recent_messages:
            speaker = "User" if msg["role"] == "user" else "Assistant"
            # Truncate very long messages
            content = msg["content"]
            if len(content) > 200:
                content = content[:197] + "..."
            formatted += f"{speaker}: {content}\n\n"
        
        return formatted
    
    def handle_user_message(self, user_message: str, chat_history: List[Dict[str, str]], 
                           candidate_info: Dict[str, str], current_state: str) -> Tuple[str, str]:
        """
        Process a user message and generate appropriate response.
        
        Returns:
            Tuple of (assistant_response, new_state)
        """
        # Sanitize input
        sanitized_message = input_sanitizer.sanitize_input(user_message)
        
        # Detect intent
        intent = self.detect_intent(sanitized_message)
        logger.info(f"Processing message with intent '{intent}' in state '{current_state}'")
        
        # Handle special intents
        if intent == "gibberish":
            return self.get_fallback_response(sanitized_message, candidate_info, current_state), current_state
        
        # If in data collection, handle field-specific validation
        if current_state == "data_collection":
            # Determine which field we're collecting
            fields = ["name", "email", "phone", "experience", "position", "location", "tech_stack"]
            current_field = None
            
            for field in fields:
                if field not in candidate_info or not candidate_info[field]:
                    current_field = field
                    break
            
            if current_field:
                # Validate the input for this field
                is_valid, message = self.is_valid_input_for_state(current_state, current_field, sanitized_message)
                
                if not is_valid:
                    return message, current_state
                
                # Update candidate info with valid input
                candidate_info[current_field] = message
                
                # Get next state and prompt
                next_state, next_prompt = self.get_next_state(current_state, candidate_info)
                
                if next_prompt:
                    return next_prompt, next_state
        
        # For other states or if no specific handling, use the LLM
        context_prompt = f"""
        Current conversation state: {current_state}
        Candidate: {candidate_info.get('name', 'Unnamed candidate')}
        Position: {candidate_info.get('position', 'Unspecified position')}
        Experience: {candidate_info.get('experience', 'Unknown')} years
        Tech stack: {candidate_info.get('tech_stack', 'Not specified')}
        
        Recent conversation:
        {self.format_chat_history(chat_history)}
        
        Latest message: "{sanitized_message}"
        
        Respond as TalentScout AI, a professional hiring assistant. Keep your response concise (under 75 words),
        focused on screening for the position, and maintain a professional tone.
        """
        
        # Generate response using LLM
        response, metadata = llm_service.generate_response(
            prompt=context_prompt,
            task_type="screening" if current_state != "technical_assessment" else "technical_questions"
        )
        
        # Process response for very long messages
        max_length = get_config("UI_SETTINGS", "max_message_display_length", 800)
        if len(response) > max_length:
            response = response[:max_length] + "..."
        
        # Determine if we should transition state based on response
        next_state, _ = self.get_next_state(current_state, candidate_info, sanitized_message)
        
        return response, next_state
    
    def get_fallback_response(self, user_input: str, candidate_info: Dict[str, str], 
                             current_state: str) -> str:
        """
        Generate an intelligent fallback response when the user's input is unclear.
        This provides clear guidance to get back on track.
        """
        # Personalize if we have the name
        name = candidate_info.get('name', 'there')
        
        # Different fallbacks based on conversation state
        if current_state == "initial":
            return f"Hi {name}, I didn't quite understand that. I'm TalentScout AI, your hiring assistant. To get started with the screening process, could you please tell me your full name?"
        
        elif current_state == "data_collection":
            fields = ["name", "email", "phone", "experience", "position", "location", "tech_stack"]
            # Find which field we're currently collecting
            current_field = None
            for field in fields:
                if field not in candidate_info or not candidate_info[field]:
                    current_field = field
                    break
            
            if current_field:
                field_descriptions = {
                    "name": "full name",
                    "email": "email address (example: name@company.com)",
                    "phone": "phone number",
                    "experience": "years of experience in your field",
                    "position": "position you're applying for",
                    "location": "current location or city",
                    "tech_stack": "technical skills and technologies you're proficient in"
                }
                
                return f"I need to collect some information for your application. Could you please provide your {field_descriptions.get(current_field, current_field)}?"
        
        elif current_state == "technical_assessment":
            return f"I didn't quite understand your response, {name}. We're currently in the technical assessment phase. Could you please elaborate on your experience with the technologies you mentioned?"
        
        # Generic fallback for other states
        return f"I didn't quite understand that, {name}. Could you please rephrase or provide more details? I'm here to help with your job application."


# Singleton instance
conversation_manager = ConversationManager()