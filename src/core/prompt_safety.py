from typing import List, Dict, Set
import re
from src.core.logging import get_logger

logger = get_logger(__name__)

class PromptSafety:
    # Prohibited content patterns
    PROHIBITED_PATTERNS = {
        'personal_info': r'\b(?:ssn|social\ssecurity|credit\scard|bank\saccount|password|pin)\b',
        'sensitive_topics': r'\b(?:politics|religion|race|gender|sexuality|violence|drugs|alcohol)\b',
        'inappropriate_language': r'\b(?:fuck|shit|damn|hell|bitch|asshole)\b',
        'company_secrets': r'\b(?:confidential|proprietary|trade\ssecret|internal\suse\sonly)\b',
        'financial_advice': r'\b(?:invest|stock|market|trading|financial\sadvice)\b',
        'medical_advice': r'\b(?:prescription|diagnosis|treatment|medical\sadvice|doctor)\b',
        'legal_advice': r'\b(?:legal\sadvice|lawyer|attorney|court|lawsuit)\b'
    }
    
    # Required content patterns
    REQUIRED_PATTERNS = {
        'disclaimer': r'This is a grocery shopping assistant and recipe helper',
        'scope': r'focusing on food, recipes, and grocery shopping',
        'limitation': r'cannot provide (?:medical|legal|financial) advice'
    }
    
    # Safe response templates
    SAFE_RESPONSES = {
        'prohibited_content': "I apologize, but I can't assist with that topic. I'm here to help with grocery shopping and recipes.",
        'sensitive_topic': "I'm designed to focus on grocery shopping and recipes. Let's keep our conversation related to food and shopping.",
        'out_of_scope': "I'm a grocery shopping assistant and can only help with food-related queries. Would you like help with your shopping list or a recipe instead?"
    }
    
    @classmethod
    def validate_prompt(cls, prompt: str, message_type: str) -> Dict[str, bool]:
        """Validate a prompt against safety policies."""
        validation_results = {
            'is_safe': True,
            'violations': [],
            'warnings': []
        }
        
        # Check for prohibited content
        for category, pattern in cls.PROHIBITED_PATTERNS.items():
            if re.search(pattern, prompt, re.IGNORECASE):
                validation_results['is_safe'] = False
                validation_results['violations'].append(f"Contains {category}")
                logger.warning(f"Prompt contains prohibited content: {category}")
        
        # Check for required content
        for category, pattern in cls.REQUIRED_PATTERNS.items():
            if not re.search(pattern, prompt, re.IGNORECASE):
                validation_results['warnings'].append(f"Missing {category}")
                logger.warning(f"Prompt missing required content: {category}")
        
        # Validate message type specific requirements
        if message_type == "Recipe type":
            if not re.search(r'\b(?:recipe|cook|prepare|make|ingredients)\b', prompt, re.IGNORECASE):
                validation_results['warnings'].append("Recipe prompt missing key terms")
        
        elif message_type == "Item Addition type":
            if not re.search(r'\b(?:add|put|include|shopping\slist)\b', prompt, re.IGNORECASE):
                validation_results['warnings'].append("Item addition prompt missing key terms")
        
        return validation_results
    
    @classmethod
    def sanitize_prompt(cls, prompt: str) -> str:
        """Sanitize a prompt by removing or replacing prohibited content."""
        sanitized_prompt = prompt
        
        # Remove prohibited content
        for pattern in cls.PROHIBITED_PATTERNS.values():
            sanitized_prompt = re.sub(pattern, '[REDACTED]', sanitized_prompt, flags=re.IGNORECASE)
        
        # Add required disclaimers if missing
        if not re.search(cls.REQUIRED_PATTERNS['disclaimer'], sanitized_prompt, re.IGNORECASE):
            sanitized_prompt = f"{cls.REQUIRED_PATTERNS['disclaimer']}. {sanitized_prompt}"
        
        return sanitized_prompt
    
    @classmethod
    def get_safe_response(cls, violation_type: str) -> str:
        """Get a safe response for a specific violation type."""
        return cls.SAFE_RESPONSES.get(violation_type, cls.SAFE_RESPONSES['out_of_scope'])
    
    @classmethod
    def add_safety_context(cls, prompt: str) -> str:
        """Add safety context to the prompt."""
        safety_context = """
        Safety Guidelines:
        1. Focus only on grocery shopping and recipes
        2. Do not provide medical, legal, or financial advice
        3. Do not discuss personal or sensitive topics
        4. Maintain professional and respectful tone
        5. Do not share confidential information
        6. Stay within the scope of food and shopping
        """
        return f"{safety_context}\n\n{prompt}" 