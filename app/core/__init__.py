"""
Core Application Logic

Contains the main business logic and services.
"""

from .agent import ShopAgent
from .llm import LLMManager

__all__ = ['ShopAgent', 'LLMManager'] 