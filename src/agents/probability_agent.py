"""
Intelligent Probability Agent.

This agent provides win/draw probability analysis using OpenAI.
Falls back to calculated probabilities if OpenAI unavailable.
"""

from src.core.state import MatchState
from src.services.llm_client import get_intelligent_response


def _state_to_dict(state: MatchState) -> dict:
    """Convert MatchState to dictionary for LLM context."""
    overs_remaining = 90 - state.overs_played
    wickets_remaining = 10 - state.wickets_lost
    runs_needed = state.target - state.total_runs
    
    return {
        "team_batting": state.team_batting,
        "total_runs": state.total_runs,
        "wickets_lost": state.wickets_lost,
        "overs_played": state.overs_played,
        "target": state.target,
        "overs_remaining": overs_remaining,
        "wickets_remaining": wickets_remaining,
        "runs_needed": runs_needed,
        "p_draw": state.p_draw,
        "p_sa_win": state.p_sa_win,
    }


def _get_fallback_response(state: MatchState) -> str:
    """Fallback probability response using calculated values."""
    overs_remaining = 90 - state.overs_played
    wickets_remaining = 10 - state.wickets_lost
    
    return (
        f"P(Draw): {state.p_draw:.0%}, "
        f"P(SA Win): {state.p_sa_win:.0%}. "
        f"India need to bat {overs_remaining:.0f}+ overs "
        f"without losing more than {wickets_remaining - 1} wickets."
    )


async def get_probability_response_async(state: MatchState, query: str = "") -> str:
    """
    Generate intelligent probability analysis using OpenAI (with fallback).
    
    Args:
        state: Current match state
        query: User query
    
    Returns:
        str: Intelligent or fallback response
    """
    if not query:
        query = "What are India's chances of drawing or winning?"
    
    state_data = _state_to_dict(state)
    
    try:
        intelligent_response = await get_intelligent_response(query, state_data, agent_type="probability")
        if intelligent_response:
            return intelligent_response
    except Exception:
        pass
    
    return _get_fallback_response(state)

