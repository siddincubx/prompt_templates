"""
AI service for template generation using BAML client
"""
import asyncio
import os
from typing import Dict, Any
from baml_client import b
from baml_py import ClientRegistry

class AIService:
    """Service for AI-powered template generation"""
    
    def __init__(self):
        # Verify BAML imports are working
        try:
            # Test ClientRegistry import
            ClientRegistry()
        except Exception as e:
            print(f"Warning: BAML ClientRegistry import failed: {e}")
    
    async def generate_template(self, requirement: str) -> Dict[str, Any]:
        """
        Generate a template using the BAML AI client
        
        Args:
            requirement: User's requirement description
            
        Returns:
            Dictionary with 'text' and 'variables' keys
        """
        try:
            # Run the synchronous BAML function in an executor to make it async
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, b.CreateTemplate, requirement)
            
            return {
                "text": result.text,
                "variables": result.variables,
                "suggested_name": result.title,
                "suggested_category": result.category
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate template: {str(e)}")
    
    async def do_prompt_trial(self, prompt_text: str, model: str = None) -> Dict[str, Any]:
        """
        Test a prompt using the BAML AI client with specified model
        
        Args:
            prompt_text: The generated prompt text to test
            model: The model to use ('gemini-2.0-flash' or 'gpt-4')
            
        Returns:
            Dictionary with 'text' key containing the AI response
        """
        try:
            # Create a client registry to select the model
            client_registry = ClientRegistry()
            
            # Map frontend model names to BAML client configurations
            # Model configuration mapping
            model_configs = {
                "gemini-2.0-flash": {
                    'provider': 'google-ai',
                    'model': 'gemini-2.0-flash',
                    'api_key_env': 'GEMINI_API_KEY'
                },
                "gemini-2.5-pro": {
                    'provider': 'google-ai',
                    'model': 'gemini-2.5-pro',
                    'api_key_env': 'GEMINI_API_KEY'
                },
                "gpt-4": {
                    'provider': 'openai',
                    'model': 'gpt-4',
                    'api_key_env': 'OPENAI_API_KEY'
                }
            }
            
            if model not in model_configs:
                raise Exception("Please select a valid model from the options")
            
            config = model_configs[model]
            api_key = os.environ.get(config['api_key_env'])
            if not api_key:
                raise Exception(f"{config['api_key_env']} not configured")
            
            client_registry.add_llm_client(
                name='TrialClient',
                provider=config['provider'],
                options={
                    'model': config['model'],
                    'api_key': api_key
                }
            )
            
            # Set the primary client
            client_registry.set_primary('TrialClient')
            
            # Run the synchronous BAML function in an executor to make it async
            loop = asyncio.get_event_loop()
            
            # Use client registry with the specific model
            result = await loop.run_in_executor(
                None, 
                lambda: b.DoPromptTrial(prompt_text, baml_options={"client_registry": client_registry})
            )
            
            return {
                "text": result.text
            }
            
        except Exception as e:
            raise Exception(f"Failed to perform prompt trial: {str(e)}")
    
    def _suggest_name_from_requirement(self, requirement: str) -> str:
        """
        Generate a suggested name based on the requirement
        
        Args:
            requirement: User's requirement description
            
        Returns:
            Suggested template name
        """
        # Simple name suggestion based on keywords
        requirement_lower = requirement.lower()
        
        # Common patterns and their suggested names
        patterns = {
            "email": "email-template",
            "invitation": "invitation-template", 
            "apology": "apology-template",
            "product description": "product-description-template",
            "social media": "social-media-template",
            "blog post": "blog-post-template",
            "newsletter": "newsletter-template",
            "announcement": "announcement-template",
            "marketing": "marketing-template",
            "sales": "sales-template",
            "customer service": "customer-service-template",
            "review": "review-template",
            "feedback": "feedback-template"
        }
        
        for pattern, suggested_name in patterns.items():
            if pattern in requirement_lower:
                return suggested_name
        
        # Fallback: generate name from first few words
        words = requirement.split()[:3]
        name = "-".join(w.lower().strip(".,!?;:") for w in words if w.isalnum())
        return f"{name}-template" if name else "custom-template"
    
    def _suggest_category_from_requirement(self, requirement: str) -> str:
        """
        Suggest a category based on the requirement
        
        Args:
            requirement: User's requirement description
            
        Returns:
            Suggested category
        """
        requirement_lower = requirement.lower()
        
        # Category mapping
        categories = {
            "email": "Email",
            "invitation": "Email", 
            "apology": "Communication",
            "product": "E-commerce",
            "social media": "Social Media",
            "blog": "Content",
            "newsletter": "Marketing",
            "announcement": "Communication",
            "marketing": "Marketing",
            "sales": "Sales",
            "customer": "Customer Service",
            "review": "Feedback",
            "feedback": "Feedback",
            "educational": "Education",
            "technical": "Technical",
            "creative": "Creative"
        }
        
        for keyword, category in categories.items():
            if keyword in requirement_lower:
                return category
        
        return "General"

# Global AI service instance
ai_service = AIService()