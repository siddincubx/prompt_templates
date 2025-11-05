# Prompt Template Engine - Project Plan

## Overview
A web application that allows users to save, manage, and reuse prompt templates with variables. Users can create new templates using AI generation or use existing templates by filling in variables to generate final prompts for LLMs.

## Core Features

### 1. Template Management
- **View Templates**: Browse all saved prompt templates
- **Create Templates**: Generate new templates using AI (existing `b.CreateTemplate()` function)
- **Use Templates**: Fill variables in existing templates to generate final prompts
- **Edit Templates**: Modify existing templates manually
- **Delete Templates**: Remove unwanted templates

### 2. Template Structure
- **Name**: Unique identifier for the template
- **Description**: Brief explanation of what the template does
- **Text**: EJS format template string with variables
- **Variables**: List of variable names used in the template
- **Category**: Optional categorization (e.g., "email", "product", "social")
- **Created Date**: Timestamp of creation
- **Usage Count**: Track how often template is used

## Technical Architecture

### Backend (Python FastAPI)
- **Framework**: FastAPI for REST API
- **Database**: SQLite for local storage
- **Template Engine**: Jinja2 for server-side rendering
- **AI Integration**: Existing `baml_client.b.CreateTemplate()` function

### Frontend
- **Rendering**: Server-side rendering with Jinja2
- **Interactivity**: HTMX for dynamic interactions
- **Styling**: DaisyUI (Tailwind CSS framework)
- **Template Processing**: EJS-like variable replacement

### Database Schema
```sql
-- Templates table
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    text TEXT NOT NULL,
    variables TEXT NOT NULL, -- JSON array of variable names
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);

-- Template usage history (optional for analytics)
CREATE TABLE template_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates (id)
);
```

## Project Structure
```
prompt_templates/
├── main.py                    # FastAPI application entry point
├── app/
│   ├── __init__.py
│   ├── database.py           # SQLite database setup and models
│   ├── models.py             # Pydantic models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── templates.py      # Template CRUD operations
│   │   └── api.py            # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── template_service.py # Business logic
│   │   └── ai_service.py     # AI template generation
│   └── utils.py              # Helper functions
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html             # Base template
│   ├── index.html            # Home page
│   ├── templates/
│   │   ├── list.html         # View all templates
│   │   ├── create.html       # Create new template
│   │   ├── use.html          # Use template form
│   │   ├── edit.html         # Edit template
│   │   └── view.html         # View single template
│   └── components/           # Reusable components
├── baml_client/              # Existing AI client
└── docs/
```

## Implementation Phases

### Phase 1: Database and Models Setup
1. Set up SQLite database with schema
2. Create Pydantic models for API
3. Implement database operations (CRUD)

### Phase 2: Core Backend API
1. FastAPI application setup
2. Template CRUD endpoints
3. Integration with existing `b.CreateTemplate()` function
4. EJS variable processing utilities

### Phase 3: Frontend Templates
1. Base HTML template with DaisyUI styling
2. Template listing page
3. Template creation form
4. Template usage form with dynamic variable inputs

### Phase 4: HTMX Integration
1. Dynamic form interactions
2. Real-time template preview
3. Inline editing capabilities
4. Search and filtering

### Phase 5: Enhancement Features
1. Template categorization
2. Usage analytics
3. Template import/export
4. Template sharing capabilities

## Key Pages and User Flows

### 1. Home Page (`/`)
- Welcome message
- Quick access to main features
- Recent templates
- Statistics (total templates, most used, etc.)

### 2. Templates List (`/templates`)
- Grid/list view of all templates
- Search and filter by category
- Quick actions (use, edit, delete)
- Pagination for large collections

### 3. Create Template (`/templates/create`)
- Form with requirement input
- AI generation using `b.CreateTemplate()`
- Preview generated template
- Edit before saving

### 4. Use Template (`/templates/{id}/use`)
- Display template information
- Dynamic form for all variables
- Real-time preview of final prompt
- Copy to clipboard functionality

### 5. Edit Template (`/templates/{id}/edit`)
- Form to modify template details
- Template text editor with syntax highlighting
- Variable list management

## API Endpoints

### Templates
- `GET /api/templates` - List all templates
- `POST /api/templates` - Create new template
- `GET /api/templates/{id}` - Get template by ID
- `PUT /api/templates/{id}` - Update template
- `DELETE /api/templates/{id}` - Delete template
- `POST /api/templates/{id}/use` - Generate prompt from template

### AI Generation
- `POST /api/generate-template` - Generate template using AI
- `POST /api/preview-template` - Preview template with variables

## Dependencies to Add
```toml
dependencies = [
    "baml-py>=0.212.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "jinja2>=3.1.0",
    "python-multipart>=0.0.6",
    "aiosqlite>=0.19.0",
    "pydantic>=2.0.0",
    "python-dateutil>=2.8.0"
]
```

## Next Steps
1. Update `pyproject.toml` with new dependencies
2. Implement database layer
3. Create FastAPI application structure
4. Build core templates and routes
5. Integrate HTMX for dynamic interactions
6. Style with DaisyUI components

This plan provides a solid foundation for building a comprehensive prompt template management system that leverages the existing AI capabilities while providing an intuitive web interface for users.