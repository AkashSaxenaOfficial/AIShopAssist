"""
LLM Manager for AI Shop Assist

Handles LLM interactions and tool management using Claude.
"""

import time
from typing import List
from langchain_anthropic import ChatAnthropic

from .. import config

class LLMManager:
    """Manages LLM interactions and tools"""
    
    def __init__(self):

        self.llm = self.initialize_llm()
        
        
    def initialize_llm(self):
        self.llm = ChatAnthropic(
            model=config.ANTHROPIC_MODEL,
            anthropic_api_key=config.API_KEYS["ANTHROPIC_API_KEY"],
            temperature=0.7,
            max_retries=3,
            timeout=30
        )
        return self.llm
    