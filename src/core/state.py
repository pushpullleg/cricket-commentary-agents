"""
State models for cricket agent system.

This module defines the core data structures using Pydantic:
- Batter: Represents a batsman's current state
- Event: Represents a single cricket event (wicket, runs, etc.)
- MatchState: Represents the complete match state at any point in time

These models form the foundation of the system's state management,
ensuring type safety and data validation throughout the application.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Batter(BaseModel):
    """
    Represents a batsman's current state.
    
    Attributes:
        name: Batsman's name
        runs: Runs scored by this batsman
        balls_faced: Number of balls faced
        is_on_strike: Whether this batsman is currently on strike
    """
    name: str
    runs: int
    balls_faced: int
    is_on_strike: bool


class Event(BaseModel):
    """
    Represents a single cricket event (ball-by-ball or significant event).
    
    This model captures all information needed to reconstruct the match state
    after any event occurs. Events are immutable - each event creates a new
    state rather than modifying the existing one.
    
    Attributes:
        timestamp: When the event occurred
        event_type: Type of event ('wicket', 'runs', 'maiden', 'boundary', etc.)
        runs_scored: Runs scored in this event (0 for wickets)
        batter: Name of the batsman involved
        bowler: Name of the bowler
        overs_played: Overs played (e.g., 12.3 means 12 overs and 3 balls)
        dismissal_mode: For wickets: 'caught', 'bowled', 'lbw', 'stumped'
        fielder: Who caught/ran out the batter (for wickets)
        current_score: Total runs after this ball
        current_wickets: Wickets lost after this ball
        balls_in_over: Which ball of the over (1-6)
        commentary: Ball-by-ball description
    """
    timestamp: datetime
    event_type: str = Field(
        ...,
        description="Type of event: 'wicket', 'runs', 'maiden', 'boundary', 'dot', 'wide', 'no_ball'"
    )
    runs_scored: int = 0
    batter: Optional[str] = None
    bowler: Optional[str] = None
    overs_played: float = Field(..., description="Overs played (e.g., 12.3 means 12 overs and 3 balls)")
    dismissal_mode: Optional[str] = Field(
        None,
        description="For wickets: 'caught', 'bowled', 'lbw', 'stumped'"
    )
    fielder: Optional[str] = Field(None, description="Who caught/ran out the batter (for wickets)")
    current_score: int = Field(..., description="Total runs after this ball")
    current_wickets: int = Field(..., description="Wickets lost after this ball")
    balls_in_over: int = Field(ge=1, le=6, description="Which ball of the over (1-6)")
    commentary: Optional[str] = Field(None, description="Ball-by-ball description from Cricbuzz")


class DismissedPlayer(BaseModel):
    """
    Represents a dismissed player with their score and dismissal details.
    
    This model tracks players who have been dismissed, allowing the system
    to answer questions about past dismissals and maintain match history.
    
    Attributes:
        name: Player's name
        runs: Runs scored before dismissal
        balls_faced: Balls faced before dismissal
        dismissal_mode: How they were dismissed
        bowler: Who bowled them out
        fielder: Who caught/ran them out (if applicable)
        dismissed_at_score: Team score when dismissed
        dismissed_at_overs: Overs played when dismissed
    """
    name: str
    runs: int
    balls_faced: int
    dismissal_mode: str
    bowler: str
    fielder: Optional[str] = None
    dismissed_at_score: int  # Team score when dismissed
    dismissed_at_overs: float  # Overs when dismissed


class MatchState(BaseModel):
    """
    Represents the complete match state at any point in time.
    
    This is the central state object that all agents operate on.
    It gets updated atomically when new events arrive, ensuring
    consistency across the entire system.
    
    The state is immutable in principle - updates create new
    state objects rather than modifying existing ones.
    
    Attributes:
        match_id: Unique identifier for the match
        team_batting: Name of the team currently batting
        total_runs: Total runs scored
        wickets_lost: Number of wickets lost
        overs_played: Overs played (e.g., 12.3)
        target: Target runs to win
        current_batter: Current batsman on strike
        dismissed_players: List of dismissed players
        recent_events: Recent match events (for context)
        p_draw: Probability of draw (0.0 to 1.0)
        p_sa_win: Probability of SA win (0.0 to 1.0)
        last_updated: When state was last updated
    """
    match_id: str
    team_batting: str
    total_runs: int
    wickets_lost: int
    overs_played: float
    target: int
    current_batter: Batter
    dismissed_players: List[DismissedPlayer] = Field(default_factory=list)
    recent_events: List[Event] = Field(default_factory=list)
    p_draw: float = Field(..., ge=0.0, le=1.0, description="Probability of draw (0.0 to 1.0)")
    p_sa_win: float = Field(..., ge=0.0, le=1.0, description="Probability of SA win (0.0 to 1.0)")
    last_updated: datetime


def initialize_match_state() -> MatchState:
    """
    Initialize Day 5 state for India vs SA Test Match.
    
    This function sets up the match state at the start of Day 5,
    based on the end-of-Day-4 position.
    
    At start of Day 5: India 27/2
    - Current: Sai Sudharsan 2*
    
    Note: Dismissed players will be tracked automatically as events come in.
    If you need historical dismissals, they should come from the API or
    be provided via configuration.
    
    Returns:
        MatchState: Initialized match state ready for Day 5 events
    """
    return MatchState(
        match_id="117380",
        team_batting="India",
        total_runs=27,  # End of Day 4 score
        wickets_lost=2,
        overs_played=6.0,  # Overs bowled at stumps
        target=549,  # SA's total
        current_batter=Batter(
            name="Sai Sudharsan",
            runs=2,
            balls_faced=4,
            is_on_strike=True
        ),
        dismissed_players=[],  # Will be populated from events as they come in
        recent_events=[],
        p_draw=0.35,  # Pre-Day-5 probability (India unlikely to win, more likely draw or lose)
        p_sa_win=0.65,
        last_updated=datetime.now()
    )

