"""
Claude Service.

Contains business logic for Anthropic API (Claude) interactions.
"""

from typing import List, Optional
from anthropic import Anthropic

from src.config import get_settings
from src.models.claude import Message

settings = get_settings()


class ClaudeService:
    """Service for Claude API interactions."""

    def __init__(self):
        """Initialize Anthropic client."""
        if not settings.anthropic_api_key or settings.anthropic_api_key == "tu-api-key-aqui":
            raise ValueError("ANTHROPIC_API_KEY not configured. Update your .env file")
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-20250514"

    async def chat(
        self,
        message: str,
        history: Optional[List[Message]] = None,
        max_tokens: int = 1024
    ) -> dict:
        """
        Send a message to Claude and get a response.

        Args:
            message: User message
            history: List of previous conversation messages
            max_tokens: Maximum tokens in response

        Returns:
            Dictionary with response and metadata
        """
        messages = []

        if history:
            for msg in history:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        messages.append({
            "role": "user",
            "content": message
        })

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages
        )

        return {
            "response": response.content[0].text,
            "model": response.model,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
