"""
API routes for template operations
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional

from ..models import (
    Template, TemplateCreate, TemplateUpdate, TemplateListItem,
    GenerateTemplateRequest, GenerateTemplateResponse,
    UseTemplateRequest, UseTemplateResponse,
    APIResponse, ErrorResponse, TemplateStatsResponse
)
from ..services.template_service import template_service

api_router = APIRouter()

@api_router.get("/templates", response_model=List[TemplateListItem])
async def get_templates(
    category: Optional[str] = None,
    limit: Optional[int] = 20,
    offset: int = 0
):
    """Get all templates with optional filtering"""
    try:
        templates = await template_service.get_all_templates(category, limit, offset)
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/templates/{template_id}", response_model=Template)
async def get_template(template_id: int):
    """Get a specific template by ID"""
    try:
        template = await template_service.get_template(template_id)
        return template
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/templates", response_model=Template)
async def create_template(template_data: TemplateCreate):
    """Create a new template"""
    try:
        template = await template_service.create_template(template_data)
        return template
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/templates/{template_id}", response_model=Template)
async def update_template(template_id: int, update_data: TemplateUpdate):
    """Update a template"""
    try:
        template = await template_service.update_template(template_id, update_data)
        return template
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/templates/{template_id}", response_model=APIResponse)
async def delete_template(template_id: int):
    """Delete a template"""
    try:
        success = await template_service.delete_template(template_id)
        if success:
            return APIResponse(message="Template deleted successfully")
        else:
            raise HTTPException(status_code=500, detail="Failed to delete template")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/templates/{template_id}/use", response_model=UseTemplateResponse)
async def use_template(template_id: int, request: UseTemplateRequest):
    """Use a template with provided variable values (JSON)"""
    try:
        result = await template_service.use_template(template_id, request.variable_values)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/templates/{template_id}/use-form")
async def use_template_form(template_id: int, request: Request):
    """Use a template with provided variable values (form data)"""
    try:
        form_data = await request.form()
        
        # Parse form data to extract variable_values
        variable_values = {}
        for key, value in form_data.items():
            if key.startswith('variable_values.'):
                variable_name = key.replace('variable_values.', '')
                variable_values[variable_name] = value
        
        print(f"Parsed variable values: {variable_values}")  # Debug log
        
        result = await template_service.use_template(template_id, variable_values)
        
        # Return JSON response for HTMX to handle
        from fastapi.responses import JSONResponse
        return JSONResponse(content={
            "final_prompt": result.final_prompt,
            "template_name": result.template_name,
            "variables_used": result.variables_used
        })
        
    except ValueError as e:
        print(f"ValueError in use_template_form: {e}")  # Debug log
        from fastapi.responses import JSONResponse
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except Exception as e:
        print(f"Error in use_template_form: {e}")  # Debug log
        from fastapi.responses import JSONResponse
        return JSONResponse(content={"error": str(e)}, status_code=500)

@api_router.post("/generate-template", response_model=GenerateTemplateResponse)
async def generate_template(request: GenerateTemplateRequest):
    """Generate a template using AI"""
    try:
        print(f"Received template generation request: {request}")  # Debug log
        result = await template_service.generate_template_from_ai(request)
        print(f"Generated template result: {result}")  # Debug log
        return result
    except Exception as e:
        print(f"Error in generate_template: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/templates/search/{query}", response_model=List[TemplateListItem])
async def search_templates(query: str):
    """Search templates by name or description"""
    try:
        templates = await template_service.search_templates(query)
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/categories", response_model=List[str])
async def get_categories():
    """Get all template categories"""
    try:
        categories = await template_service.get_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/stats", response_model=TemplateStatsResponse)
async def get_stats():
    """Get template statistics"""
    try:
        stats = await template_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/preview-template")
async def preview_template(template_text: str, variables: dict):
    """Preview a template with given variables (JSON)"""
    try:
        result = await template_service.preview_template(template_text, variables)
        return {"preview": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/preview-template-form")
async def preview_template_form(request: Request):
    """Preview a template with given variables (form data)"""
    try:
        form_data = await request.form()
        print(f"Preview form data keys: {list(form_data.keys())}")  # Debug
        
        # Get template text from form data
        template_text = form_data.get('text', '')
        if not template_text:
            template_text = form_data.get('template_text', '')
        
        print(f"Template text length: {len(template_text)}")  # Debug
        
        # Parse any preview variables (if included)
        variables = {}
        for key, value in form_data.items():
            if key.startswith('preview-vars.'):
                var_name = key.replace('preview-vars.', '')
                variables[var_name] = value
        
        print(f"Preview request - variables: {variables}")  # Debug
        
        # If no variables provided, extract them from template and use sample values
        if not variables and template_text:
            import re
            variable_pattern = r'<%=\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*%>'
            found_variables = re.findall(variable_pattern, template_text)
            for var in found_variables:
                variables[var] = f"[{var.upper()}]"
        
        if not template_text.strip():
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content='<p class="text-base-content/50 italic">Start typing your template to see a preview...</p>')
        
        result = await template_service.preview_template(template_text, variables)
        
        # Return HTML for the preview
        from fastapi.responses import HTMLResponse
        escaped_result = result.replace('<', '&lt;').replace('>', '&gt;')  # Escape HTML
        return HTMLResponse(content=f'<pre class="whitespace-pre-wrap font-mono text-sm">{escaped_result}</pre>')
        
    except Exception as e:
        print(f"Error in preview_template_form: {e}")  # Debug log
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Traceback: {traceback_str}")  # Debug log
        from fastapi.responses import HTMLResponse
        error_msg = f'Preview error: {str(e)}'
        return HTMLResponse(content=f'<p class="text-error text-sm">{error_msg}</p>', status_code=200)  # Changed to 200 to avoid HTMX errors

@api_router.get("/test-preview")
async def test_preview():
    """Test the preview functionality"""
    try:
        test_text = "Hello <%= name %>, welcome to <%= company %>!"
        test_vars = {"name": "John", "company": "Acme Corp"}
        result = await template_service.preview_template(test_text, test_vars)
        return {"test_text": test_text, "test_vars": test_vars, "result": result}
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@api_router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "message": "API is working"}

@api_router.post("/test-generate")
async def test_generate_template(requirement: str):
    """Test endpoint for template generation"""
    try:
        from ..models import GenerateTemplateRequest
        request = GenerateTemplateRequest(requirement=requirement)
        result = await template_service.generate_template_from_ai(request)
        return result
    except Exception as e:
        return {"error": str(e), "requirement": requirement}

@api_router.get("/test-page")
async def serve_test_page():
    """Serve the API test page"""
    from fastapi.responses import HTMLResponse
    try:
        with open("test_page.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Test page not found</h1><p>The test_page.html file is missing.</p>")

@api_router.get("/debug/test-baml")
async def test_baml_endpoint():
    """Debug endpoint to test BAML integration directly"""
    try:
        from ..services.ai_service import AIService
        ai_service = AIService()
        result = await ai_service.generate_template("Test requirement: Create a simple welcome email")
        return {
            "status": "success",
            "baml_result": result,
            "message": "BAML integration working"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "BAML integration failed"
        }