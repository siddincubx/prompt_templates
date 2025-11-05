"""
Web routes for serving HTML pages
"""
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from ..services.template_service import template_service

# Initialize templates
templates = Jinja2Templates(directory="templates")

web_router = APIRouter()

@web_router.get("/templates", response_class=HTMLResponse)
async def templates_list(request: Request, category: Optional[str] = None):
    """Templates listing page"""
    try:
        templates_data = await template_service.get_all_templates(category=category)
        categories = await template_service.get_categories()
        
        return templates.TemplateResponse("templates/list.html", {
            "request": request,
            "templates": templates_data,
            "categories": categories,
            "selected_category": category
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_router.get("/templates/create", response_class=HTMLResponse)
async def create_template_page(request: Request):
    """Create template page"""
    categories = await template_service.get_categories()
    return templates.TemplateResponse("templates/create.html", {
        "request": request,
        "categories": categories
    })

@web_router.get("/templates/{template_id}", response_class=HTMLResponse)
async def view_template(request: Request, template_id: int):
    """View single template page"""
    try:
        template = await template_service.get_template(template_id)
        return templates.TemplateResponse("templates/view.html", {
            "request": request,
            "template": template
        })
    except ValueError:
        raise HTTPException(status_code=404, detail="Template not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_router.get("/templates/{template_id}/use", response_class=HTMLResponse)
async def use_template_page(request: Request, template_id: int):
    """Use template page"""
    try:
        template = await template_service.get_template(template_id)
        return templates.TemplateResponse("templates/use.html", {
            "request": request,
            "template": template
        })
    except ValueError:
        raise HTTPException(status_code=404, detail="Template not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_router.get("/templates/{template_id}/edit", response_class=HTMLResponse)
async def edit_template_page(request: Request, template_id: int):
    """Edit template page"""
    try:
        template = await template_service.get_template(template_id)
        categories = await template_service.get_categories()
        return templates.TemplateResponse("templates/edit.html", {
            "request": request,
            "template": template,
            "categories": categories
        })
    except ValueError:
        raise HTTPException(status_code=404, detail="Template not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_router.post("/templates/create")
async def create_template_form(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    text: str = Form(...),
    category: str = Form(None)
):
    """Handle template creation form submission"""
    try:
        # Extract variables from template text
        variables = template_service._extract_variables_from_text(text)
        
        from ..models import TemplateCreate
        template_data = TemplateCreate(
            name=name,
            description=description or None,
            text=text,
            variables=variables,
            category=category or None
        )
        
        template = await template_service.create_template(template_data)
        return RedirectResponse(f"/templates/{template.id}", status_code=303)
        
    except ValueError as e:
        # Return to form with error
        categories = await template_service.get_categories()
        return templates.TemplateResponse("templates/create.html", {
            "request": request,
            "error": str(e),
            "form_data": {
                "name": name,
                "description": description,
                "text": text,
                "category": category
            },
            "categories": categories
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_router.post("/templates/{template_id}/edit")
async def edit_template_form(
    request: Request,
    template_id: int,
    name: str = Form(...),
    description: str = Form(""),
    text: str = Form(...),
    category: str = Form(None)
):
    """Handle template edit form submission"""
    try:
        # Extract variables from template text
        variables = template_service._extract_variables_from_text(text)
        
        from ..models import TemplateUpdate
        update_data = TemplateUpdate(
            name=name,
            description=description or None,
            text=text,
            variables=variables,
            category=category or None
        )
        
        template = await template_service.update_template(template_id, update_data)
        return RedirectResponse(f"/templates/{template.id}", status_code=303)
        
    except ValueError as e:
        # Return to form with error
        template = await template_service.get_template(template_id)
        categories = await template_service.get_categories()
        return templates.TemplateResponse("templates/edit.html", {
            "request": request,
            "template": template,
            "categories": categories,
            "error": str(e)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_router.post("/templates/{template_id}/delete")
async def delete_template_form(template_id: int):
    """Handle template deletion"""
    try:
        await template_service.delete_template(template_id)
        return RedirectResponse("/templates", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))