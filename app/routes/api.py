"""
API routes for template operations
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
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

@api_router.post("/templates/{template_id}/trial")
async def trial_prompt(template_id: int, request: Request):
    """Trial a generated prompt with selected AI model"""
    try:
        form_data = await request.form()
        
        # Extract data from form
        prompt_text = form_data.get('prompt_text', '')
        selected_model = form_data.get('model', '')
        
        print(f"Trial request - prompt_text length: {len(prompt_text)}, model: {selected_model}")  # Debug log
        
        if not prompt_text.strip():
            from fastapi.responses import JSONResponse
            return JSONResponse(content={"error": "No prompt text provided"}, status_code=400)
        
        if not selected_model:
            from fastapi.responses import JSONResponse
            return JSONResponse(content={"error": "No model selected"}, status_code=400)
        
        # Use AI service to trial the prompt
        from ..services.ai_service import ai_service
        result = await ai_service.do_prompt_trial(prompt_text, selected_model)
        
        # Return JSON response for HTMX to handle
        from fastapi.responses import JSONResponse
        return JSONResponse(content={
            "text": result["text"],
            "model_used": selected_model,
            "prompt_text": prompt_text
        })
        
    except ValueError as e:
        print(f"ValueError in trial_prompt: {e}")  # Debug log
        from fastapi.responses import JSONResponse
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except Exception as e:
        print(f"Error in trial_prompt: {e}")  # Debug log
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

@api_router.get("/stats/html", response_class=HTMLResponse)
async def get_stats_html():
    """Get template statistics as HTML"""
    try:
        stats = await template_service.get_stats()
        
        # Format numbers for display
        def format_number(num):
            if num >= 1000000:
                return f"{num/1000000:.1f}M"
            elif num >= 1000:
                return f"{num/1000:.1f}K"
            else:
                return str(num)
        
        # Handle most used template display
        most_used_name = stats.most_used_template.get('name', 'None') if stats.most_used_template else 'None'
        most_used_count = stats.most_used_template.get('usage_count', 0) if stats.most_used_template else 0
        
        # Truncate long template names
        display_name = most_used_name
        if len(most_used_name) > 15:
            display_name = most_used_name[:12] + '...'
        
        # Calculate progress percentages
        usage_progress = min(stats.total_usage / max(stats.total_templates * 20, 1) * 100, 100) if stats.total_templates > 0 else 0
        popular_progress = min(most_used_count / max(stats.total_usage, 1) * 100, 100) if stats.total_usage > 0 else 0
        category_progress = min(stats.categories_count / 15 * 100, 100)  # Assume 15 is a good max
        
        # Create HTML for stats cards
        html = f"""
        <div class="stats-card stats-card-primary">
            <div class="stats-card-icon text-primary">
                <i class="fas fa-file-alt"></i>
            </div>
            <div class="stats-card-value number-animated">{stats.total_templates}</div>
            <div class="stats-card-label">Total Templates</div>
            <div class="stats-card-description">Available for use</div>
            <div class="stat-progress">
                <div class="stat-progress-fill" style="width: 100%;"></div>
            </div>
        </div>
        
        <div class="stats-card stats-card-secondary">
            <div class="stats-card-icon text-secondary">
                <i class="fas fa-chart-line"></i>
            </div>
            <div class="stats-card-value number-animated">{format_number(stats.total_usage)}</div>
            <div class="stats-card-label">Total Usage</div>
            <div class="stats-card-description">Templates executed</div>
            <div class="stat-progress">
                <div class="stat-progress-fill" style="width: {usage_progress:.1f}%;"></div>
            </div>
        </div>
        
        <div class="stats-card stats-card-accent">
            <div class="stats-card-icon text-accent">
                <i class="fas fa-star"></i>
            </div>
            <div class="stats-card-value text-sm font-medium" title="{most_used_name}">{display_name}</div>
            <div class="stats-card-label">Most Popular</div>
            <div class="stats-card-description">{most_used_count} uses</div>
            <div class="stat-progress">
                <div class="stat-progress-fill" style="width: {popular_progress:.1f}%;"></div>
            </div>
        </div>
        
        <div class="stats-card stats-card-info">
            <div class="stats-card-icon text-info">
                <i class="fas fa-tags"></i>
            </div>
            <div class="stats-card-value number-animated">{stats.categories_count}</div>
            <div class="stats-card-label">Categories</div>
            <div class="stats-card-description">Organized groups</div>
            <div class="stat-progress">
                <div class="stat-progress-fill" style="width: {category_progress:.1f}%;"></div>
            </div>
        </div>
        """
        
        return HTMLResponse(content=html)
    except Exception as e:
        error_html = """
        <div class="col-span-full text-center py-8">
            <div class="alert alert-error">
                <i class="fas fa-exclamation-triangle"></i>
                <span>Failed to load statistics. Please try again later.</span>
            </div>
        </div>
        """
        return HTMLResponse(content=error_html, status_code=200)

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