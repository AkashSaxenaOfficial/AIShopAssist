"""
Test script for AI Shop Assist Agent
"""

import os
import uuid
from dotenv import load_dotenv
from app.core.agent import get_response

def test_agent():
    """Test the shopping agent"""
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        return
    
    # Create agent
    
    # Create a conversation ID
    conversation_id = str(uuid.uuid4())
    
    # Test queries
    test_cases = [
        {
            "query": "Tell me about the air conditioner with ID AC001",
            "context": ["Looking for information about air conditioner AC001"]
        },
        {
            "query": "What are the features of air conditioner AC002?",
            "context": ["Interested in features of AC002"]
        },
        {
            "query": "Compare AC001 and AC002",
            "context": [
                "Need to compare two air conditioners",
                "First product: AC001",
                "Second product: AC002"
            ]
        }
    ]
    
    print("🤖 Testing AI Shop Assist Agent")
    print("=" * 50)
    print(f"Conversation ID: {conversation_id}")
    print("=" * 50)
    
    for case in test_cases:
        print(f"\n📝 Query: {case['query']}")
        print("-" * 50)
        response = get_response(
            query=case['query'],
            context=case['context'],
            conversation_id=conversation_id
        )
        print(f"💬 Response: {response}")
        print("-" * 50)

if __name__ == "__main__":
    test_agent() 