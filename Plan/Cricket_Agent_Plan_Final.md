# Real-Time Cricket Commentary Agent System (MVP - Final Plan)

## Overview
Build a multi-agent system that generates real-time cricket match commentary. **MVP focuses on manual JSON event input, query routing, stats retrieval, and realistic probability calculations.** All specifications detailed below for immediate implementation.

## MVP Scope (Build Before Day 5)

### Phase 1: Foundation & Core Models

**Project Structure**: Create modular directory structure (`agents/`, `models/`, `data/`, `utils/`)

**State Models** (`models/state.py`): Complete Pydantic models with all required fields:

```python
class Batter(BaseModel):
    name: str
    runs: int
    balls_faced: int
    is_on_strike: bool

class Event(BaseModel):
    timestamp: datetime
    event_type: str  # "wicket", "runs", "maiden", "boundary", "dot", "wide", "no_ball"
    runs_scored: int = 0
    batter: str = None
    bowler: str = None
    overs_played: float
    dismissal_mode: str = None  # "caught", "bowled", "lbw", "stumped"
    fielder: str = None
    current_score: int  # Total runs after this ball
    current_wickets: int  # Wickets after this ball
    balls_in_over: int  # Which ball of the over (1-6)
    commentary: str = None  # Ball-by-ball description

class MatchState(BaseModel):
    match_id: str
    team_batting: str
    total_runs: int
    wickets_lost: int
    overs_played: float
    target: int
    current_batter: Batter
    recent_events: List[Event]
    p_draw: float
    p_sa_win: float
    last_updated: datetime
```

**State Initialization Function** (`models/state.py`):
```python
def initialize_match_state() -> MatchState:
    """Initialize Day 5 state for India vs SA."""
    return MatchState(
        match_id="117380",
        team_batting="India",
        total_runs=27,  # End of Day 4
        wickets_lost=2,
        overs_played=6.0,
        target=549,
        current_batter=Batter(name="Sai Sudharsan", runs=2, balls_faced=4, is_on_strike=True),
        recent_events=[],
        p_draw=0.35,
        p_sa_win=0.65,
        last_updated=datetime.now()
    )
```

**Dependencies**: Install Python packages (pydantic, asyncio, python-dotenv) - **NO OpenAI yet**

**Environment Setup**: Prepare `.env.example` for future OpenAI key (not needed for MVP)

### Phase 2: Manual Event Ingestion

**JSON Format Specification**: Exact format for manual input:

**Wicket Event:**
```json
{
  "event_type": "wicket",
  "timestamp": "2025-11-26T09:30:00+05:30",
  "batter": "Yashasvi Jaiswal",
  "bowler": "Marco Jansen",
  "dismissal_mode": "caught",
  "fielder": "Aiden Markram",
  "current_score": 45,
  "current_wickets": 3,
  "overs_played": 12.3,
  "balls_in_over": 3,
  "runs_scored": 0,
  "commentary": "Jaiswal caught at slip off Jansen's short delivery"
}
```

**Runs Event:**
```json
{
  "event_type": "runs",
  "timestamp": "2025-11-26T09:35:00+05:30",
  "batter": "Sai Sudharsan",
  "bowler": "Marco Jansen",
  "runs_scored": 4,
  "current_score": 49,
  "current_wickets": 3,
  "overs_played": 12.4,
  "balls_in_over": 4,
  "commentary": "Sudharsan drives through covers for four"
}
```

**Event Handler** (`agents/event_handler.py`):
- Async function to process manual JSON events
- Strict validation function:
  ```python
  def validate_event(event_dict):
      required_fields = ["event_type", "timestamp", "current_score", "current_wickets", "overs_played"]
      for field in required_fields:
          if field not in event_dict:
              raise ValueError(f"Missing required field: {field}")
      return Event(**event_dict)
  ```

**State Updates with Validation** (`agents/event_handler.py`):
```python
def update_state(state: MatchState, event: Event) -> MatchState:
    """Update state with event, validating transitions."""
    
    # Validate runs are non-negative
    if event.runs_scored < 0:
        raise ValueError("Runs cannot be negative")
    
    # Validate overs don't go backwards
    if event.overs_played < state.overs_played:
        raise ValueError(f"Overs went backwards: {state.overs_played} → {event.overs_played}")
    
    # Validate wickets don't exceed 10
    if event.event_type == "wicket":
        if state.wickets_lost + 1 > 10:
            raise ValueError("Cannot lose more than 10 wickets")
    
    # Update probability first (before creating new state)
    new_p_draw = update_probability(state.p_draw, event, state)
    
    # Rebuild state from scratch (safer than copy() - avoids shallow copy issues with recent_events list)
    new_state = MatchState(
        match_id=state.match_id,
        team_batting=state.team_batting,
        total_runs=event.current_score,  # Use event's current_score for accuracy
        wickets_lost=event.current_wickets,
        overs_played=event.overs_played,
        target=state.target,
        current_batter=state.current_batter,  # Update this if batter changed (future enhancement)
        recent_events=state.recent_events + [event],  # New list (not shared reference)
        p_draw=new_p_draw,
        p_sa_win=1.0 - new_p_draw,
        last_updated=event.timestamp
    )
    
    return new_state
```

