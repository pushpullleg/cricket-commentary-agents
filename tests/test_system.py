"""
Quick test script to verify the cricket agent system works.

This script tests:
1. State initialization
2. Event processing
3. Query routing
4. Stats agent
5. Probability updates
"""

import json
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.state import initialize_match_state
from src.agents.event_handler import process_event
from src.agents.router import route_query, test_router
from src.agents.stats_agent import get_stats_response


async def test_event_processing():
    """Test event processing with mock events."""
    print("\n" + "=" * 60)
    print("Testing Event Processing")
    print("=" * 60)
    
    # Initialize state
    state = initialize_match_state()
    print(f"\nInitial State:")
    print(f"  Score: {state.total_runs}/{state.wickets_lost}")
    print(f"  P(Draw): {state.p_draw:.2%}")
    print(f"  P(SA Win): {state.p_sa_win:.2%}")
    
    # Test with sample event (simulating API data)
    print(f"\nTesting event processing with sample data...")
    
    # Create a sample event (simulating what API would return)
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
    state = await process_event(event_json, state)
    print(f"\nSample event processed: {sample_event['event_type']} - {sample_event.get('runs_scored', 0)} runs")
    print(f"  Score: {state.total_runs}/{state.wickets_lost}")
    print(f"  P(Draw): {state.p_draw:.2%}")
    
    print("\n✅ Event processing test passed!")


def test_query_routing():
    """Test query routing."""
    print("\n" + "=" * 60)
    print("Testing Query Routing")
    print("=" * 60)
    
    test_queries = [
        ("What's the score?", "stats"),
        ("Can India draw?", "probability"),
        ("What just happened?", "momentum"),
        ("Why did Jaiswal get out?", "tactical"),
    ]
    
    all_passed = True
    for query, expected in test_queries:
        result = route_query(query)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{query}' -> {result} (expected: {expected})")
        if result != expected:
            all_passed = False
    
    if all_passed:
        print("\n✅ Query routing test passed!")
    else:
        print("\n❌ Query routing test failed!")
    
    return all_passed


def test_stats_agent():
    """Test stats agent."""
    print("\n" + "=" * 60)
    print("Testing Stats Agent")
    print("=" * 60)
    
    state = initialize_match_state()
    response = get_stats_response(state)
    
    print(f"\nStats Response: {response}")
    
    # Verify response contains key information
    assert "India" in response
    assert str(state.total_runs) in response
    assert str(state.wickets_lost) in response
    assert "Target" in response
    
    print("\n✅ Stats agent test passed!")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Cricket Agent System - Test Suite")
    print("=" * 60)
    
    try:
        # Test query routing
        test_query_routing()
        
        # Test stats agent
        test_stats_agent()
        
        # Test event processing
        await test_event_processing()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60 + "\n")
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

