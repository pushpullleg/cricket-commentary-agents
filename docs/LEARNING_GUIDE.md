# Learning Guide

This guide helps you understand how the Cricket Commentary Agent System works and how to learn from it.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Code Walkthrough](#code-walkthrough)
4. [Key Patterns](#key-patterns)
5. [Extension Points](#extension-points)

## Getting Started

### Prerequisites

- Python 3.8+
- Understanding of:
  - Python async/await
  - Pydantic models
  - Basic REST APIs

### First Steps

1. **Read the README**: Understand what the system does
2. **Run the examples**: See it in action
3. **Read the code**: Start with `src/core/state.py`
4. **Trace a query**: Follow a query through the system

## Core Concepts

### 1. Multi-Agent Architecture

**What it is**: Multiple specialized agents handle different types of queries.

**Why it matters**: 
- Separation of concerns
- Easy to extend
- Clear responsibilities

**Where to see it**: `src/agents/` directory

**Key files**:
- `router.py`: Routes queries to agents
- `stats_agent.py`: Handles statistics queries
- `momentum_agent.py`: Analyzes match momentum

### 2. State Management

**What it is**: Immutable state updates using Pydantic models.

**Why it matters**:
- Type safety
- Validation
- Thread safety

**Where to see it**: `src/core/state.py`

**Key concepts**:
- `MatchState`: Complete match state
- `Event`: Single cricket event
- Immutable updates: `new_state = update_state(old_state, event)`

### 3. Intelligent Agents with Fallback

**What it is**: Agents use LLM for intelligent responses, fallback to keyword matching.

**Why it matters**:
- Works without API keys
- Cost optimization
- Graceful degradation

**Where to see it**: Any agent file (e.g., `src/agents/stats_agent.py`)

**Pattern**:
```python
try:
    response = await get_intelligent_response(...)
    if response:
        return response
except:
    pass
return fallback_response(...)
```

### 4. Async Event Processing

**What it is**: Non-blocking event processing with asyncio.

**Why it matters**:
- Real-time updates
- Efficient resource usage
- Concurrent operations

**Where to see it**: `src/cli/main.py`

**Key concepts**:
- `asyncio.Queue`: Event queue
- `asyncio.create_task`: Concurrent tasks
- `await`: Non-blocking operations

## Code Walkthrough

### Following a Query

Let's trace what happens when a user asks "What's the score?"

1. **CLI receives query** (`src/cli/main.py:168`)
   ```python
   response = await self.handle_query(user_input)
   ```

2. **Router classifies query** (`src/agents/router.py:31`)
   ```python
   category = route_query(query)  # Returns "stats"
   ```

3. **Stats agent processes** (`src/agents/stats_agent.py:112`)
   ```python
   response = await get_stats_response_async(state, query)
   ```

4. **LLM client (if available)** (`src/services/llm_client.py:57`)
   ```python
   response = await get_intelligent_response(query, state_data, "stats")
   ```

5. **Fallback (if LLM unavailable)** (`src/agents/stats_agent.py:45`)
   ```python
   return _get_keyword_response(state, query)
   ```

6. **Response returned** to user

### Following an Event

Let's trace what happens when a new event arrives:

1. **API polling** (`src/services/cricket_api.py:354`)
   ```python
   event = await client.get_latest_event(state)
   ```

2. **Event detection** (`src/services/cricket_api.py:172`)
   ```python
   event = client.detect_new_event(match_data, state)
   ```

3. **Event queued** (`src/cli/main.py:393`)
   ```python
   await event_queue.put(event)
   ```

4. **Event processed** (`src/cli/main.py:114`)
   ```python
   self.state = update_state(self.state, event)
   ```

5. **State updated** (`src/agents/event_handler.py:49`)
   ```python
   new_state = MatchState(...)  # New immutable state
   ```

6. **Probability updated** (`src/core/probability.py:17`)
   ```python
   new_p_draw = update_probability(old_p_draw, event, state)
   ```

## Key Patterns

### Pattern 1: Agent with Fallback

```python
async def get_response(state, query):
    # Try intelligent response first
    try:
        response = await get_intelligent_response(...)
        if response:
            return response
    except:
        pass
    
    # Fallback to simple logic
    return fallback_response(state, query)
```

**Why**: Works with or without API keys, cost-effective.

### Pattern 2: Immutable State Updates

```python
def update_state(state, event):
    # Create new state, don't modify old one
    return MatchState(
        total_runs=event.current_score,
        # ... other fields
    )
```

**Why**: Thread-safe, easy to debug, no side effects.

### Pattern 3: Service Abstraction

```python
class CricketAPIClient:
    async def fetch_match_data(self):
        # Try multiple sources
        data = await self._fetch_cricscore()
        if data:
            return data
        return await self._fetch_cricbuzz()
```

**Why**: Easy to swap implementations, testable.

### Pattern 4: Async Event Loop

```python
async def run(self):
    # Start background tasks
    polling_task = asyncio.create_task(poll_api(...))
    processor = asyncio.create_task(process_events(...))
    
    # Main loop
    while self.running:
        query = await get_user_input()
        response = await handle_query(query)
```

**Why**: Non-blocking, real-time updates.

## Extension Points

### Adding a New Agent

1. Create `src/agents/my_agent.py`:
```python
from src.core.state import MatchState
from src.services.llm_client import get_intelligent_response

async def get_my_agent_response_async(state: MatchState, query: str) -> str:
    # Your agent logic
    pass
```

2. Add routing in `src/agents/router.py`:
```python
if "my_keyword" in query_lower:
    return "my_agent"
```

3. Update `src/cli/main.py`:
```python
elif category == "my_agent":
    from src.agents.my_agent import get_my_agent_response_async
    response = await get_my_agent_response_async(self.state, query)
```

### Adding a New Service

1. Create `src/services/my_service.py`:
```python
async def my_service_function():
    # Your service logic
    pass
```

2. Update `src/services/__init__.py`:
```python
from .my_service import my_service_function
```

### Customizing State

1. Extend `src/core/state.py`:
```python
class MatchState(BaseModel):
    # ... existing fields
    my_new_field: str = "default"
```

2. Update initialization:
```python
def initialize_match_state():
    return MatchState(
        # ... existing fields
        my_new_field="value"
    )
```

## Learning Path

### Beginner

1. Read `src/core/state.py` - Understand data models
2. Read `src/agents/router.py` - See query routing
3. Run `examples/basic_usage.py` - See it in action

### Intermediate

1. Read `src/agents/stats_agent.py` - Understand agent pattern
2. Read `src/services/llm_client.py` - See service abstraction
3. Read `src/cli/main.py` - Understand orchestration

### Advanced

1. Read `src/core/probability.py` - Understand probability model
2. Read `src/services/cricket_api.py` - See API integration
3. Read `src/agents/event_handler.py` - Understand state updates

## Common Questions

### Q: Why immutable state?

**A**: Thread-safe, easier to debug, no side effects. Each event creates a new state object.

### Q: Why async everywhere?

**A**: Non-blocking operations, real-time updates, efficient resource usage.

### Q: Why fallback mechanisms?

**A**: Works without API keys, cost-effective, graceful degradation.

### Q: How do I add a new query type?

**A**: Create a new agent, add routing logic, update CLI handler.

### Q: How do I customize the probability model?

**A**: Modify `src/core/probability.py` - the `update_probability` function.

## Next Steps

1. **Experiment**: Modify agents, add features
2. **Test**: Write tests for your changes
3. **Extend**: Add new agents or services
4. **Learn**: Read related patterns and architectures

## Resources

- **Pydantic Docs**: https://docs.pydantic.dev/
- **Python Async**: https://docs.python.org/3/library/asyncio.html
- **Multi-Agent Systems**: Research papers and books
- **OpenAI API**: https://platform.openai.com/docs/

Happy learning! 🎓

