"""
Intelligent Momentum Agent.

This agent provides narrative commentary and momentum analysis using OpenAI.
Falls back to simple logic if OpenAI unavailable.
"""

from src.core.state import MatchState
from src.services.llm_client import get_intelligent_response


def _state_to_dict(state: MatchState) -> dict:
    """Convert MatchState to dictionary for LLM context."""
    # Get recent events summary
    recent_events_summary = []
    for event in state.recent_events[-5:]:  # Last 5 events
        if event.event_type == "wicket":
            recent_events_summary.append(f"{event.batter} dismissed by {event.bowler}")
        elif event.event_type == "runs" and event.runs_scored >= 4:
            recent_events_summary.append(f"{event.batter} scored {event.runs_scored} runs")
    
    return {
        "team_batting": state.team_batting,
        "total_runs": state.total_runs,
        "wickets_lost": state.wickets_lost,
        "overs_played": state.overs_played,
        "target": state.target,
        "p_draw": state.p_draw,
        "p_sa_win": state.p_sa_win,
        "recent_events": recent_events_summary,
    }


def _get_fallback_response(state: MatchState) -> str:
    """Fallback momentum analysis using simple logic."""
    recent_wickets = sum(1 for e in state.recent_events[-10:] if e.event_type == "wicket")
    recent_runs = sum(e.runs_scored for e in state.recent_events[-10:] if e.event_type == "runs")
    
    if recent_wickets > 0:
        return "South Africa has momentum with recent wickets."
    elif recent_runs >= 20:
        return "India building momentum with good scoring."
    else:
        return "Match is balanced, both teams fighting."


async def get_momentum_response_async(state: MatchState, query: str = "") -> str:
    """
    Generate intelligent momentum analysis using OpenAI (with fallback).
    
    Args:
        state: Current match state
        query: User query
    
    Returns:
        str: Intelligent or fallback response
    """
    if not query:
        query = "What's the current momentum in the match?"
    
    state_data = _state_to_dict(state)
    
    try:
        intelligent_response = await get_intelligent_response(query, state_data, agent_type="momentum")
        if intelligent_response:
            return intelligent_response
    except Exception:
        pass
    
    return _get_fallback_response(state)

