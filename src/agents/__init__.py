"""
Agents package for cricket agent system.

This package contains specialized agents that handle different types of queries:
- Router: Classifies queries into categories
- Event Handler: Processes and validates events
- Stats Agent: Answers statistics questions
- Momentum Agent: Analyzes match momentum
- Probability Agent: Calculates win/draw probabilities
- Tactical Agent: Provides tactical analysis
"""

from .router import route_query, QUERY_EXAMPLES
from .event_handler import validate_event, update_state, process_event
from .stats_agent import get_stats_response, get_stats_response_async
from .momentum_agent import get_momentum_response_async
from .probability_agent import get_probability_response_async
from .tactical_agent import get_tactical_response_async

__all__ = [
    "route_query",
    "QUERY_EXAMPLES",
    "validate_event",
    "update_state",
    "process_event",
    "get_stats_response",
    "get_stats_response_async",
    "get_momentum_response_async",
    "get_probability_response_async",
    "get_tactical_response_async",
]

