"""
Automated test script for cricket agent system.

Tests various query types and verifies responses.
"""

import asyncio
from models.state import initialize_match_state
from agents.router import route_query
from agents.stats_agent import get_stats_response_async
from agents.probability_agent import get_probability_response_async
from agents.momentum_agent import get_momentum_response_async
from agents.tactical_agent import get_tactical_response_async


# Test queries organized by category
TEST_QUERIES = {
    "stats": [
        "what's the score?",
        "how many wickets remaining",
        "how many runs to win",
        "who is batting",
        "what is the total score",
        "how many overs left",
    ],
    "probability": [
        "can India draw?",
        "what are India's chances?",
        "what's the win probability?",
    ],
    "momentum": [
        "what just happened?",
        "is India in trouble?",
        "who has the momentum?",
    ],
    "tactical": [
        "why did Jaiswal get out?",
        "what's the strategy for India?",
        "how was Jaiswal dismissed?",
    ],
}


async def test_query_routing():
    """Test query routing."""
    print("\n" + "=" * 60)
    print("Testing Query Routing")
    print("=" * 60)
    
    test_cases = [
        ("what's the score?", "stats"),
        ("can India draw?", "probability"),
        ("what just happened?", "momentum"),
        ("why did Jaiswal get out?", "tactical"),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_category in test_cases:
        category = route_query(query)
        if category == expected_category:
            print(f"✅ '{query}' → {category}")
            passed += 1
        else:
            print(f"❌ '{query}' → {category} (expected {expected_category})")
            failed += 1
    
    print(f"\nRouting Test: {passed} passed, {failed} failed")
    return failed == 0


async def test_stats_agent():
    """Test stats agent."""
    print("\n" + "=" * 60)
    print("Testing Stats Agent")
    print("=" * 60)
    
    state = initialize_match_state()
    
    for query in TEST_QUERIES["stats"]:
        try:
            response = await get_stats_response_async(state, query)
            print(f"\nQuery: {query}")
            print(f"Response: {response[:100]}..." if len(response) > 100 else f"Response: {response}")
        except Exception as e:
            print(f"❌ Error with '{query}': {e}")
    
    print("\n✅ Stats agent test complete")


async def test_probability_agent():
    """Test probability agent."""
    print("\n" + "=" * 60)
    print("Testing Probability Agent")
    print("=" * 60)
    
    state = initialize_match_state()
    
    for query in TEST_QUERIES["probability"]:
        try:
            response = await get_probability_response_async(state, query)
            print(f"\nQuery: {query}")
            print(f"Response: {response[:100]}..." if len(response) > 100 else f"Response: {response}")
        except Exception as e:
            print(f"❌ Error with '{query}': {e}")
    
    print("\n✅ Probability agent test complete")


async def test_momentum_agent():
    """Test momentum agent."""
    print("\n" + "=" * 60)
    print("Testing Momentum Agent")
    print("=" * 60)
    
    state = initialize_match_state()
    
    for query in TEST_QUERIES["momentum"]:
        try:
            response = await get_momentum_response_async(state, query)
            print(f"\nQuery: {query}")
            print(f"Response: {response[:100]}..." if len(response) > 100 else f"Response: {response}")
        except Exception as e:
            print(f"❌ Error with '{query}': {e}")
    
    print("\n✅ Momentum agent test complete")


async def test_tactical_agent():
    """Test tactical agent."""
    print("\n" + "=" * 60)
    print("Testing Tactical Agent")
    print("=" * 60)
    
    state = initialize_match_state()
    
    for query in TEST_QUERIES["tactical"]:
        try:
            response = await get_tactical_response_async(state, query)
            print(f"\nQuery: {query}")
            print(f"Response: {response[:100]}..." if len(response) > 100 else f"Response: {response}")
        except Exception as e:
            print(f"❌ Error with '{query}': {e}")
    
    print("\n✅ Tactical agent test complete")


async def test_all():
    """Run all tests."""
    print("=" * 60)
    print("Cricket Agent System - Automated Tests")
    print("=" * 60)
    
    # Test routing
    routing_ok = await test_query_routing()
    
    # Test agents
    await test_stats_agent()
    await test_probability_agent()
    await test_momentum_agent()
    await test_tactical_agent()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Query Routing: {'✅ PASS' if routing_ok else '❌ FAIL'}")
    print("Agent Tests: ✅ Complete (check output above)")
    print("\n💡 Tip: Run 'python main.py' for interactive testing")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_all())

