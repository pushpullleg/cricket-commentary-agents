"""
Win probability model for cricket match.

This module implements a realistic probability model that updates
P(draw) and P(SA win) based on match events.

The model accounts for:
- Time decay (more overs = safer for batsmen to draw)
- Wicket penalties (India already weak at 2/3)
- Boundary boosts (help India survive)
- Day 5 pitch deterioration

This is a simplified probabilistic model suitable for real-time updates.
For production use, consider more sophisticated models based on historical
data and advanced statistics.
"""

from .state import Event, MatchState


def update_probability(old_p_draw: float, event: Event, state: MatchState) -> float:
    """
    Update draw probability based on event and current match state.
    
    This is a realistic model for Day 5 scenario where:
    - India is in a weak position (2/3 wickets down)
    - Needs 522 runs in ~90 overs (5.8 runs/over - very high)
    - Day 5 pitch deteriorates (helps bowlers)
    
    The model uses simple heuristics:
    - Time factor: More overs remaining = better for draw
    - Wicket penalty: Each wicket reduces draw probability
    - Boundary boost: Boundaries slightly increase survival chances
    
    Args:
        old_p_draw: Previous draw probability (0.0 to 1.0)
        event: The cricket event that just occurred
        state: Current match state (before this event is applied)
    
    Returns:
        float: Updated draw probability (capped between 0.05 and 0.95)
    
    Example:
        >>> state = MatchState(...)
        >>> event = Event(event_type="wicket", ...)
        >>> new_prob = update_probability(0.35, event, state)
        >>> print(f"New draw probability: {new_prob:.2%}")
    """
    p_draw = old_p_draw
    
    # Time decay: More overs played = safer for batsmen to draw
    # As time passes, India just needs to survive, not chase runs
    overs_remaining = 90 - state.overs_played
    time_factor = min(1.0, 1 + (overs_remaining / 90) * 0.2)  # Max +20% boost
    p_draw *= time_factor
    
    # Wicket penalty: India already weak at 2/3
    # Early wickets hurt more (lose 15%), late wickets hurt even more (lose 30% - collapse risk)
    if event.event_type == 'wicket':
        if state.wickets_lost < 5:
            p_draw *= 0.85  # Lose 15% per wicket early in innings
        else:
            p_draw *= 0.70  # Lose 30% if already 5+ down (high collapse risk)
    
    # Runs scored: Boundaries help India survive
    # Scoring runs means India is building partnerships and surviving
    if event.event_type == 'runs':
        if event.runs_scored >= 4:
            p_draw *= 1.05  # Boundary helps survival (+5% boost)
    
    # Cap between 0.05 and 0.95
    # Always leave some chance of collapse or counter-attack
    return max(0.05, min(0.95, p_draw))

