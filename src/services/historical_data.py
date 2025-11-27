"""
Historical data fetcher for cricket match.

Fetches historical dismissed players and match data from free APIs.
This allows the system to know about players dismissed before it started tracking.
"""

from typing import List
from src.core.state import MatchState, DismissedPlayer
from .cricket_api import CricketAPIClient


async def fetch_and_update_historical_data(state: MatchState) -> MatchState:
    """
    Fetch historical dismissed players from API and update state.
    
    This function:
    1. Fetches historical dismissal data from free APIs
    2. Updates the state with dismissed players
    3. Falls back gracefully if data not available
    
    Args:
        state: Current match state
    
    Returns:
        MatchState: Updated state with historical data
    """
    client = CricketAPIClient(state.match_id, ("India", "South Africa"))
    
    print("📊 Fetching historical dismissal data from API...")
    
    try:
        # Fetch historical dismissals
        dismissed_players = await client.fetch_historical_dismissals()
        
        if dismissed_players:
            print(f"✅ Found {len(dismissed_players)} historical dismissals")
            # Update state with historical data
            state.dismissed_players = dismissed_players
        else:
            print("ℹ️  No historical dismissal data available from API")
            print("   (This is normal - system will track dismissals going forward)")
    
    except Exception as e:
        print(f"⚠️  Could not fetch historical data: {e}")
        print("   (System will work fine - will track dismissals going forward)")
    
    return state


async def initialize_state_with_history() -> MatchState:
    """
    Initialize match state and fetch historical data from API.
    
    This is the recommended way to initialize the state:
    1. Creates base state
    2. Fetches historical dismissed players from API
    3. Returns complete state ready for use
    
    Returns:
        MatchState: Initialized state with historical data
    """
    from src.core.state import initialize_match_state
    
    # Start with base state
    state = initialize_match_state()
    
    # Fetch and add historical data
    state = await fetch_and_update_historical_data(state)
    
    return state

