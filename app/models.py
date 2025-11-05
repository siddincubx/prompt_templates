"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TemplateBase(BaseModel):
    """Base template model"""
    name: str = Field(..., description="Unique name for the template")
    description: Optional[str] = Field(None, description="Brief description of the template")
    text: str = Field(..., description="Template text in EJS format")
    variables: List[str] = Field([], description="List of variable names used in the template")
    category: Optional[str] = Field(None, description="Template category")

class TemplateCreate(TemplateBase):
    """Model for creating a new template"""
    pass

class TemplateUpdate(BaseModel):
    """Model for updating an existing template"""
    name: Optional[str] = None
    description: Optional[str] = None
    text: Optional[str] = None
    variables: Optional[List[str]] = None
    category: Optional[str] = None

class Template(TemplateBase):
    """Full template model with metadata"""
    id: int
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    
    model_config = {"from_attributes": True}

class TemplateListItem(BaseModel):
    """Simplified template model for listing"""
    id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    created_at: datetime
    usage_count: int = 0
    variable_count: int = Field(..., description="Number of variables in the template")

class GenerateTemplateRequest(BaseModel):
    """Request model for AI template generation"""
    requirement: str = Field(..., description="Requirement description for template generation")
    name: Optional[str] = Field(None, description="Optional name for the template")
    category: Optional[str] = Field(None, description="Optional category for the template")

class GenerateTemplateResponse(BaseModel):
    """Response model for AI template generation"""
    text: str = Field(..., description="Generated template text")
    variables: List[str] = Field(..., description="Extracted variables from the template")
    suggested_name: Optional[str] = Field(None, description="AI suggested name for the template")
    suggested_category: Optional[str] = Field(None, description="AI suggested category")

class UseTemplateRequest(BaseModel):
    """Request model for using a template with variable values"""
    variable_values: dict = Field(..., description="Dictionary mapping variable names to values")

class UseTemplateResponse(BaseModel):
    """Response model for template usage"""
    final_prompt: str = Field(..., description="Final prompt with variables filled")
    template_name: str = Field(..., description="Name of the template used")
    variables_used: dict = Field(..., description="Variables and their values used")

class SearchTemplatesRequest(BaseModel):
    """Request model for searching templates"""
    query: str = Field(..., description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    limit: Optional[int] = Field(20, description="Maximum number of results")
    offset: Optional[int] = Field(0, description="Offset for pagination")

class TemplateStatsResponse(BaseModel):
    """Response model for template statistics"""
    total_templates: int
    total_usage: int
    most_used_template: Optional[dict]
    categories_count: int
    recent_templates: List[TemplateListItem]

class APIResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None
    errors: Optional[List[str]] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    errors: Optional[List[str]] = None
    error_code: Optional[str] = None