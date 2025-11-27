"""
Quick test to verify OpenAI integration is working.
"""

import asyncio
import os
from dotenv import load_dotenv
from models.state import initialize_match_state
from agents.stats_agent import get_stats_response_async
from utils.llm_client import get_openai_client

load_dotenv()

async def test():
    print("Testing OpenAI Integration...")
    print("=" * 50)
    
    # Check if API key is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY not set or still has placeholder value")
        print("   Please update .env file with your actual API key")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test OpenAI client
    client = get_openai_client()
    if not client:
        print("❌ Failed to create OpenAI client")
        return
    
    print("✅ OpenAI client created successfully")
    
    # Test with a query
    state = initialize_match_state()
    query = "how many runs to win"
    
    print(f"\nTesting query: '{query}'")
    print("-" * 50)
    
    try:
        response = await get_stats_response_async(state, query)
        print(f"Response: {response}")
        print("\n✅ Intelligent agent is working!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())

