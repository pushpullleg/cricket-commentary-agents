"""
Main orchestration file for Cricket Commentary Agent.

This module implements the async event loop that:
1. Automatically fetches events from free cricket APIs
2. Handles user queries
3. Routes queries to appropriate agents
4. Updates match state and probabilities

CLI interface allows real-time interaction during live match.
Events are automatically fetched - no manual JSON input needed.
"""

import asyncio
import sys
import os

from src.core.state import MatchState, initialize_match_state
from src.agents.event_handler import update_state
from src.agents.router import route_query
from src.core.probability import update_probability
from src.services.cricket_api import poll_cricket_api
from src.services.historical_data import initialize_state_with_history


class CricketAgent:
    """
    Main agent orchestrator for cricket commentary system.
    
    This class manages the entire agent system lifecycle:
    - State initialization
    - Event processing
    - Query handling
    - API polling
    
    Example:
        >>> agent = CricketAgent(auto_poll=True, poll_interval=30)
        >>> await agent.run()
    """
    
    def __init__(self, auto_poll: bool = True, poll_interval: int = 30, fetch_history: bool = True):
        """
        Initialize the agent with Day 5 starting state.
        
        Args:
            auto_poll: Enable automatic API polling (default: True)
            poll_interval: Seconds between API polls (default: 30)
            fetch_history: Fetch historical dismissed players from API (default: True)
        """
        # Will be initialized in async run() method
        self.state = None
        self.event_queue = asyncio.Queue()
        self.running = True
        self.auto_poll = auto_poll
        self.poll_interval = poll_interval
        self.fetch_history = fetch_history
    
    def display_current_state(self):
        """Display current match state in CLI."""
        print("\n" + "=" * 50)
        print("=== Cricket Commentary Agent ===")
        print("Match: India vs SA, Day 5")
        print("\nCurrent State:")
        print(f"  India: {self.state.total_runs}/{self.state.wickets_lost} "
              f"({self.state.current_batter.name} {self.state.current_batter.runs}*)")
        print(f"  Target: {self.state.target}")
        print(f"  P(Draw): {self.state.p_draw:.0%}")
        print(f"  P(SA Win): {self.state.p_sa_win:.0%}")
        print("=" * 50 + "\n")
    
    async def handle_query(self, query: str) -> str:
        """
        Handle a user query by routing to appropriate agent.
        
        Args:
            query: User's query string
        
        Returns:
            str: Agent's response
        """
        try:
            # Route query to appropriate category
            category = route_query(query)
            
            # Handle based on category
            if category == "stats":
                from src.agents.stats_agent import get_stats_response_async
                response = await get_stats_response_async(self.state, query)
                return f"[STATS] {response}"
            
            elif category == "probability":
                from src.agents.probability_agent import get_probability_response_async
                response = await get_probability_response_async(self.state, query)
                return f"[PROBABILITY] {response}"
            
            elif category == "momentum":
                from src.agents.momentum_agent import get_momentum_response_async
                response = await get_momentum_response_async(self.state, query)
                return f"[MOMENTUM] {response}"
            
            elif category == "tactical":
                from src.agents.tactical_agent import get_tactical_response_async
                response = await get_tactical_response_async(self.state, query)
                return f"[TACTICAL] {response}"
            
            else:
                return "I didn't understand that. Try: 'What's the score?', 'Can India draw?', 'What just happened?'"
        
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    
    async def process_auto_events(self):
        """Process events from API polling queue."""
        while self.running:
            try:
                # Check for events from API
                if not self.event_queue.empty():
                    event = await asyncio.wait_for(self.event_queue.get(), timeout=0.1)
                    # Update state with event
                    self.state = update_state(self.state, event)
                    self.state.p_draw = update_probability(self.state.p_draw, event, self.state)
                    self.state.p_sa_win = 1.0 - self.state.p_draw
                    
                    print(f"\n🔄 Auto-update: {event.event_type} - Score: {self.state.total_runs}/{self.state.wickets_lost}")
                    print(f"   P(Draw): {self.state.p_draw:.0%}\n")
                else:
                    await asyncio.sleep(0.5)  # Small delay to avoid busy waiting
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"⚠️  Error processing auto event: {e}")
                await asyncio.sleep(1)
    
    async def run(self):
        """Main async event loop."""
        # Initialize state (with historical data if enabled)
        if self.fetch_history:
            print("🔄 Initializing state with historical data...")
            self.state = await initialize_state_with_history()
        else:
            self.state = initialize_match_state()
        
        self.display_current_state()
        
        # Start automated API polling if enabled
        # NOTE: This uses FREE APIs only - NO OpenAI calls, NO cost!
        if self.auto_poll:
            polling_task = asyncio.create_task(
                poll_cricket_api(self.state.match_id, self.state, self.event_queue, self.poll_interval)
            )
            # Start event processor
            event_processor = asyncio.create_task(self.process_auto_events())
        
        print("Enter your query (type 'exit' to quit):")
        if self.auto_poll:
            print("(Auto-polling enabled - events update automatically from free APIs)")
        print("(No manual JSON needed - everything is automated!)\n")
        
        while self.running:
            try:
                # Get user input - queries only (no JSON events)
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit command
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\nGoodbye!\n")
                    self.running = False
                    break
                
                # All input is treated as queries (no JSON parsing)
                response = await self.handle_query(user_input)
                print(f"\n{response}\n")
            
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!\n")
                self.running = False
                break
            
            except EOFError:
                print("\n\nGoodbye!\n")
                self.running = False
                break


async def main():
    """
    Entry point for the cricket agent system.
    
    Events are automatically fetched from free cricket APIs.
    Set auto_poll=False to disable automatic API polling.
    Set poll_interval to change how often API is polled (default: 30 seconds).
    Set FETCH_HISTORY=false to disable historical data fetching.
    """
    # Check if auto-polling should be enabled (default: True)
    auto_poll = os.getenv("AUTO_POLL", "true").lower() == "true"
    poll_interval = int(os.getenv("POLL_INTERVAL", "30"))
    fetch_history = os.getenv("FETCH_HISTORY", "true").lower() == "true"
    
    agent = CricketAgent(auto_poll=auto_poll, poll_interval=poll_interval, fetch_history=fetch_history)
    await agent.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)

