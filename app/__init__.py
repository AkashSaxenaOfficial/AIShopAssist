"""
AI Shop Assist Application Package

A modern AI-powered shopping assistant with real-time LLM integration.
"""

from . import config
from .core import ShopAgent, LLMManager
from .server import websocket

__version__ = config.APP_VERSION
__all__ = ['config', 'ShopAgent', 'LLMManager', 'websocket'] 