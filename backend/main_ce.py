"""
Main FastAPI Server for Experiment Generator
Entry point of the application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import os

# Import from create_experiment module
from create_experiment.ollama_client import OllamaClient
from create_experiment.prompt_engine import PromptEngine
from create_experiment.validator import ConfigValidator
from create_experiment.code_generator import CodeGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Experiment Generator API",
    description="Generate interactive simulations from natural language",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ollama_client = OllamaClient()
prompt_engine = PromptEngine()
validator = ConfigValidator()
code_generator = CodeGenerator()


# Request/Response Models
class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500, description="Natural language description")
    template_hint: Optional[str] = Field(None, description="Suggest a specific template")


class GenerateResponse(BaseModel):
    success: bool
    config: Optional[Dict[str, Any]] = None
    html_code: Optional[str] = None
    error: Optional[str] = None
    suggestions: Optional[List[str]] = None


class TemplateInfo(BaseModel):
    id: str
    name: str
    description: str
    params: Dict[str, Any]
    examples: List[str]


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Experiment Generator API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "templates": "/templates",
            "generate": "/generate",
            "preview": "/preview/{experiment_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Check system health and Ollama status"""
    try:
        ollama_status = await ollama_client.health_check()
        return {
            "status": "healthy" if ollama_status else "degraded",
            "ollama_running": ollama_status,
            "model": "qwen2.5-coder:7b",
            "templates_available": len(code_generator.get_available_templates())
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/templates", response_model=List[TemplateInfo])
async def list_templates():
    """Get all available templates"""
    try:
        templates = code_generator.get_available_templates()
        return templates
    except Exception as e:
        logger.error(f"Error fetching templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate", response_model=GenerateResponse)
async def generate_experiment(request: GenerateRequest):
    """
    Generate experiment from natural language prompt
    
    Process:
    1. Build AI prompt with context
    2. Call Ollama to generate config
    3. Validate configuration
    4. Generate HTML/JS code
    5. Return complete working code
    """
    try:
        logger.info(f"Received generation request: '{request.prompt}'")
        
        # Step 1: Build enhanced prompt
        # Try to extract title and description from prompt if they're in "Title: X\nDescription: Y" format
        title = None
        description = None
        prompt_text = request.prompt
        
        # Check if prompt contains "Title:" and "Description:" format
        if "Title:" in prompt_text and "Description:" in prompt_text:
            lines = prompt_text.split("\n")
            for line in lines:
                if line.startswith("Title:"):
                    title = line.replace("Title:", "").strip()
                elif line.startswith("Description:"):
                    description = line.replace("Description:", "").strip()
            # Remove title/description lines and use the rest as prompt
            prompt_text = "\n".join([l for l in lines if not l.startswith("Title:") and not l.startswith("Description:")]).strip()
            if not prompt_text:
                # If nothing left, combine title and description
                prompt_text = f"{title}. {description}" if title and description else (title or description or request.prompt)
        
        ai_prompt = prompt_engine.build_prompt(
            user_prompt=prompt_text,
            template_hint=request.template_hint,
            title=title,
            description=description
        )
        
        # Step 2: Generate config using AI
        logger.info("Calling Ollama AI...")
        raw_response = await ollama_client.generate(ai_prompt)
        
        # Step 3: Extract JSON config
        config_dict = prompt_engine.extract_json(raw_response)
        
        if not config_dict:
            return GenerateResponse(
                success=False,
                error="Could not parse valid configuration from AI response",
                suggestions=[
                    "Try being more specific in your prompt",
                    "Include keywords like 'network', 'particles', or 'waves'",
                    "Example: 'Create a network with 10 nodes and fast routing'"
                ]
            )
        
        # Step 4: Validate configuration
        is_valid, error_msg = validator.validate(config_dict)
        
        if not is_valid:
            logger.warning(f"Invalid config: {error_msg}")
            return GenerateResponse(
                success=False,
                error=f"Invalid configuration: {error_msg}",
                suggestions=["Please rephrase your request and try again"]
            )
        
        # Step 5: Generate HTML code
        logger.info(f"Generating code for template: {config_dict['template']}")
        html_code = code_generator.generate_html(config_dict)
        
        if not html_code:
            return GenerateResponse(
                success=False,
                error="Failed to generate experiment code",
                suggestions=["The selected template might not be fully implemented"]
            )
        
        logger.info("Successfully generated experiment!")
        
        return GenerateResponse(
            success=True,
            config=config_dict,
            html_code=html_code
        )
        
    except Exception as e:
        logger.error(f"Error in generate_experiment: {e}", exc_info=True)
        return GenerateResponse(
            success=False,
            error=f"Internal error: {str(e)}",
            suggestions=["Please try again with a different prompt"]
        )


@app.get("/preview/{experiment_id}", response_class=HTMLResponse)
async def preview_experiment(experiment_id: str):
    """
    Preview a generated experiment
    (In production, you'd store experiments in DB and retrieve by ID)
    """
    # For now, return a placeholder
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Experiment Preview</title>
    </head>
    <body>
        <h1>Experiment Preview</h1>
        <p>Experiment ID: {}</p>
        <p>Use the /generate endpoint to create new experiments</p>
    </body>
    </html>
    """.format(experiment_id)


@app.post("/download")
async def download_experiment(config: Dict[str, Any]):
    """
    Generate and return downloadable HTML file
    """
    try:
        # Validate config
        is_valid, error_msg = validator.validate(config)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Generate HTML
        html_code = code_generator.generate_html(config)
        
        if not html_code:
            raise HTTPException(status_code=500, detail="Failed to generate HTML")
        
        # Return as downloadable file
        from fastapi.responses import Response
        
        filename = f"{config['template']}_experiment.html"
        
        return Response(
            content=html_code,
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating download: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    # Create necessary directories
    os.makedirs("create_experiment/templates", exist_ok=True)
    
    logger.info("Starting Experiment Generator API...")
    logger.info("Make sure Ollama is running: ollama serve")
    logger.info("Make sure model is available: ollama pull qwen2.5-coder:7b")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