**Mock Data** (`data/mock_events.json`): Pre-generated realistic event sequence (10-15 events) for testing

**Manual Input Pipeline**: CLI interface to paste/type JSON events during live match

### Phase 3: Query Router (Keyword-Based)

**Router Agent** (`agents/router.py`): Simple keyword matching (no LLM):
- `stats`: "score", "runs", "wickets", "overs"
- `momentum`: "momentum", "happening", "situation"
- `probability`: "chance", "draw", "win", "probability", "odds"
- `tactical`: "why", "how", "dismissed"
- Default: `stats` if no match

**Query Examples & Test Cases**:
```python
QUERY_EXAMPLES = {
    "What's the score?": "stats",
    "How many runs has Jaiswal scored?": "stats",
    "Who is batting now?": "stats",
    "What just happened?": "momentum",
    "Is India in trouble?": "momentum",
    "Who has the momentum?": "momentum",
    "Can India draw?": "probability",
    "What are India's chances?": "probability",
    "What's the win probability?": "probability",
    "Why did Jaiswal get out?": "tactical",
    "What was the dismissal?": "tactical",
    "How was Sudharsan dismissed?": "tactical",
}

# Test router
for query, expected_category in QUERY_EXAMPLES.items():
    assert route_query(query) == expected_category, f"Failed for: {query}"
```

**Error Handling**: Return helpful message: "I didn't understand that. Try: 'What's the score?', 'Can India draw?', 'What just happened?'"

### Phase 4: Stats & Probability Agents

**Stats Agent** (`agents/stats_agent.py`): Fetch current scorecard from state, format as readable string

**Probability Agent** (`models/win_probability.py`): Realistic model for Day 5 scenario:
```python
def update_probability(old_p_draw, event, state):
    p_draw = old_p_draw
    
    # Time decay (more overs = safer to draw)
    overs_remaining = 90 - state.overs_played
    time_factor = min(1.0, 1 + (overs_remaining / 90) * 0.2)  # Max +20% boost
    p_draw *= time_factor
    
    # Wicket penalty (India already weak at 2/3)
    if event.event_type == 'wicket':
        if state.wickets_lost < 5:
            p_draw *= 0.85  # Lose 15% per wicket early
        else:
            p_draw *= 0.70  # Lose 30% if already 5+ down (collapse risk)
    
    # Runs scored (boundaries help survival)
    if event.event_type == 'runs':
        if event.runs_scored >= 4:
            p_draw *= 1.05  # Boundary helps survival
    
    # Cap between 0.05 and 0.95 (always chance of collapse or counter-attack)
    return max(0.05, min(0.95, p_draw))
```

Accounts for: India's weak position (2/3), required run rate (5.8 runs/over), Day 5 pitch deterioration

**Initial State**: P(draw) = 0.35, P(SA win) = 0.65 at start of Day 5

### Phase 5: Main Orchestration (Async)

**Main Pipeline** (`main.py`): Async event loop using `asyncio`:
```python
async def main():
    state = initialize_match_state()
    event_queue = asyncio.Queue()
    
    # Manual event input task (non-blocking)
    asyncio.create_task(manual_event_input(event_queue))
    
    # Main loop: Process events + handle queries
    while True:
        if not event_queue.empty():
            event = await event_queue.get()
            state = update_state(state, event)  # With validation
            state.p_draw = update_probability(state.p_draw, event, state)
        
        if user_query_available():
            query = get_user_query()
            category = route_query(query)
            response = await handle_query(category, query, state)
            print(response)
```

**CLI Interface Design**: Exact UX specification:
```
=== Cricket Commentary Agent ===
Match: India vs SA, Day 5

Current State:
  India: 27/2 (Jaiswal 13, Rahul 6, Sudharsan 2*)
  Target: 549
  P(Draw): 35%

Enter event JSON or query:
> {"event_type": "runs", "batter": "Sudharsan", "runs_scored": 4, "current_score": 31, "current_wickets": 2, "overs_played": 7.1}

Event processed!
India: 31/2
P(Draw): 36%

Enter query:
> What's the score?

[STATS] India: 31 for 2 in 7.1 overs. Target: 549. Overs remaining: ~82.5.

Enter query:
> Can India draw?

[PROBABILITY] P(Draw): 36%, P(SA Win): 64%. India need to bat 82+ overs without losing more than 4 wickets.

Enter event or query (type 'exit' to quit):
> exit

Goodbye!
```

