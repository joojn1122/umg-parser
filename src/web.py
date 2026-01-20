import os
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from parser import UMGParser, UMGParserConfig
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import traceback

from dotenv import load_dotenv
load_dotenv()

import logging

logger = logging.getLogger("umg-parser")

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",")

DEV = False

app = FastAPI(
    root_path="/umg-parser",
    title="UMG Parser API",
    description="Converts UMG Widget blueprints to Verse code",
    version="1.0.0",
    docs_url="/docs" if DEV else None,
    redoc_url="/redoc" if DEV else None,
    openapi_url="/openapi.json" if DEV else None
)

# Add CORS middleware
if ALLOWED_ORIGINS and ALLOWED_ORIGINS[0]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["POST"],
        allow_headers=["Content-Type"],
        max_age=600,
    )

# Request model with validation
class UMGRequest(BaseModel):
    umg_text: str = Field(
        ...,
        min_length=1,
        description="The UMG Widget blueprint text to convert"
    )
    use_translated: bool = Field(
        default=False,
        description="Whether to use translation keys for messages"
    )
    
    @field_validator('umg_text')
    @classmethod
    def validate_umg_text(cls, v: str) -> str:
        # Basic validation - must contain expected UMG markers
        if "Begin Object" not in v:
            raise ValueError("Invalid UMG format: missing 'Begin Object'")
        if "End Object" not in v:
            raise ValueError("Invalid UMG format: missing 'End Object'")
        return v

# Response models
class SuccessResponse(BaseModel):
    verse_code: str

class ErrorResponse(BaseModel):
    error: str

@app.get("/", include_in_schema=False)
async def index():
    return {"message": "UMG Parser API. Use POST to convert UMG to Verse code."}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}

@app.post(
    "/convert",
    response_model=SuccessResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def convert(request: UMGRequest):
    """Convert UMG Widget blueprint to Verse code."""
    try:
        # Create parser with config
        config = UMGParserConfig(use_translated=request.use_translated)
        parser = UMGParser(config)
        
        _, verse_code, widgets = parser.convert(request.umg_text, 0)

        added_content = ""
        if request.use_translated:
            added_content = parser.generate_messages_module(widgets)

        return SuccessResponse(verse_code=added_content + verse_code)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.args[0]) if e.args else "Invalid UMG format"
        )
    except Exception as e:
        logger.error(f"Internal server error: {traceback.format_exc()}")

        # Log the error internally but don't expose details
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Validation exception handler - return {error: message} format for 422 errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if errors:
        # Get the first error message
        first_error = errors[0]
        msg = first_error.get("msg", "Validation error")
    else:
        msg = "Validation error"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": msg}
    )

# HTTP exception handler - return {error: message} format
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Don't expose internal errors
    logger.error(f"Unhandled exception: {traceback.format_exc()}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"}
    )

# Debug only
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "web:app", 
        host="0.0.0.0",
        port=5000,
        log_level="info",
        reload=True
    )