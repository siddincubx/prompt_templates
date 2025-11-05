# Prompt Template Engine

A comprehensive web application for creating, managing, and using prompt templates with AI assistance. Built with FastAPI, HTMX, and DaisyUI.

## Features

- 🤖 **AI-Powered Template Generation**: Generate templates using natural language descriptions
- 📝 **Manual Template Creation**: Create templates from scratch with full control
- 🔄 **Template Reusability**: Save and reuse templates with variable substitution
- 🎨 **Beautiful UI**: Modern, responsive interface built with DaisyUI and Tailwind CSS
- ⚡ **Real-time Interactions**: Dynamic updates using HTMX
- 🔍 **Search & Filter**: Find templates quickly by name, category, or content
- 📊 **Usage Analytics**: Track template usage and popularity
- 💾 **Local Storage**: SQLite database for fast, local data storage

## Quick Start

### Prerequisites

- Python 3.13+
- uv package manager

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd prompt_templates
   ```

2. **Install dependencies using uv**:
   ```bash
   uv sync
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Open your browser**:
   Navigate to `http://127.0.0.1:8000`

### First Steps

1. **Create your first template**:
   - Go to `/templates/create`
   - Choose "AI Generate" tab
   - Describe what you want: e.g., "I want to generate personalized email invitations for events"
   - Click "Generate Template"
   - Review and save the generated template

2. **Use a template**:
   - Browse templates at `/templates`
   - Click "Use Template" on any template
   - Fill in the variable values
   - Copy the generated prompt

## Project Structure

```
prompt_templates/
├── app/                    # Application code
│   ├── database.py        # SQLite database management
│   ├── models.py         # Pydantic data models
│   ├── routes/           # API and web routes
│   │   ├── api.py       # REST API endpoints
│   │   └── web.py       # Web page routes
│   └── services/        # Business logic
│       ├── ai_service.py      # AI template generation
│       └── template_service.py # Template operations
├── templates/            # Jinja2 HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   └── templates/       # Template-related pages
├── static/              # Static assets (CSS, JS)
├── baml_client/         # AI client (BAML)
├── main.py             # Application entry point
└── pyproject.toml      # Project configuration
```

## API Endpoints

### Templates
- `GET /api/templates` - List all templates
- `POST /api/templates` - Create new template
- `GET /api/templates/{id}` - Get specific template
- `PUT /api/templates/{id}` - Update template
- `DELETE /api/templates/{id}` - Delete template
- `POST /api/templates/{id}/use` - Use template with variables

### AI Generation
- `POST /api/generate-template` - Generate template using AI

### Utilities
- `GET /api/categories` - Get all categories
- `GET /api/stats` - Get usage statistics
- `GET /api/templates/search/{query}` - Search templates

## Web Pages

- `/` - Home page with statistics and quick actions
- `/templates` - Browse all templates with search and filters
- `/templates/create` - Create new templates (AI or manual)
- `/templates/{id}` - View template details
- `/templates/{id}/use` - Use template with variable input form
- `/templates/{id}/edit` - Edit existing template

## Template Syntax

Templates use EJS-style syntax for variables:

```
Generate a professional email to <%= recipientName %> about <%= subject %>.
The meeting is scheduled for <%= meetingDate %> at <%= location %>.
```

Variables are automatically detected and users can fill them in when using the template.

## Testing

Run the core functionality test:
```bash
python test_core.py
```

Run the comprehensive web application test (server must be running):
```bash
python test_app.py
```

## Configuration

The application uses SQLite by default and stores the database file as `templates.db` in the project root. No additional configuration is required for basic usage.

## Technologies Used

- **Backend**: FastAPI, SQLite, Pydantic
- **Frontend**: Jinja2, HTMX, DaisyUI, Tailwind CSS
- **AI**: BAML client for template generation
- **Package Management**: uv

## Development

### Adding New Features

1. **Database changes**: Update schema in `app/database.py`
2. **API endpoints**: Add routes in `app/routes/api.py`
3. **Web pages**: Create templates in `templates/`
4. **Business logic**: Implement in `app/services/`

### Styling

The application uses DaisyUI components with Tailwind CSS. Custom styles are in `static/css/custom.css`.

### JavaScript

Interactive features use HTMX for server communication and custom JavaScript in `static/js/app.js`.

## Troubleshooting

### Common Issues

1. **Server won't start**: Ensure all dependencies are installed with `uv sync`
2. **AI generation fails**: Check BAML client configuration in `baml_client/`
3. **Database errors**: Delete `templates.db` to reset the database
4. **Port conflicts**: Change the port in `main.py` if 8000 is occupied

### Logs

The application logs to the console. Start with `python main.py` to see detailed logs.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.
