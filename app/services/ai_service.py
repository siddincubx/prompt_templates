"""
AI service for template generation using BAML client
"""
import asyncio
from typing import Dict, Any
from baml_client import b

class AIService:
    """Service for AI-powered template generation"""
    
    def __init__(self):
        pass
    
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
                "suggested_name": self._suggest_name_from_requirement(requirement),
                "suggested_category": self._suggest_category_from_requirement(requirement)
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate template: {str(e)}")
    
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