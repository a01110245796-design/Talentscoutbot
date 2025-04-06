"""
Security and Privacy Utilities for TalentScout AI
This module implements GDPR-compliant data handling, encryption, and sanitization
functions for sensitive candidate information.
"""

import re
import os
import json
import logging
import base64
import hashlib
import secrets
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

try:
    # Import cryptography if available
    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GDPRCompliance:
    """GDPR compliance utilities for handling candidate data."""

    @staticmethod
    def get_privacy_notice() -> str:
        """Return the GDPR-compliant privacy notice for candidates."""
        privacy_notice = """
        <h3>Privacy Notice - TalentScout AI Hiring Assistant</h3>
        
        <p>TalentScout AI collects and processes your personal data to facilitate the hiring process. This notice explains how we handle your information.</p>
        
        <h3>Data We Collect</h3>
        <ul>
            <li>Basic personal information (name, email, phone number)</li>
            <li>Professional information (experience, skills, position applying for)</li>
            <li>Your responses during the screening conversation</li>
        </ul>
        
        <h3>How We Use Your Data</h3>
        <ul>
            <li>To assess your suitability for the position</li>
            <li>To generate relevant technical questions</li>
            <li>To provide hiring recommendations to employers</li>
        </ul>
        
        <h3>Your Data Rights</h3>
        <ul>
            <li>Access your personal data</li>
            <li>Request correction of inaccurate data</li>
            <li>Request deletion of your data</li>
            <li>Export your conversation data</li>
        </ul>
        
        <h3>Data Retention</h3>
        <p>We retain your data for 6 months after the interview, after which it will be anonymized or deleted.</p>
        
        <h3>Contact Information</h3>
        <p>For privacy inquiries, please contact: privacy@talentscout.ai</p>
        """
        return privacy_notice

    @staticmethod
    def log_consent(candidate_id: str, consent_timestamp: datetime) -> None:
        """Log candidate consent for data processing."""
        try:
            # In a production environment, this would store consent in a secure database
            # For this demo, we'll just log it
            consent_record = {
                "candidate_id": candidate_id,
                "consent_timestamp": consent_timestamp.isoformat(),
                "consent_version": "1.0",
                "ip_address": "[Redacted for privacy]"  # In production, store hashed IP
            }
            
            logger.info(f"Logged consent for candidate {candidate_id}")
            
            # Ensure consent directory exists
            os.makedirs("data/consent_logs", exist_ok=True)
            
            # Write consent to file (in production, use a secure database)
            with open(f"data/consent_logs/{candidate_id}_consent.json", "w") as f:
                json.dump(consent_record, f)
                
        except Exception as e:
            logger.error(f"Error logging consent: {str(e)}")

    @staticmethod
    def anonymize_data(candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize candidate data for analysis or long-term storage."""
        if not candidate_data:
            return {}
            
        # Create a copy to avoid modifying the original
        anonymized = candidate_data.copy()
        
        # Anonymize identifiable fields
        if "name" in anonymized:
            # Replace with generic identifier
            anonymized["name"] = f"Candidate_{hashlib.sha256(anonymized['name'].encode()).hexdigest()[:8]}"
        
        if "email" in anonymized:
            # Hash the email
            anonymized["email"] = f"email_{hashlib.sha256(anonymized['email'].encode()).hexdigest()[:10]}"
        
        if "phone" in anonymized:
            # Hash the phone
            anonymized["phone"] = f"phone_{hashlib.sha256(anonymized['phone'].encode()).hexdigest()[:10]}"
            
        # Keep non-identifiable data
        # - experience, skills, position are kept for analytics purposes
        
        return anonymized

    @staticmethod
    def create_data_export(candidate_data: Dict[str, Any], chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a GDPR-compliant data export for a candidate."""
        export_data = {
            "personal_data": {
                key: value for key, value in candidate_data.items() 
                if key in ["name", "email", "phone", "location"]
            },
            "professional_data": {
                key: value for key, value in candidate_data.items()
                if key in ["experience", "position", "tech_stack"]
            },
            "chat_history": chat_history,
            "export_date": datetime.now().isoformat(),
            "retention_policy": "Data retained for 6 months from interview date",
            "data_controller": "TalentScout AI",
            "privacy_contact": "privacy@talentscout.ai"
        }
        
        return export_data


class DataEncryption:
    """Secure data encryption utilities."""
    
    def __init__(self, key: Optional[str] = None):
        """Initialize encryption with a key or generate one."""
        self.encryption_enabled = CRYPTO_AVAILABLE
        self.key = None
        self.fernet = None
        
        if not self.encryption_enabled:
            logger.warning("Cryptography package not available, encryption disabled")
            return
            
        try:
            if key:
                # Use provided key
                self.key = key.encode()
            else:
                # Generate a key from environment or create a new one
                env_key = os.environ.get("ENCRYPTION_KEY")
                if env_key:
                    self.key = base64.urlsafe_b64decode(env_key)
                else:
                    # Generate a new key
                    self.key = Fernet.generate_key()
            
            # Initialize Fernet with the key
            self.fernet = Fernet(self.key)
            logger.info("Encryption initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing encryption: {str(e)}")
            self.encryption_enabled = False
    
    def encrypt(self, data: str) -> str:
        """Encrypt data string."""
        if not self.encryption_enabled or not self.fernet:
            logger.warning("Encryption not available, returning unencrypted data")
            return data
            
        try:
            encrypted = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            return data
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt encrypted data string."""
        if not self.encryption_enabled or not self.fernet:
            logger.warning("Decryption not available, returning data as is")
            return encrypted_data
            
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            return encrypted_data


class InputSanitizer:
    """Input sanitization and validation utilities."""
    
    @staticmethod
    def sanitize_input(input_text: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        if not input_text:
            return ""
            
        # Convert to string if not already
        if not isinstance(input_text, str):
            input_text = str(input_text)
            
        # Basic XSS prevention - remove script tags and other potentially harmful elements
        sanitized = re.sub(r'<script.*?>.*?</script>', '', input_text, flags=re.DOTALL | re.IGNORECASE)
        sanitized = re.sub(r'<.*?javascript:.*?>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
        sanitized = re.sub(r'on\w+=".*?"', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
        
        # Truncate very long inputs
        max_length = 1000  # Reasonable limit for user input
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."
            
        return sanitized
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        # Simple email validation pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        # Allow various phone formats: (123) 456-7890, 123-456-7890, 123.456.7890, etc.
        phone = re.sub(r'[\s\(\)\-\.]', '', phone)  # Remove formatting
        # Check if it contains only digits and has a reasonable length
        return phone.isdigit() and 7 <= len(phone) <= 15
    
    @staticmethod
    def validate_input_safe(field: str, value: str) -> Tuple[bool, str]:
        """Extended input validation with better security checks and helpful error messages."""
        sanitized = InputSanitizer.sanitize_input(value)
        
        if not sanitized or sanitized.isspace():
            return False, f"Please provide a valid {field}."
        
        if field == "email":
            if not InputSanitizer.validate_email(sanitized):
                return False, "Please provide a valid email address (e.g., name@example.com)."
            return True, sanitized
            
        elif field == "phone":
            if not InputSanitizer.validate_phone(sanitized):
                return False, "Please provide a valid phone number (e.g., 123-456-7890)."
            return True, sanitized
            
        elif field == "experience":
            # Try to extract a numeric value
            # Remove non-numeric characters, except decimal point
            numeric_value = re.sub(r'[^\d\.]', '', sanitized)
            
            try:
                # Try to convert to float
                experience = float(numeric_value)
                
                # Validate range
                if experience < 0:
                    return False, "Experience cannot be negative. Please provide a valid number of years."
                if experience > 100:
                    return False, "Please provide a valid number of years of experience."
                    
                # Convert to string with proper formatting
                if experience.is_integer():
                    return True, str(int(experience))
                else:
                    return True, str(round(experience, 1))
                    
            except (ValueError, TypeError):
                return False, "Please provide a valid number for your years of experience."
        
        # For all other fields, just return the sanitized value
        return True, sanitized


# Initialize singletons
gdpr_compliance = GDPRCompliance()
data_encryption = DataEncryption()
input_sanitizer = InputSanitizer()