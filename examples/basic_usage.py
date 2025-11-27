"""
Basic usage example for the Cricket Commentary Agent System.

This example demonstrates how to:
1. Initialize the agent
2. Process queries
3. Handle events
"""

import asyncio
from src.core.state import initialize_match_state
from src.agents.router import route_query
from src.agents.stats_agent import get_stats_response_async
from src.agents.event_handler import process_event
import json


async def example_basic_usage():
    """Demonstrate basic usage of the cricket agent system."""
    
    print("=" * 60)
    print("Cricket Agent System - Basic Usage Example")
    print("=" * 60)
    
    # 1. Initialize match state
    print("\n1. Initializing match state...")
    state = initialize_match_state()
    print(f"   Initial state: {state.total_runs}/{state.wickets_lost}")
    
    # 2. Route a query
    print("\n2. Routing queries...")
    query = "What's the score?"
    category = route_query(query)
    print(f"   Query: '{query}' -> Category: {category}")
    
    # 3. Get stats response
    print("\n3. Getting stats response...")
    response = await get_stats_response_async(state, query)
    print(f"   Response: {response}")
    
    # 4. Process an event
    print("\n4. Processing an event...")
    sample_event = {
        "event_type": "runs",
        "timestamp": "2025-11-26T09:15:00+05:30",
        "batter": "Sai Sudharsan",
        "bowler": "Marco Jansen",
        "runs_scored": 4,
        "current_score": 31,
        "current_wickets": 2,
        "overs_played": 7.1,
        "balls_in_over": 1,
        "commentary": "Sudharsan drives through covers for four"
    }
    
    event_json = json.dumps(sample_event)
    new_state = await process_event(event_json, state)
    print(f"   New state: {new_state.total_runs}/{new_state.wickets_lost}")
    print(f"   P(Draw): {new_state.p_draw:.2%}")
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(example_basic_usage())

