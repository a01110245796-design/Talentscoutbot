"""
TalentScout AI Configuration Settings

This module contains application-wide settings and configuration options.
"""

import os
from typing import Dict, Any

# API and external service settings
API_KEYS = {
    "groq": os.environ.get("GROQ_API_KEY", "")
}

# Application settings
APP_SETTINGS = {
    "app_name": "TalentScout AI Hiring Assistant",
    "version": "1.0.0",
    "description": "An AI-powered hiring assistant for candidate screening",
    "author": "Goddati Bhavyasri",
    "contact_email": "support@talentscout.ai"
}

# Feature flags
FEATURES = {
    "enable_gdpr_compliance": True,
    "enable_data_encryption": True,
    "enable_advanced_assessment": True,
    "enable_conversation_analytics": True,
    "enable_export_features": True
}

# UI settings
UI_SETTINGS = {
    "primary_color": "#3b82f6",  # Blue
    "secondary_color": "#60a5fa",  # Light blue
    "accent_color": "#2563eb",  # Dark blue
    "background_color": "#0e1117",  # Dark background
    "text_color": "#ffffff",  # White text
    "footer_highlight_color": "#60a5fa",  # Blue highlight for footer
    "max_message_display_length": 800  # Maximum length of messages to display
}

# Security settings
SECURITY = {
    "allowed_origins": ["localhost", "talentscout.ai"],
    "encryption_enabled": True,
    "input_sanitization_enabled": True,
    "data_retention_days": 180,  # GDPR compliance - 6 months
}

# Assessment configuration
ASSESSMENT = {
    "max_questions_per_skill": 2,
    "max_total_questions": 5,
    "experience_levels": {
        "beginner": {"min_years": 0, "max_years": 2},
        "intermediate": {"min_years": 2, "max_years": 5},
        "advanced": {"min_years": 5, "max_years": 100}
    }
}

# Get a configuration value with default fallback
def get_config(section: str, key: str, default: Any = None) -> Any:
    """
    Get a configuration value from the specified section.
    
    Args:
        section: The configuration section (e.g., 'API_KEYS', 'APP_SETTINGS')
        key: The configuration key
        default: Default value if the configuration is not found
        
    Returns:
        The configuration value or the default
    """
    try:
        config_section = globals().get(section, {})
        return config_section.get(key, default)
    except Exception:
        return default