"""
Advanced Technical Skill Assessment for TalentScout AI

This module provides sophisticated technical assessment capabilities,
including experience-based question generation, skill evaluation,
and intelligent technical assessment based on candidate profiles.
"""

import os
import re
import json
import random
import logging
from typing import Dict, List, Tuple, Any, Optional

from models.llm_service import llm_service
from config.settings import get_config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TechnicalAssessor:
    """Advanced technical skill assessment service."""
    
    def __init__(self):
        """Initialize the technical assessor."""
        # Load skill question banks if available
        self.question_bank = {}
        try:
            question_bank_path = os.path.join("data", "question_bank.json")
            if os.path.exists(question_bank_path):
                with open(question_bank_path, 'r') as f:
                    self.question_bank = json.load(f)
                    logger.info(f"Loaded question bank with {len(self.question_bank)} skill categories")
            else:
                logger.info("Question bank file not found, will generate questions dynamically")
        except Exception as e:
            logger.error(f"Error loading question bank: {str(e)}")
            
        # Knowledge graph of related skills for improved assessment
        self.skill_relationships = {
            "javascript": ["typescript", "react", "vue", "angular", "node.js", "express", "frontend"],
            "python": ["django", "flask", "fastapi", "data science", "machine learning", "backend"],
            "java": ["spring", "spring boot", "hibernate", "backend", "enterprise"],
            "c#": [".net", "asp.net", "xamarin", "unity", "backend"],
            "react": ["javascript", "typescript", "redux", "frontend", "react native"],
            "angular": ["typescript", "javascript", "rxjs", "frontend"],
            "vue": ["javascript", "vuex", "frontend"],
            "node.js": ["javascript", "express", "backend", "api"],
            "php": ["laravel", "symfony", "wordpress", "backend"],
            "sql": ["postgresql", "mysql", "oracle", "database", "data"],
            "nosql": ["mongodb", "couchdb", "cassandra", "database", "data"],
            "aws": ["cloud", "devops", "serverless", "infrastructure"],
            "azure": ["cloud", "devops", "microsoft", "infrastructure"],
            "devops": ["ci/cd", "jenkins", "docker", "kubernetes", "infrastructure"],
            "machine learning": ["python", "tensorflow", "pytorch", "data science", "ai"],
            "data science": ["python", "r", "statistics", "machine learning", "data"],
            "mobile": ["android", "ios", "react native", "flutter", "frontend"],
            "blockchain": ["smart contracts", "ethereum", "solidity", "web3"],
            "frontend": ["html", "css", "javascript", "ui/ux", "responsive design"],
            "backend": ["api", "database", "server", "authentication", "authorization"],
            "fullstack": ["frontend", "backend", "javascript", "python", "java"]
        }
    
    def _parse_skills(self, skills_text: str) -> List[Dict[str, str]]:
        """Parse skills from raw text input with categorization."""
        if not skills_text:
            return []
            
        # Extract individual skills from text
        skill_list = re.split(r'[,;/\s]+', skills_text)
        skill_list = [s.strip().lower() for s in skill_list if s.strip()]
        
        # Deduplicate skills
        skill_list = list(set(skill_list))
        
        # Categorize each skill
        categorized_skills = []
        for skill in skill_list:
            # Skip very short skills (likely not real skills)
            if len(skill) < 2:
                continue
                
            # Determine category
            category = "unknown"
            for cat, related in self.skill_relationships.items():
                if skill == cat or skill in related:
                    category = cat
                    break
            
            categorized_skills.append({
                "skill": skill,
                "category": category
            })
            
        return categorized_skills
    
    def _determine_experience_level(self, years_experience: str) -> str:
        """Determine experience level based on years of experience."""
        try:
            # Try to convert to float
            years = float(years_experience.replace('years', '').replace('year', '').strip())
            
            if years < 2:
                return "beginner"
            elif years < 5:
                return "intermediate"
            else:
                return "advanced"
                
        except (ValueError, TypeError):
            # If years can't be parsed, default to intermediate
            return "intermediate"
    
    def _get_questions_for_skill(self, skill: Dict[str, str], experience_level: str) -> List[str]:
        """Get appropriate questions for a skill based on experience level."""
        skill_name = skill["skill"]
        category = skill["category"]
        
        # Check if we have questions for this skill in our bank
        if skill_name in self.question_bank and experience_level in self.question_bank[skill_name]:
            questions = self.question_bank[skill_name][experience_level]
            # Return a subset of questions (at most 2)
            return random.sample(questions, min(2, len(questions)))
            
        # Try to find questions for the category instead
        elif category in self.question_bank and experience_level in self.question_bank[category]:
            questions = self.question_bank[category][experience_level]
            # Return a subset of questions (at most 2)
            return random.sample(questions, min(2, len(questions)))
            
        # If no questions found, generate them using LLM
        else:
            return self._generate_questions_from_llm(skill_name, "", experience_level)
    
    def _generate_questions_from_llm(self, skill: str, position: str, experience_level: str) -> List[str]:
        """Generate skill-specific questions using the LLM."""
        # Convert experience level to years for better context
        exp_years = self._experience_years_from_level(experience_level)
        
        position_context = f" for a {position} role" if position else ""
        
        prompt = f"""Generate 2 technical interview questions about {skill} that would be appropriate for a candidate with {exp_years} years of experience{position_context}.

The questions should:
1. Be specific to {skill} and appropriate for {experience_level} level (no basic questions for advanced candidates)
2. Assess both theoretical knowledge and practical application
3. Reveal the depth of the candidate's expertise
4. Be concise and clearly worded

Format your response as a numbered list with only the questions, nothing else.
"""
        
        try:
            # Generate questions using LLM
            response, metadata = llm_service.generate_response(
                prompt=prompt,
                task_type="technical_questions",
                temperature=0.7,
                max_tokens=300
            )
            
            # Parse the response
            questions = []
            for line in response.strip().split('\n'):
                # Remove numbering and whitespace
                line = re.sub(r'^\d+[\.\)]\s*', '', line.strip())
                if line and len(line) > 10:  # Only add non-empty, meaningful questions
                    questions.append(line)
            
            # Ensure we have at least one question
            if not questions:
                questions = self._get_fallback_questions(skill, experience_level)
                
            return questions[:2]  # Return at most 2 questions
            
        except Exception as e:
            logger.error(f"Error generating questions from LLM: {str(e)}")
            return self._get_fallback_questions(skill, experience_level)
    
    def _experience_years_from_level(self, level: str) -> str:
        """Convert experience level to approximate years."""
        levels = {
            "beginner": "1-2",
            "intermediate": "3-5",
            "advanced": "5+"
        }
        return levels.get(level, "3-5")
    
    def _get_fallback_questions(self, skill: str, experience_level: str) -> List[str]:
        """Generate fallback questions when the database and LLM fail."""
        # Generic questions that can be adapted to any skill
        fallbacks = {
            "beginner": [
                f"Describe your experience with {skill} and what you've built with it so far.",
                f"What are the fundamental concepts of {skill} that you're familiar with?",
                f"How have you approached learning {skill} and what resources have you found most helpful?"
            ],
            "intermediate": [
                f"What challenges have you overcome while working with {skill} in a professional context?",
                f"How do you stay updated with best practices and new developments in {skill}?",
                f"Describe a complex problem you solved using {skill} and your approach to it."
            ],
            "advanced": [
                f"How have you optimized or improved {skill} implementations in previous roles?",
                f"Describe your approach to mentoring junior developers in {skill}.",
                f"What architectural decisions have you made around {skill} and what were the trade-offs?"
            ]
        }
        
        # Get questions for the specified level, or intermediate as fallback
        questions = fallbacks.get(experience_level, fallbacks["intermediate"])
        
        # Return a subset of questions
        return random.sample(questions, min(2, len(questions)))
    
    def generate_technical_questions(self, skills: str, experience: str, position: str) -> str:
        """Generate tailored technical questions based on candidate profile."""
        if not skills:
            return "Could not generate questions without skill information."
        
        # Parse skills
        parsed_skills = self._parse_skills(skills)
        if not parsed_skills:
            return "Could not identify specific skills to generate questions. Please provide more details about your technical expertise."
        
        # Determine experience level
        experience_level = self._determine_experience_level(experience)
        
        # Generate questions for each skill
        all_questions = []
        
        # Get configuration
        max_questions_per_skill = get_config("ASSESSMENT", "max_questions_per_skill", 2)
        max_total_questions = get_config("ASSESSMENT", "max_total_questions", 5)
        
        # Prioritize skills based on relevance to position
        if position:
            position_lower = position.lower()
            # Sort skills by relevance to position
            for skill in parsed_skills:
                skill_relevance = self.evaluate_technical_skill(skill["skill"], experience, position)
                skill["relevance"] = skill_relevance["score"]
            
            parsed_skills.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        
        # Generate questions for each skill, but limit total number
        for skill in parsed_skills:
            if len(all_questions) >= max_total_questions:
                break
                
            skill_questions = self._get_questions_for_skill(skill, experience_level)
            # Take at most max_questions_per_skill questions per skill
            skill_questions = skill_questions[:max_questions_per_skill]
            
            for question in skill_questions:
                if len(all_questions) < max_total_questions:
                    all_questions.append({
                        "skill": skill["skill"],
                        "question": question
                    })
        
        # Format questions into a nice Markdown format
        if all_questions:
            formatted_output = f"## Technical Interview Questions\n\nBased on the candidate's profile ({experience_level} level, {position}), here are customized technical questions:\n\n"
            
            for i, q in enumerate(all_questions, 1):
                formatted_output += f"### {i}. {q['skill'].capitalize()} Question\n"
                formatted_output += f"{q['question']}\n\n"
            
            # Add interviewer notes
            formatted_output += "### Interviewer Notes\n"
            formatted_output += f"- Candidate has indicated {experience} years of experience, placing them at an {experience_level} level.\n"
            formatted_output += f"- Focus on depth of knowledge in their primary skills: {', '.join([s['skill'] for s in parsed_skills[:3]])}\n"
            formatted_output += "- These questions are designed to reveal both theoretical understanding and practical application.\n"
            
            return formatted_output
        else:
            return "Could not generate appropriate technical questions. Please review the candidate's skills and experience."
    
    def evaluate_technical_skill(self, skill: str, experience: str, position: str) -> Dict[str, Any]:
        """Evaluate the relevance and depth of a technical skill for a position."""
        # Default values
        evaluation = {
            "skill": skill,
            "relevance": "moderate",
            "score": 50,  # Default middle score
            "experience_level": "intermediate",
            "recommendation": "Consider exploring this skill further in the interview."
        }
        
        # Determine experience level
        evaluation["experience_level"] = self._determine_experience_level(experience)
        
        if not position:
            return evaluation
            
        # Set up skill matching for common positions
        position_lower = position.lower()
        
        # Define skill relevance to common roles
        role_skills = {
            "frontend": ["javascript", "typescript", "react", "vue", "angular", "html", "css", "responsive", "ui/ux"],
            "backend": ["java", "python", "c#", "node.js", "php", "go", "rust", "sql", "nosql", "api"],
            "fullstack": ["javascript", "python", "java", "node.js", "react", "angular", "vue", "sql", "nosql"],
            "devops": ["docker", "kubernetes", "jenkins", "github actions", "aws", "azure", "gcp", "linux", "ci/cd"],
            "data": ["python", "r", "sql", "nosql", "pandas", "hadoop", "spark", "etl", "tableau", "power bi"],
            "mobile": ["android", "ios", "swift", "kotlin", "react native", "flutter"],
            "machine learning": ["python", "tensorflow", "pytorch", "scikit-learn", "nlp", "computer vision"]
        }
        
        # Figure out which role this position most closely matches
        matched_role = None
        max_match = 0
        
        for role, keywords in role_skills.items():
            match_score = 0
            for keyword in keywords:
                if keyword in position_lower:
                    match_score += 1
            
            if match_score > max_match:
                max_match = match_score
                matched_role = role
        
        # If no role matched, use generic scoring
        if not matched_role:
            # Generic relevance for unrecognized roles
            evaluation["relevance"] = "moderate"
            evaluation["score"] = 50
            evaluation["recommendation"] = f"Explore how {skill} has been applied in previous roles."
            return evaluation
        
        # Calculate relevance score based on role match
        relevant_skills = role_skills[matched_role]
        skill_lower = skill.lower()
        
        # Direct match
        if skill_lower in relevant_skills:
            evaluation["relevance"] = "high"
            evaluation["score"] = random.randint(80, 100)  # High relevance score
            evaluation["recommendation"] = f"{skill} is a core skill for this {matched_role} role. Explore depth of expertise."
        
        # Check for related skills
        elif skill_lower in self.skill_relationships:
            related = self.skill_relationships[skill_lower]
            role_match = any(r in relevant_skills for r in related)
            
            if role_match:
                evaluation["relevance"] = "medium-high"
                evaluation["score"] = random.randint(65, 80)  # Medium-high relevance
                evaluation["recommendation"] = f"{skill} is a complementary skill for this {matched_role} role. Assess how it enhances their primary expertise."
            else:
                evaluation["relevance"] = "medium-low"
                evaluation["score"] = random.randint(40, 65)  # Medium-low relevance
                evaluation["recommendation"] = f"While {skill} is not directly related to the {matched_role} role, it may provide valuable perspective."
        
        # Unrelated skill
        else:
            evaluation["relevance"] = "low"
            evaluation["score"] = random.randint(20, 40)  # Low relevance
            evaluation["recommendation"] = f"{skill} appears to be outside the core requirements for this {matched_role} role, but may indicate breadth of knowledge."
        
        # Consider experience level in the final score
        experience_multiplier = {
            "beginner": 0.8,
            "intermediate": 1.0,
            "advanced": 1.2
        }.get(evaluation["experience_level"], 1.0)
        
        # Adjust score based on experience (more experienced candidates get slightly higher scores)
        adjusted_score = int(evaluation["score"] * experience_multiplier)
        evaluation["score"] = max(0, min(100, adjusted_score))  # Keep within 0-100 range
        
        return evaluation
    
    def _get_skill_recommendation(self, skill: str, relevance: float, experience_level: str) -> str:
        """Generate a recommendation based on skill evaluation."""
        if relevance >= 80:
            if experience_level == "advanced":
                return f"Candidate shows strong alignment with {skill}, which is critical for this role. Consider exploring architecture and leadership aspects."
            elif experience_level == "intermediate":
                return f"Candidate has solid experience with {skill}. Explore depth of knowledge and recent projects."
            else:
                return f"Candidate has promising foundation in {skill}. Assess potential for growth and learning curve."
        elif relevance >= 60:
            return f"{skill} is relevant to the role. Determine how effectively they've applied it in previous work."
        else:
            return f"{skill} is not a core requirement but may provide valuable perspective. Consider how it complements their primary skills."


# Create a singleton instance
skill_assessor = TechnicalAssessor()