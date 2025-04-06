"""
Advanced LLM service for TalentScout AI
This module handles all interactions with large language models (Groq API).
Features:
- Better context management with RAG approach
- Memory management for conversations
- Custom model selection based on task type
- Comprehensive error handling and retry logic
- Better prompt templating and engineering
"""

import os
import json
import time
import hashlib
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
import groq

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMCache:
    """Cache for LLM responses to improve performance and reduce API costs."""
    
    def __init__(self, cache_dir: str = ".cache"):
        """Initialize the cache."""
        self.cache_dir = cache_dir
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        logger.info(f"Initialized LLM cache at {cache_dir}")
    
    def _get_cache_key(self, prompt: str, model: str, temperature: float) -> str:
        """Generate a unique cache key based on input parameters."""
        # Create a unique hash based on prompt, model, and temperature
        key_content = f"{prompt}|{model}|{temperature}"
        cache_key = hashlib.md5(key_content.encode()).hexdigest()
        
        return cache_key
    
    def get_from_cache(self, prompt: str, model: str, temperature: float) -> Optional[str]:
        """Retrieve a response from cache if it exists."""
        cache_key = self._get_cache_key(prompt, model, temperature)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            # Check if cache file exists
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is still valid (not expired)
                cache_time = cached_data.get('timestamp', 0)
                current_time = time.time()
                
                # Cache validity - 24 hours for now
                if current_time - cache_time < 86400:  # 24 hours in seconds
                    logger.info(f"Cache hit for {cache_key[:8]}...")
                    return cached_data.get('response')
                else:
                    logger.info(f"Cache expired for {cache_key[:8]}...")
                    # Remove expired cache
                    os.remove(cache_file)
        
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
        
        return None
    
    def save_to_cache(self, prompt: str, model: str, temperature: float, response: str) -> None:
        """Save a response to the cache."""
        cache_key = self._get_cache_key(prompt, model, temperature)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            cache_data = {
                'prompt': prompt,
                'model': model,
                'temperature': temperature,
                'response': response,
                'timestamp': time.time()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
                
            logger.info(f"Saved response to cache with key {cache_key[:8]}...")
            
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")


class GroqLLMService:
    """Enhanced service for interacting with Groq LLM API."""
    
    MODEL_CAPABILITIES = {
        "llama3-70b-8192": {
            "strengths": ["general purpose", "coding", "instruction following", "reasoning"],
            "max_tokens": 8192,
            "best_for": ["technical questions", "detailed explanations", "complex reasoning"]
        },
        "mixtral-8x7b-32768": {
            "strengths": ["context length", "knowledge", "general purpose"],
            "max_tokens": 32768,
            "best_for": ["long conversations", "document analysis", "general chat"]
        },
        "gemma-7b-it": {
            "strengths": ["instruction following", "efficient", "fast"],
            "max_tokens": 8192,
            "best_for": ["simple tasks", "quick responses", "lightweight applications"]
        }
    }
    
    TASK_MODEL_MAPPING = {
        "screening": "llama3-70b-8192",  # Good for general conversation and evaluation
        "technical_questions": "llama3-70b-8192",  # Good for generating technical questions
        "skill_assessment": "llama3-70b-8192",  # Good for evaluating technical skills
        "conversation": "mixtral-8x7b-32768",  # Good for handling long conversations
        "summarization": "llama3-70b-8192",  # Good for creating summaries
        "quick_response": "gemma-7b-it"  # Good for simple, fast responses
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM service with API key and caching."""
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.client = None
        self.cache = LLMCache()
        self.last_call_time = 0
        self.rate_limit_delay = 0.5  # Default delay between calls in seconds
        
        # Initialize Groq client if key is available
        if self.api_key:
            try:
                self.client = groq.Client(api_key=self.api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Groq client: {str(e)}")
        else:
            logger.warning("No Groq API key provided, LLM service will be unavailable")
    
    def is_available(self) -> bool:
        """Check if the LLM service is available and properly configured."""
        if not self.api_key or not self.client:
            return False
            
        try:
            # Simple test call with minimal tokens
            _ = self.client.chat.completions.create(
                model="gemma-7b-it",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"LLM service availability check failed: {str(e)}")
            return False
    
    def select_best_model(self, task_type: str, context_length: int = 0) -> str:
        """Select the best model based on task type and context length."""
        # Get default model for task
        model = self.TASK_MODEL_MAPPING.get(task_type, "llama3-70b-8192")
        
        # For very long contexts, prefer mixtral which has longer context window
        if context_length > 7000:
            model = "mixtral-8x7b-32768"
            
        # For quick responses with short context, use faster model
        if task_type == "quick_response" and context_length < 2000:
            model = "gemma-7b-it"
            
        return model
    
    def _format_system_prompt(self, task_type: str) -> str:
        """Create a better system prompt based on task type."""
        system_prompts = {
            "screening": """You are TalentScout AI, a professional hiring assistant. 
            Your goal is to help screen candidates by gathering information and assessing fit.
            Keep your responses concise, professional, and focused on the candidate's qualifications.
            Be friendly but maintain a professional tone suitable for a hiring context.
            Format responses clearly and avoid technical jargon unless discussing technical topics.
            If you don't know something, acknowledge it rather than making up information.""",
            
            "technical_questions": """You are TalentScout AI, an expert technical interviewer.
            Generate insightful, targeted technical questions that assess both theoretical knowledge and practical experience.
            Tailor questions to the candidate's experience level: avoid basic questions for senior candidates and advanced questions for juniors.
            For coding or technical questions, focus on problem-solving approach rather than specific syntax.
            Include questions that reveal both depth of knowledge and breadth across related technologies.""",
            
            "skill_assessment": """You are TalentScout AI, a technical skill assessor.
            Analyze technical skills and provide constructive evaluation based on industry standards.
            Consider both the core skill mentioned and its relation to adjacent technologies.
            Evaluate skills in context of the role requirements and candidate's experience level.
            Be honest but constructive when identifying skill gaps or suggesting areas for improvement.""",
            
            "conversation": """You are TalentScout AI, a conversational hiring assistant.
            Maintain the flow of conversation while extracting relevant information for the hiring process.
            Keep track of what has been discussed and avoid repeating questions.
            Follow up on interesting points that could reveal more about the candidate's qualifications or approach.
            Be concise, engaging, and clear in your communication.""",
            
            "summarization": """You are TalentScout AI, a hiring data analyst.
            Summarize candidate information objectively, highlighting key qualifications and potential fit.
            Organize information by relevance to the position requirements.
            Present both strengths and areas for development in a balanced way.
            Avoid including personal opinions or biases in your summary.""",
            
            "quick_response": """You are TalentScout AI, a responsive hiring assistant.
            Provide clear, direct responses to immediate questions or clarifications.
            Be brief but helpful, focusing on the most relevant information.
            When uncertain, acknowledge limitations rather than speculating."""
        }
        
        return system_prompts.get(task_type, system_prompts["screening"])
    
    def _create_structured_prompt(self, base_prompt: str, variables: Dict[str, Any] = None) -> str:
        """Create a structured prompt with variable substitution."""
        if not variables:
            return base_prompt
            
        # Simple variable substitution
        final_prompt = base_prompt
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in final_prompt:
                final_prompt = final_prompt.replace(placeholder, str(value))
                
        return final_prompt
    
    def _validate_response(self, response: str) -> bool:
        """Validate that the response meets quality standards."""
        if not response or len(response.strip()) < 10:
            return False
            
        # Check for common error patterns
        error_patterns = [
            "I cannot assist with that",
            "I'm unable to",
            "I don't have access to",
            "I apologize, but I cannot",
            "API Error",
            "Error code"
        ]
        
        for pattern in error_patterns:
            if pattern.lower() in response.lower():
                return False
                
        return True
    
    def generate_response(
        self, 
        prompt: str, 
        task_type: str = "screening",
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 300,
        use_cache: bool = True
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a response from the LLM with enhanced error handling and caching.
        
        Returns:
            Tuple of (response_text, metadata)
        """
        metadata = {
            "model_used": None,
            "tokens_used": 0,
            "cache_hit": False,
            "task_type": task_type,
            "error": None
        }
        
        # Check cache first if enabled
        if use_cache:
            cached_response = self.cache.get_from_cache(prompt, model or self.select_best_model(task_type), temperature)
            if cached_response:
                metadata["cache_hit"] = True
                metadata["model_used"] = model or self.select_best_model(task_type)
                return cached_response, metadata
        
        # Check if client is available
        if not self.client:
            fallback = self._get_fallback_response(task_type, prompt)
            metadata["error"] = "LLM client not initialized"
            return fallback, metadata
        
        # Select model if not specified
        if not model:
            model = self.select_best_model(task_type, len(prompt))
        
        metadata["model_used"] = model
        
        # Get appropriate system prompt if not provided
        if not system_prompt:
            system_prompt = self._format_system_prompt(task_type)
        
        # Rate limiting - ensure we don't hit API too quickly
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            time.sleep(sleep_time)
        
        # Update last call time
        self.last_call_time = time.time()
        
        # Try to generate response with error handling and retries
        max_retries = 2
        retries = 0
        
        while retries <= max_retries:
            try:
                # Call Groq API
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Extract response text
                response_text = response.choices[0].message.content
                
                # Update metadata
                metadata["tokens_used"] = response.usage.total_tokens
                
                # Validate response quality
                if self._validate_response(response_text):
                    # Save to cache if valid and caching is enabled
                    if use_cache:
                        self.cache.save_to_cache(prompt, model, temperature, response_text)
                    
                    return response_text, metadata
                else:
                    # Invalid response, retry with different model or parameters
                    logger.warning(f"Invalid response received, retrying ({retries+1}/{max_retries})")
                    retries += 1
                    
                    # Try a different model if available
                    if retries == 1 and model != "llama3-70b-8192":
                        model = "llama3-70b-8192"
                        metadata["model_used"] = model
                        continue
                    
                    # Try with higher temperature on last retry
                    if retries == 2:
                        temperature = min(0.9, temperature + 0.2)  # Increase temperature but cap at 0.9
                
            except Exception as e:
                logger.error(f"Error generating response (try {retries+1}/{max_retries}): {str(e)}")
                retries += 1
                
                # Exponential backoff
                if retries <= max_retries:
                    backoff = 2 ** retries
                    time.sleep(backoff)
        
        # If all retries failed, return fallback response
        fallback = self._get_fallback_response(task_type, prompt)
        metadata["error"] = "Failed after max retries"
        return fallback, metadata
    
    def _get_fallback_response(self, task_type: str, prompt: str) -> str:
        """Get an appropriate fallback response based on task type."""
        # Generic fallbacks for different task types
        fallbacks = {
            "screening": "Thank you for your response. I've noted your information and will continue with the screening process. Could you please provide more details about your experience and skills?",
            
            "technical_questions": "Based on your experience, I'd like to ask about your approach to problem-solving in your technical work. Could you describe a challenging technical problem you've solved recently and how you approached it?",
            
            "skill_assessment": "Your technical background is valuable. To better understand your expertise, could you elaborate on which aspects of these technologies you've used most extensively in your work?",
            
            "conversation": "I appreciate you sharing that information. Let's continue our conversation about your qualifications and how they align with this position.",
            
            "summarization": "Based on our conversation, I've gathered some key information about your background and skills. We'll take this into consideration for the next steps of the hiring process.",
            
            "quick_response": "Thank you for your question. I'll make a note of it and ensure it's addressed appropriately."
        }
        
        return fallbacks.get(task_type, fallbacks["screening"])


# Create singleton instance
llm_service = GroqLLMService()