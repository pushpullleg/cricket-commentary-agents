"""
LLM client for OpenAI integration.

Provides intelligent query understanding and response generation.
Includes response caching to minimize API costs.

This service abstracts away OpenAI API details and provides a simple
interface for getting intelligent responses with automatic caching.
"""

import os
import json
import hashlib
from typing import Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Response cache to avoid redundant API calls
_response_cache: Dict[str, str] = {}


def get_openai_client() -> Optional[OpenAI]:
    """
    Get OpenAI client if API key is available.
    
    Returns:
        OpenAI client or None if API key not found
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def _get_cache_key(query: str, state_data: Dict[str, Any]) -> str:
    """
    Generate cache key from query and state.
    
    Args:
        query: User query
        state_data: Match state data
    
    Returns:
        str: Cache key
    """
    # Create hash from query + key state fields
    cache_data = {
        "query": query.lower().strip(),
        "runs": state_data.get("total_runs"),
        "wickets": state_data.get("wickets_lost"),
        "overs": round(state_data.get("overs_played", 0), 1),  # Round to avoid float precision issues
    }
    cache_str = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(cache_str.encode()).hexdigest()


async def get_intelligent_response(
    query: str,
    state_data: Dict[str, Any],
    agent_type: str = "stats"
) -> Optional[str]:
    """
    Get intelligent response from OpenAI for a query.
    
    Uses caching to avoid redundant API calls for identical queries/states.
    
    Args:
        query: User's query
        state_data: Current match state data
        agent_type: Type of agent ("stats", "momentum", "probability", "tactical")
    
    Returns:
        str: Intelligent response, or None if OpenAI unavailable
    """
    client = get_openai_client()
    if not client:
        return None
    
    # Check cache first
    cache_key = _get_cache_key(query, state_data)
    if cache_key in _response_cache:
        return _response_cache[cache_key]
    
    # Build context for the LLM based on agent type
    base_context = f"""
You are a cricket commentary agent answering questions about a live Test match.

Current Match State:
- Team: {state_data.get('team_batting', 'India')}
- Score: {state_data.get('total_runs', 0)}/{state_data.get('wickets_lost', 0)}
- Overs played: {state_data.get('overs_played', 0):.1f}
- Target: {state_data.get('target', 0)} runs
"""
    
    # Add agent-specific context
    if agent_type == "stats":
        context = base_context + f"""
- Current batsman: {state_data.get('current_batter', {}).get('name', 'Unknown')} ({state_data.get('current_batter', {}).get('runs', 0)}* runs)
- Wickets remaining: {10 - state_data.get('wickets_lost', 0)}
- Runs needed: {state_data.get('target', 0) - state_data.get('total_runs', 0)}

User Question: {query}

Provide a concise, accurate answer about match statistics. Be specific with numbers.
"""
    
    elif agent_type == "probability":
        context = base_context + f"""
- Overs remaining: {state_data.get('overs_remaining', 0):.1f}
- Wickets remaining: {state_data.get('wickets_remaining', 0)}
- Runs needed: {state_data.get('runs_needed', 0)}
- P(Draw): {state_data.get('p_draw', 0):.0%}
- P(SA Win): {state_data.get('p_sa_win', 0):.0%}

User Question: {query}

Analyze the probability of different match outcomes. Consider the match situation, required run rate, wickets remaining, and time left.
"""
    
    elif agent_type == "momentum":
        recent_events = state_data.get('recent_events', [])
        context = base_context + f"""
- Recent events: {', '.join(recent_events) if recent_events else 'None'}
- P(Draw): {state_data.get('p_draw', 0):.0%}
- P(SA Win): {state_data.get('p_sa_win', 0):.0%}

User Question: {query}

Analyze the current momentum in the match. Consider recent events, scoring rate, wickets, and which team has the upper hand.
"""
    
    elif agent_type == "tactical":
        recent_events = state_data.get('recent_events', [])
        context = base_context + f"""
- Current batsman: {state_data.get('current_batter', {}).get('name', 'Unknown')} ({state_data.get('current_batter', {}).get('runs', 0)}* runs)
- Recent events: {recent_events}

User Question: {query}

Provide tactical analysis of dismissals, bowling strategies, batting approaches, and match situation.
"""
    
    else:
        context = base_context + f"""
User Question: {query}

Provide a concise, accurate answer based on the match state. Be specific and helpful.
Answer naturally, as if you're a cricket commentator.
"""
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective model
            messages=[
                {"role": "system", "content": "You are a helpful cricket commentary assistant. Answer questions accurately and concisely."},
                {"role": "user", "content": context}
            ],
            max_tokens=150,
            temperature=0.3,  # Lower temperature for more factual responses
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Cache the response
        _response_cache[cache_key] = answer
        
        return answer
    
    except Exception:
        # If API call fails, return None (fallback to keyword matching)
        return None


def clear_cache():
    """Clear the response cache."""
    global _response_cache
    _response_cache = {}

