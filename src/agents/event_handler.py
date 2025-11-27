"""
Event handler agent.

This module handles event validation and state updates.
Events come from automated API polling (not manual input).
It ensures data integrity through strict validation and atomic state transitions.

The event handler is responsible for:
1. Validating incoming events
2. Ensuring state transitions are logical
3. Updating match state atomically
4. Tracking dismissed players
"""

import json
from typing import Dict, Any
from datetime import datetime

from src.core.state import Event, MatchState, DismissedPlayer
from src.core.probability import update_probability


def validate_event(event_dict: Dict[str, Any]) -> Event:
    """
    Validate and create an Event from a dictionary.
    
    This function performs strict validation to ensure all required
    fields are present before creating an Event object.
    
    Args:
        event_dict: Dictionary containing event data (from JSON)
    
    Returns:
        Event: Validated Event object
    
    Raises:
        ValueError: If required fields are missing
    """
    required_fields = ["event_type", "timestamp", "current_score", "current_wickets", "overs_played"]
    
    for field in required_fields:
        if field not in event_dict:
            raise ValueError(f"Missing required field: {field}")
    
    # Parse timestamp if it's a string
    if isinstance(event_dict.get("timestamp"), str):
        try:
            event_dict["timestamp"] = datetime.fromisoformat(event_dict["timestamp"])
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format: {e}")
    
    return Event(**event_dict)


def update_state(state: MatchState, event: Event) -> MatchState:
    """
    Update match state with a new event, validating all transitions.
    
    This function ensures state integrity by:
    1. Validating event data (runs, overs, wickets)
    2. Checking state transitions are logical
    3. Rebuilding state from scratch (avoids shallow copy issues)
    4. Updating probabilities
    
    Args:
        state: Current match state
        event: New event to apply
    
    Returns:
        MatchState: Updated match state
    
    Raises:
        ValueError: If state transition is invalid
    
    Example:
        >>> state = initialize_match_state()
        >>> event = Event(event_type="runs", runs_scored=4, ...)
        >>> new_state = update_state(state, event)
    """
    # Validate runs are non-negative
    if event.runs_scored < 0:
        raise ValueError("Runs cannot be negative")
    
    # Validate overs don't go backwards
    if event.overs_played < state.overs_played:
        raise ValueError(
            f"Overs went backwards: {state.overs_played} → {event.overs_played}"
        )
    
    # Validate wickets don't exceed 10
    if event.event_type == "wicket":
        if state.wickets_lost + 1 > 10:
            raise ValueError("Cannot lose more than 10 wickets")
    
    # Update probability first (before creating new state)
    # Pass current state (before event) for probability calculation
    new_p_draw = update_probability(state.p_draw, event, state)
    
    # Track dismissed players when wicket falls
    dismissed_players = state.dismissed_players.copy()  # Copy existing dismissed players
    if event.event_type == "wicket" and event.batter:
        # Calculate runs scored by dismissed batter
        # This is approximate - ideally we'd track individual scores better
        dismissed_runs = 0
        if state.current_batter.name == event.batter:
            dismissed_runs = state.current_batter.runs
        else:
            # Try to find from recent events
            for prev_event in reversed(state.recent_events):
                if prev_event.batter == event.batter and prev_event.event_type == "runs":
                    dismissed_runs += prev_event.runs_scored
        
        # Add dismissed player to history
        dismissed_players.append(
            DismissedPlayer(
                name=event.batter,
                runs=dismissed_runs,
                balls_faced=0,  # Not tracked in events
                dismissal_mode=event.dismissal_mode or "unknown",
                bowler=event.bowler or "unknown",
                fielder=event.fielder,
                dismissed_at_score=event.current_score,
                dismissed_at_overs=event.overs_played
            )
        )
    
    # Rebuild state from scratch (safer than copy() - avoids shallow copy issues with recent_events list)
    # This ensures recent_events is a new list, not a shared reference
    new_state = MatchState(
        match_id=state.match_id,
        team_batting=state.team_batting,
        total_runs=event.current_score,  # Use event's current_score for accuracy
        wickets_lost=event.current_wickets,
        overs_played=event.overs_played,
        target=state.target,
        current_batter=state.current_batter,  # Update this if batter changed (future enhancement)
        dismissed_players=dismissed_players,
        recent_events=state.recent_events + [event],  # New list (not shared reference)
        p_draw=new_p_draw,
        p_sa_win=1.0 - new_p_draw,
        last_updated=event.timestamp
    )
    
    return new_state


async def process_event(event_json: str, state: MatchState) -> MatchState:
    """
    Process a JSON event string and update match state.
    
    This is the main entry point for processing events from manual input.
    It handles JSON parsing, validation, and state updates.
    
    Args:
        event_json: JSON string containing event data
        state: Current match state
    
    Returns:
        MatchState: Updated match state
    
    Raises:
        ValueError: If JSON is invalid or event validation fails
        json.JSONDecodeError: If JSON cannot be parsed
    """
    try:
        # Parse JSON
        event_dict = json.loads(event_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    
    # Validate and create event
    event = validate_event(event_dict)
    
    # Update state
    new_state = update_state(state, event)
    
    return new_state

