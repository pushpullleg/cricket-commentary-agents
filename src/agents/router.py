"""
Query router agent.

This module classifies user queries into categories:
- stats: Match statistics, scorecard data
- momentum: Narrative commentary, recent events
- probability: Win/draw probability calculations
- tactical: Specific dismissal analysis, strategy

Uses simple keyword matching (no LLM required for MVP).
This is fast, deterministic, and doesn't require external API calls.
"""


# Query examples and expected routing for testing
QUERY_EXAMPLES = {
    "What's the score?": "stats",
    "How many runs has Jaiswal scored?": "stats",
    "Who is batting now?": "stats",
    "What just happened?": "momentum",
    "Is India in trouble?": "momentum",
    "Who has the momentum?": "momentum",
    "Can India draw?": "probability",
    "What are India's chances?": "probability",
    "What's the win probability?": "probability",
    "Why did Jaiswal get out?": "tactical",
    "What was the dismissal?": "tactical",
    "How was Sudharsan dismissed?": "tactical",
}


def route_query(query: str) -> str:
    """
    Classify user query into a category.
    
    Uses simple keyword matching to route queries to appropriate agents.
    This is fast, deterministic, and doesn't require LLM calls.
    
    Order matters: Check more specific categories first to avoid false matches.
    
    Args:
        query: User's query string
    
    Returns:
        str: Category name: 'stats', 'momentum', 'probability', or 'tactical'
             Defaults to 'stats' if no match found
    
    Example:
        >>> route_query("What's the score?")
        'stats'
        >>> route_query("Can India draw?")
        'probability'
    """
    query_lower = query.lower()
    
    # Stats queries: Check first (most common, and "runs", "score" are unambiguous)
    # Looking for scorecard data
    stats_keywords = ["score", "runs", "wickets", "overs", "batting"]
    if any(keyword in query_lower for keyword in stats_keywords):
        return "stats"
    
    # Special case: "runs to win" or "runs needed" should be stats, not probability
    if ("run" in query_lower or "runs" in query_lower) and "win" in query_lower:
        return "stats"
    
    # Check "who" separately - only if not asking about momentum
    if "who" in query_lower and "momentum" not in query_lower:
        return "stats"
    
    # Probability queries: Check before tactical/momentum
    # Looking for win/draw chances (but not if asking about runs to win)
    probability_keywords = ["chance", "draw", "win", "probability", "odds", "likely"]
    if any(keyword in query_lower for keyword in probability_keywords):
        return "probability"
    
    # Momentum queries: Check before tactical
    # Looking for narrative/context
    momentum_keywords = ["momentum", "happening", "happened", "situation", "trouble", "doing"]
    if any(keyword in query_lower for keyword in momentum_keywords):
        return "momentum"
    
    # Tactical queries: Check last (most specific)
    # Looking for specific dismissal/strategy analysis
    # Match "how" or "why" only if combined with dismissal-related words
    if any(word in query_lower for word in ["dismissed", "dismissal"]):
        return "tactical"
    if ("why" in query_lower or "how" in query_lower) and "out" in query_lower:
        return "tactical"
    
    # Default to stats if no match found
    return "stats"


def test_router():
    """
    Test the router with query examples.
    
    This function validates that the router correctly classifies
    all example queries. Run this before Day 5 to catch bugs.
    """
    print("Testing query router...")
    all_passed = True
    
    for query, expected_category in QUERY_EXAMPLES.items():
        result = route_query(query)
        if result != expected_category:
            print(f"❌ FAILED: '{query}' -> Expected '{expected_category}', got '{result}'")
            all_passed = False
        else:
            print(f"✅ PASSED: '{query}' -> '{result}'")
    
    if all_passed:
        print("\n✅ All router tests passed!")
    else:
        print("\n❌ Some router tests failed!")
    
    return all_passed


if __name__ == "__main__":
    # Run tests when executed directly
    test_router()

