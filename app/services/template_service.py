"""
Template service for business logic and template processing
"""
import re
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database import db_manager
from ..models import (
    Template, TemplateCreate, TemplateUpdate, TemplateListItem,
    GenerateTemplateRequest, GenerateTemplateResponse,
    UseTemplateRequest, UseTemplateResponse,
    TemplateStatsResponse
)
from .ai_service import ai_service

class TemplateService:
    """Service for template operations and business logic"""
    
    def __init__(self):
        self.db = db_manager
    
    async def create_template(self, template_data: TemplateCreate) -> Template:
        """Create a new template"""
        try:
            # Check if name already exists
            existing = await self.db.get_template_by_name(template_data.name)
            if existing:
                raise ValueError(f"Template with name '{template_data.name}' already exists")
            
            # Validate variables in template text
            detected_variables = self._extract_variables_from_text(template_data.text)
            if set(detected_variables) != set(template_data.variables):
                # Auto-correct variables list based on detected variables
                template_data.variables = detected_variables
            
            template_id = await self.db.create_template(
                name=template_data.name,
                description=template_data.description,
                text=template_data.text,
                variables=template_data.variables,
                category=template_data.category
            )
            
            return await self.get_template(template_id)
            
        except Exception as e:
            raise Exception(f"Failed to create template: {str(e)}")
    
    async def get_template(self, template_id: int) -> Template:
        """Get a template by ID"""
        template_data = await self.db.get_template(template_id)
        if not template_data:
            raise ValueError(f"Template with ID {template_id} not found")
        
        return Template(**template_data)
    
    async def get_template_by_name(self, name: str) -> Template:
        """Get a template by name"""
        template_data = await self.db.get_template_by_name(name)
        if not template_data:
            raise ValueError(f"Template with name '{name}' not found")
        
        return Template(**template_data)
    
    async def get_all_templates(self, category: str = None, 
                               limit: int = None, offset: int = 0) -> List[TemplateListItem]:
        """Get all templates with optional filtering"""
        templates_data = await self.db.get_all_templates(category, limit, offset)
        
        templates = []
        for template_data in templates_data:
            template_item = TemplateListItem(
                id=template_data["id"],
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                created_at=template_data["created_at"],
                usage_count=template_data["usage_count"],
                variable_count=len(template_data["variables"])
            )
            templates.append(template_item)
        
        return templates
    
    async def update_template(self, template_id: int, update_data: TemplateUpdate) -> Template:
        """Update a template"""
        # Check if template exists
        existing = await self.get_template(template_id)
        
        # If text is being updated, validate variables
        if update_data.text is not None:
            detected_variables = self._extract_variables_from_text(update_data.text)
            if update_data.variables is None:
                update_data.variables = detected_variables
            elif set(detected_variables) != set(update_data.variables):
                # Auto-correct variables list
                update_data.variables = detected_variables
        
        # Check for name conflicts if name is being updated
        if update_data.name and update_data.name != existing.name:
            existing_by_name = await self.db.get_template_by_name(update_data.name)
            if existing_by_name:
                raise ValueError(f"Template with name '{update_data.name}' already exists")
        
        success = await self.db.update_template(
            template_id=template_id,
            name=update_data.name,
            description=update_data.description,
            text=update_data.text,
            variables=update_data.variables,
            category=update_data.category
        )
        
        if not success:
            raise Exception("Failed to update template")
        
        return await self.get_template(template_id)
    
    async def delete_template(self, template_id: int) -> bool:
        """Delete a template"""
        # Check if template exists
        await self.get_template(template_id)
        
        return await self.db.delete_template(template_id)
    
    async def use_template(self, template_id: int, variable_values: Dict[str, Any]) -> UseTemplateResponse:
        """Use a template by filling in variables"""
        template = await self.get_template(template_id)
        
        # Validate that all required variables are provided
        missing_variables = set(template.variables) - set(variable_values.keys())
        if missing_variables:
            raise ValueError(f"Missing values for variables: {', '.join(missing_variables)}")
        
        # Generate final prompt by replacing variables
        final_prompt = self._fill_template_variables(template.text, variable_values)
        
        # Increment usage count
        await self.db.increment_usage_count(template_id)
        
        return UseTemplateResponse(
            final_prompt=final_prompt,
            template_name=template.name,
            variables_used=variable_values
        )
    
    async def generate_template_from_ai(self, request: GenerateTemplateRequest) -> GenerateTemplateResponse:
        """Generate a template using AI"""
        try:
            ai_result = await ai_service.generate_template(request.requirement)
            
            return GenerateTemplateResponse(
                text=ai_result["text"],
                variables=ai_result["variables"],
                suggested_name=request.name or ai_result["suggested_name"],
                suggested_category=request.category or ai_result["suggested_category"]
            )
            
        except Exception as e:
            raise Exception(f"Failed to generate template: {str(e)}")
    
    async def search_templates(self, query: str) -> List[TemplateListItem]:
        """Search templates"""
        templates_data = await self.db.search_templates(query)
        
        templates = []
        for template_data in templates_data:
            template_item = TemplateListItem(
                id=template_data["id"],
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                created_at=template_data["created_at"],
                usage_count=template_data["usage_count"],
                variable_count=len(template_data["variables"])
            )
            templates.append(template_item)
        
        return templates
    
    async def get_categories(self) -> List[str]:
        """Get all template categories"""
        return await self.db.get_categories()
    
    async def get_stats(self) -> TemplateStatsResponse:
        """Get template statistics"""
        stats = await self.db.get_stats()
        recent_templates = await self.get_all_templates(limit=5)
        
        return TemplateStatsResponse(
            total_templates=stats["total_templates"],
            total_usage=stats["total_usage"],
            most_used_template=stats["most_used_template"],
            categories_count=stats["categories_count"],
            recent_templates=recent_templates
        )
    
    def _extract_variables_from_text(self, text: str) -> List[str]:
        """
        Extract variable names from EJS template text
        
        Looks for patterns like <%= variableName %>
        """
        # Regular expression to match EJS variables
        pattern = r'<%=\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*%>'
        matches = re.findall(pattern, text)
        
        # Remove duplicates and return sorted list
        return sorted(list(set(matches)))
    
    def _fill_template_variables(self, template_text: str, variables: Dict[str, Any]) -> str:
        """
        Fill template variables with provided values
        
        Replaces <%= variableName %> with actual values
        """
        result = template_text
        
        for var_name, var_value in variables.items():
            # Handle different variable formats
            patterns = [
                f"<%=\\s*{var_name}\\s*%>",  # <%= varName %>
                f"<%\\s*=\\s*{var_name}\\s*%>",  # <% = varName %>
            ]
            
            for pattern in patterns:
                result = re.sub(pattern, str(var_value), result)
        
        return result
    
    async def preview_template(self, template_text: str, variables: Dict[str, Any]) -> str:
        """Preview a template with given variables without saving"""
        # Extract variables from text to validate
        detected_variables = self._extract_variables_from_text(template_text)
        
        # Check for missing variables
        missing_variables = set(detected_variables) - set(variables.keys())
        if missing_variables:
            # Fill missing variables with placeholder
            for var in missing_variables:
                variables[var] = f"[{var}]"
        
        return self._fill_template_variables(template_text, variables)

# Global template service instance
template_service = TemplateService()