**Error Handling**: Comprehensive try/except blocks:
- Malformed JSON: "Invalid JSON format. Please check your event structure."
- Invalid queries: "I didn't understand that. Try: 'What's the score?', 'Can India draw?', 'What just happened?'"
- State validation errors: "Invalid state transition: [specific error message]"
- Timeout errors: "Processing took too long. Here's what I know: [fallback response]"

## Post-MVP Features (Build After Day 5)

### Phase 6: OpenAI Integration (Cost-Optimized)
- LLM Client with response caching, batch processing
- Momentum Agent for narrative generation
- Use `gpt-4o-mini` or `gpt-3.5-turbo` only for narrative generation

### Phase 7: Dual-Thread Racing & Judge
- Facts Agent: Race Thread A (factual) vs Thread B (narrative) with 2-second timeout
- Judge Agent: Specific criteria for each query type

### Phase 8: Live API Integration
- Cricbuzz unofficial API or ESPN Cricinfo scraper
- Auto polling every 30 seconds, with manual JSON fallback

### Phase 9: Visualization
- Plot P(draw) over time
- Update every 10 overs (not every event)
- Mark wickets as red dots, half-centuries as green
- Save PNG to disk

## Technical Decisions

**Architecture**: Async/Await (Not Threading) - Use Python's `asyncio` for concurrency

**Data Source**: Manual JSON First - MVP uses manual input, post-MVP adds API

**OpenAI**: Deferred & Optimized - MVP has no OpenAI, post-MVP adds with caching

**Error Handling**: Comprehensive validation at every layer

## File Structure
```
AI_Agent_System/
├── agents/
│   ├── __init__.py
│   ├── router.py              # MVP: Keyword-based routing + test cases
│   ├── event_handler.py      # MVP: Manual JSON processing + validation
│   ├── stats_agent.py         # MVP: Scorecard formatting
│   ├── momentum_agent.py      # Post-MVP: OpenAI narrative
│   ├── facts_agent.py         # Post-MVP: Thread racing
│   ├── judge.py               # Post-MVP: Response selection
│   └── corrective_agent.py    # Post-MVP: Style correction
├── models/
│   ├── __init__.py
│   ├── state.py               # MVP: Complete Pydantic models + initialization
│   └── win_probability.py     # MVP: Realistic probability calc
├── utils/
│   ├── __init__.py
│   ├── cricket_api.py         # Post-MVP: API integration
│   └── llm_client.py          # Post-MVP: OpenAI wrapper
├── data/
│   └── mock_events.json       # MVP: Test data (10-15 events)
├── .env.example
├── .gitignore
├── requirements.txt
├── main.py                     # MVP: Async orchestration + CLI
└── visualize.py               # Post-MVP: Probability plots
```

## Implementation Order (MVP First)

### Day 1-2 (Before Match):
1. Setup project structure and dependencies (no OpenAI)
2. Create complete state models with initialization (`models/state.py`)
3. Build manual event handler with validation (`agents/event_handler.py`)
4. Implement keyword-based router with test cases (`agents/router.py`)
5. Create stats agent (`agents/stats_agent.py`)
6. Build realistic probability model (`models/win_probability.py`)
7. Wire up async main loop with CLI (`main.py`)
8. Test with mock events JSON

### Day 2-3 (Optional, Before Match):
9. Add basic visualization (text updates + simple plot)
10. Create mock narrative responses (no OpenAI yet)

### Post-Day-5 (Refinement):
11. Integrate OpenAI for narrative generation (with caching)
12. Build dual-thread racing system
13. Implement judge and corrective agents
14. Add Cricbuzz API scraper
15. Enhance probability model based on actual outcomes
16. Build live web dashboard (optional)

## Pre-Coding Checklist (All Items Specified Above)

- [x] **Event schema** (all fields needed for Day 5)
- [x] **Manual JSON format** (exact structure specified)
- [x] **MatchState initialization** (Day 5 starting numbers)
- [x] **Probability model math** (realistic for India's weak position)
- [x] **Query examples** (test cases for router)
- [x] **State validation rules** (what transitions are illegal)
- [x] **CLI mockup** (user experience flow)
- [x] **Mock events** (10-15 realistic Day 5 events for testing)

## Key MVP Files to Create

- `models/state.py`: Complete Pydantic models (Batter, Event with all fields, MatchState) + initialization function
- `agents/event_handler.py`: Async event processing from manual JSON + strict validation + state update with validation (rebuild from scratch, not copy())
- `agents/router.py`: Simple keyword-based query classification + test cases
- `agents/stats_agent.py`: Scorecard data retrieval and formatting
- `models/win_probability.py`: Realistic probability calculation for Day 5 scenario
- `main.py`: Async orchestration loop with event queue + CLI interface as specified

## Important Fix Applied

**State Update Fix**: The plan uses `MatchState(...)` rebuild from scratch instead of `state.copy()` to avoid shallow copy issues with the `recent_events` list. This ensures state integrity during live match processing.

