"""
Intelligent Tactical Agent.

This agent provides tactical analysis of dismissals and match strategy using OpenAI.
Falls back to simple event description if OpenAI unavailable.
"""

from src.core.state import MatchState
from src.services.llm_client import get_intelligent_response


def _state_to_dict(state: MatchState) -> dict:
    """Convert MatchState to dictionary for LLM context."""
    # Get recent events with details
    recent_events_detail = []
    for event in state.recent_events[-3:]:  # Last 3 events
        event_detail = {
            "type": event.event_type,
            "batter": event.batter,
            "bowler": event.bowler,
            "commentary": event.commentary,
        }
        if event.event_type == "wicket":
            event_detail["dismissal_mode"] = event.dismissal_mode
            event_detail["fielder"] = event.fielder
        elif event.event_type == "runs":
            event_detail["runs_scored"] = event.runs_scored
        
        recent_events_detail.append(event_detail)
    
    # Include dismissed players information
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
        },
        "dismissed_players": dismissed_info,
        "recent_events": recent_events_detail,
    }


def _get_fallback_response(state: MatchState, query: str = "") -> str:
    """Fallback tactical analysis using simple event description."""
    query_lower = query.lower() if query else ""
    
    # Check if asking about a specific dismissed player
    if any(name.lower() in query_lower for name in ["jaiswal", "jasiwal", "yashasvi"]):
        for player in state.dismissed_players:
            if "jaiswal" in player.name.lower() or "jasiwal" in query_lower:
                dismissal_desc = f"c {player.fielder}" if player.fielder else player.dismissal_mode
                return f"{player.name} scored {player.runs} runs and was dismissed {dismissal_desc} b {player.bowler}."
    
    # Check recent events
    if state.recent_events:
        last_event = state.recent_events[-1]
        if last_event.event_type == "wicket":
            dismissal_desc = f"c {last_event.fielder}" if last_event.fielder else last_event.dismissal_mode
            response = (
                f"{last_event.batter} dismissed {dismissal_desc} b {last_event.bowler}. "
                f"{last_event.commentary or 'Wicket falls!'}"
            )
        else:
            response = f"Last ball: {last_event.commentary or 'No commentary available.'}"
    else:
        response = "No recent events to analyze."
    
    return response


async def get_tactical_response_async(state: MatchState, query: str = "") -> str:
    """
    Generate intelligent tactical analysis using OpenAI (with fallback).
    
    Args:
        state: Current match state
        query: User query
    
    Returns:
        str: Intelligent or fallback response
    """
    if not query:
        if state.recent_events and state.recent_events[-1].event_type == "wicket":
            query = f"Why was {state.recent_events[-1].batter} dismissed?"
        else:
            query = "What's the tactical situation?"
    
    state_data = _state_to_dict(state)
    
    try:
        intelligent_response = await get_intelligent_response(query, state_data, agent_type="tactical")
        if intelligent_response:
            return intelligent_response
    except Exception:
        pass
    
    return _get_fallback_response(state, query)

