"""
Conversation management module for legacylens.

This module provides in-memory conversation management for the public preview.
"""

from .interface import ConversationInterface
from .memory import InMemoryConversationManager

__all__ = [
    "ConversationInterface",
    "InMemoryConversationManager",
]
