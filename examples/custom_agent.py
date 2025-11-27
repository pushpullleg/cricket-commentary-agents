"""
Example: Creating a custom agent.

This example shows how to create a custom agent that extends
the system's functionality.
"""

import asyncio
from src.core.state import MatchState
from src.services.llm_client import get_intelligent_response


async def custom_analysis_agent(state: MatchState, query: str) -> str:
    """
    Example custom agent for custom analysis.
    
    This demonstrates how to create a new agent type that
    can be integrated into the system.
    
    Args:
        state: Current match state
        query: User query
    
    Returns:
        str: Custom analysis response
    """
    # Convert state to dict for LLM
    state_data = {
        "team_batting": state.team_batting,
        "total_runs": state.total_runs,
        "wickets_lost": state.wickets_lost,
        "overs_played": state.overs_played,
        "target": state.target,
        "p_draw": state.p_draw,
    }
    
    # Use LLM for intelligent response
    try:
        response = await get_intelligent_response(
            query,
            state_data,
            agent_type="custom"  # Custom agent type
        )
        if response:
            return response
    except Exception:
        pass
    
    # Fallback response
    return f"Custom analysis: {state.team_batting} is at {state.total_runs}/{state.wickets_lost}"


async def example_custom_agent():
    """Demonstrate using a custom agent."""
    from src.core.state import initialize_match_state
    
    print("=" * 60)
    print("Custom Agent Example")
    print("=" * 60)
    
    state = initialize_match_state()
    query = "Provide a custom analysis of the match situation"
    
    response = await custom_analysis_agent(state, query)
    print(f"\nCustom Agent Response: {response}")


if __name__ == "__main__":
    asyncio.run(example_custom_agent())

