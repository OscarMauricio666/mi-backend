"""
Pydantic schemas for Claude service.

Defines validation schemas for Claude API input/output.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class Message(BaseModel):
    """Represents a message in the conversation."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request schema for Claude chat."""

    message: str = Field(..., min_length=1, description="Message to send to Claude")
    history: Optional[List[Message]] = Field(
        default=[],
        description="Previous message history"
    )
    max_tokens: int = Field(default=1024, ge=1, le=4096, description="Max tokens in response")


class ChatResponse(BaseModel):
    """Response schema for Claude chat."""

    response: str = Field(..., description="Claude's response")
    model: str = Field(..., description="Model used")
    input_tokens: int = Field(..., description="Input tokens used")
    output_tokens: int = Field(..., description="Output tokens generated")
