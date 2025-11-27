"""
Intelligent Stats Agent.

This agent uses OpenAI to understand natural language queries and provide
intelligent responses. Falls back to keyword matching if OpenAI is unavailable.

This makes it a TRUE agent - it understands context, handles variations,
and provides natural responses.
"""

import asyncio
from src.core.state import MatchState
from src.services.llm_client import get_intelligent_response


def _state_to_dict(state: MatchState) -> dict:
    """Convert MatchState to dictionary for LLM context."""
    dismissed_info = []
    for player in state.dismissed_players:
        dismissed_info.append({
            "name": player.name,
            "runs": player.runs,
            "dismissal_mode": player.dismissal_mode,
            "bowler": player.bowler,
            "fielder": player.fielder,
        })
    
    return {
        "team_batting": state.team_batting,
        "total_runs": state.total_runs,
        "wickets_lost": state.wickets_lost,
        "overs_played": state.overs_played,
        "target": state.target,
        "current_batter": {
            "name": state.current_batter.name,
            "runs": state.current_batter.runs,
            "balls_faced": state.current_batter.balls_faced,
        },
        "dismissed_players": dismissed_info,
        "p_draw": state.p_draw,
        "p_sa_win": state.p_sa_win,
    }


def _get_keyword_response(state: MatchState, query: str) -> str:
    """
    Fallback keyword-based response (used when OpenAI unavailable).
    
    This is the old keyword matching logic, kept as fallback.
    """
    query_lower = query.lower() if query else ""
    
    # Calculate key metrics
    overs_remaining = 90 - state.overs_played
    wickets_remaining = 10 - state.wickets_lost
    runs_needed = state.target - state.total_runs
    overs_str = f"{state.overs_played:.1f}"
    
    # Answer specific questions
    if "wicket" in query_lower and ("remain" in query_lower or "remian" in query_lower or "left" in query_lower):
        return f"India has {wickets_remaining} wickets remaining (currently {state.wickets_lost} down)."
    
    if "wicket" in query_lower and "lost" in query_lower:
        return f"India has lost {state.wickets_lost} wickets so far."
    
    if "bat" in query_lower and ("who" in query_lower or "is" in query_lower):
        return f"Currently batting: {state.current_batter.name} ({state.current_batter.runs}* runs, {state.current_batter.balls_faced} balls)."
    
    if "run" in query_lower and ("need" in query_lower or "require" in query_lower):
        return f"India needs {runs_needed} more runs to win (currently {state.total_runs}/{state.wickets_lost})."
    
    if "run" in query_lower and "win" in query_lower:
        return f"India needs {runs_needed} more runs to win (currently {state.total_runs}/{state.wickets_lost})."
    
    if "run" in query_lower and ("score" in query_lower or "total" in query_lower):
        return f"India's current score: {state.total_runs} runs for {state.wickets_lost} wickets."
    
    # Questions about dismissed players
    if any(name.lower() in query_lower for name in ["jaiswal", "jasiwal", "yashasvi"]):
        for player in state.dismissed_players:
            if "jaiswal" in player.name.lower() or "jasiwal" in query_lower:
                dismissal_desc = f"c {player.fielder}" if player.fielder else player.dismissal_mode
                return f"{player.name} scored {player.runs} runs. Dismissed: {dismissal_desc} b {player.bowler}."
    
    # Generic dismissed player questions
    if ("out" in query_lower or "dismiss" in query_lower) and any(
        word in query_lower for word in ["how", "what", "who", "when"]
    ):
        if state.dismissed_players:
            last_dismissed = state.dismissed_players[-1]
            dismissal_desc = f"c {last_dismissed.fielder}" if last_dismissed.fielder else last_dismissed.dismissal_mode
            return f"{last_dismissed.name} scored {last_dismissed.runs} runs. Dismissed: {dismissal_desc} b {last_dismissed.bowler}."
    
    if "over" in query_lower and ("remain" in query_lower or "left" in query_lower):
        return f"Approximately {overs_remaining:.1f} overs remaining in the day (currently at {overs_str} overs)."
    
    if "target" in query_lower:
        return f"India's target is {state.target} runs. Currently at {state.total_runs}/{state.wickets_lost}."
    
    # Default: Full scorecard summary
    response = (
        f"India: {state.total_runs} for {state.wickets_lost} in {overs_str} overs. "
        f"Target: {state.target}. "
        f"Overs remaining: ~{overs_remaining:.1f}. "
        f"Wickets remaining: {wickets_remaining}. "
        f"Currently batting: {state.current_batter.name} ({state.current_batter.runs}*)."
    )
    
    return response


async def get_stats_response_async(state: MatchState, query: str = "") -> str:
    """
    Generate an intelligent stats response using OpenAI (with keyword fallback).
    
    This is a TRUE intelligent agent that:
    1. Tries OpenAI first for natural language understanding
    2. Falls back to keyword matching if OpenAI unavailable
    3. Understands context, typos, variations, and natural language
    
    Args:
        state: Current match state
        query: User query
    
    Returns:
        str: Intelligent or keyword-based response
    """
    if not query:
        # No query, return default summary
        return _get_keyword_response(state, "")
    
    # Try OpenAI first (intelligent agent)
    state_data = _state_to_dict(state)
    
    try:
        intelligent_response = await get_intelligent_response(query, state_data, agent_type="stats")
        
        if intelligent_response:
            return intelligent_response
    except Exception:
        # If OpenAI fails, fall through to keyword matching
        pass
    
    # Fallback to keyword matching if OpenAI unavailable
    return _get_keyword_response(state, query)


# Synchronous wrapper for backward compatibility
def get_stats_response(state: MatchState, query: str = "") -> str:
    """
    Synchronous wrapper for get_stats_response_async.
    
    For use in non-async contexts. In async contexts, use get_stats_response_async.
    """
    try:
        loop = asyncio.get_running_loop()
        # We're in async context, this shouldn't be called
        # Return keyword response as fallback
        return _get_keyword_response(state, query)
    except RuntimeError:
        # No running loop, can use asyncio.run
        return asyncio.run(get_stats_response_async(state, query))

