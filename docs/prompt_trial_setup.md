# Prompt Trial Feature Setup

The prompt trial feature allows users to test their generated prompts with different AI models. This document outlines the setup requirements.

## Environment Variables

To use the prompt trial feature, you need to configure the following environment variables in your `.env` file:

### For Gemini 2.0 Flash
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### For GPT-4
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Model Configuration

The feature currently supports two models:
- **Gemini 2.0 Flash**: Google's latest language model
- **GPT-4**: OpenAI's GPT-4 model

## BAML Client Registry

The implementation uses BAML's ClientRegistry to dynamically configure and switch between different AI providers at runtime. This allows for:

1. **Dynamic Model Selection**: Users can choose their preferred model from the dropdown
2. **Runtime Configuration**: API keys and model parameters are configured on-demand
3. **Error Handling**: Graceful handling of missing API keys or configuration issues

## Usage Flow

1. User generates a prompt using the template system
2. User clicks "Try Prompt" button
3. Modal opens with the generated prompt and model selection dropdown
4. User selects a model (Gemini 2.0 Flash or GPT-4)
6. User clicks "Run Trial"
7. System uses BAML ClientRegistry to configure the selected model
8. Prompt is sent to the selected AI model
9. Response is displayed in the right panel
10. Trial is rate-limited to 1 request per 10 seconds

## Implementation Details

### AI Service (`app/services/ai_service.py`)
- `do_prompt_trial()` method handles model selection using ClientRegistry
- Dynamically creates BAML client configurations for each model
- Sets the primary client based on user selection

### API Route (`app/routes/api.py`)
- `POST /api/templates/{template_id}/trial` endpoint
- Accepts form data with prompt text and selected model
- Returns JSON response with AI-generated text

### Frontend (`templates/templates/use.html`)
- Modal interface for prompt trial
- Model selection dropdown
- Real-time trial execution with loading states
- Rate limiting: 1 request per 10 seconds with countdown timer

## Error Handling

The system handles various error scenarios:
- Missing API keys (returns appropriate error message)
- Invalid model selection
- Network or API failures
- BAML configuration issues

## Dependencies

- `baml-py>=0.212.0`: Core BAML functionality
- `baml_py.ClientRegistry`: Runtime client configuration
- Environment variable access via `os.environ`