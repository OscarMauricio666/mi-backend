"""
Claude resource routes.

Defines endpoints for Claude API interactions.
"""

from fastapi import APIRouter, HTTPException, status

from src.models.claude import ChatRequest, ChatResponse
from src.services.claude_service import ClaudeService

router = APIRouter(prefix="/claude", tags=["Claude AI"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with Claude",
    description="Send a message to Claude and receive a response."
)
async def chat_with_claude(request: ChatRequest) -> ChatResponse:
    """
    Interact with Claude AI.

    - **message**: The message to send to Claude
    - **history**: Optional list of previous messages for context
    - **max_tokens**: Max tokens in response (1-4096)
    """
    try:
        service = ClaudeService()
        result = await service.chat(
            message=request.message,
            history=request.history,
            max_tokens=request.max_tokens
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error communicating with Claude: {str(e)}"
        )


@router.get(
    "/health",
    summary="Claude service status",
    description="Check if Claude API connection is working."
)
async def claude_health():
    """Check Claude API connectivity."""
    try:
        service = ClaudeService()
        result = await service.chat(
            message="Reply only with: OK",
            max_tokens=10
        )
        return {
            "status": "ok",
            "model": result["model"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Claude API unavailable: {str(e)}"
        )
