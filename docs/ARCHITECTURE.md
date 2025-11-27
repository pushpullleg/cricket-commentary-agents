# Architecture Documentation

## System Overview

The Cricket Commentary Agent System is built using a **multi-agent architecture** with clear separation of concerns. The system is organized into distinct layers:

```
┌─────────────────────────────────────────┐
│           CLI Layer (src/cli)            │
│         User Interface & Orchestration   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Agent Layer (src/agents)         │
│  Router, Stats, Momentum, Probability,  │
│         Tactical, Event Handler         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Service Layer (src/services)        │
│    Cricket API, LLM Client, Historical │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Core Layer (src/core)            │
│    State Models, Probability Models     │
└─────────────────────────────────────────┘
```

## Layer Descriptions

### Core Layer (`src/core`)

**Purpose**: Domain models and business logic

- **`state.py`**: Core data models (Batter, Event, MatchState, DismissedPlayer)
- **`probability.py`**: Win/draw probability calculations

**Key Principles**:
- Immutable state transitions
- Type safety with Pydantic
- Pure business logic (no external dependencies)

### Service Layer (`src/services`)

**Purpose**: External integrations and utilities

- **`cricket_api.py`**: Free cricket API client (Cricscore, Cricbuzz)
- **`llm_client.py`**: OpenAI integration with caching
- **`historical_data.py`**: Historical data fetching

**Key Principles**:
- Abstract external APIs
- Graceful error handling
- Cost optimization (caching, free APIs)

### Agent Layer (`src/agents`)

**Purpose**: Specialized query handlers

- **`router.py`**: Query classification
- **`event_handler.py`**: Event validation and state updates
- **`stats_agent.py`**: Statistics queries
- **`momentum_agent.py`**: Momentum analysis
- **`probability_agent.py`**: Probability analysis
- **`tactical_agent.py`**: Tactical analysis

**Key Principles**:
- Single responsibility per agent
- Intelligent responses with fallback
- Async-first design

### CLI Layer (`src/cli`)

**Purpose**: User interface and orchestration

- **`main.py`**: Main event loop and CLI interface

**Key Principles**:
- User-friendly interface
- Real-time updates
- Graceful shutdown

## Data Flow

### Query Processing Flow

```
User Query
    │
    ▼
Router Agent (classify query)
    │
    ├─► Stats Agent ──► LLM Client ──► Response
    ├─► Momentum Agent ──► LLM Client ──► Response
    ├─► Probability Agent ──► LLM Client ──► Response
    └─► Tactical Agent ──► LLM Client ──► Response
```

### Event Processing Flow

```
API Polling
    │
    ▼
Cricket API Client (fetch data)
    │
    ▼
Event Detection (compare with state)
    │
    ▼
Event Handler (validate & update)
    │
    ├─► State Update
    └─► Probability Update
```

## Design Patterns

### 1. Multi-Agent Pattern
- Specialized agents for different query types
- Router pattern for query classification
- Agent coordination through shared state

### 2. Repository Pattern
- Service layer abstracts data sources
- Easy to swap API implementations
- Testable with mock services

### 3. Strategy Pattern
- Different agents use different strategies
- Fallback mechanisms (LLM → keyword matching)
- Pluggable agent implementations

### 4. Observer Pattern
- Event queue for async processing
- State updates trigger probability recalculations
- Real-time UI updates

## State Management

### Immutable State Updates

State is updated immutably - each event creates a new state object:

```python
new_state = MatchState(
    match_id=state.match_id,
    total_runs=event.current_score,
    # ... other fields
)
```

**Benefits**:
- Thread-safe
- Easy to debug (state history)
- No side effects

### State Validation

All state transitions are validated:
- Runs cannot be negative
- Overs cannot go backwards
- Wickets cannot exceed 10

## Error Handling

### Graceful Degradation

1. **API Failures**: System continues with last known state
2. **LLM Failures**: Fallback to keyword matching
3. **Event Validation Failures**: Error message, state unchanged

### Error Recovery

- Automatic retry for API polling
- Cache for LLM responses
- Validation prevents invalid states

## Performance Considerations

### Caching

- LLM responses cached by query + state hash
- Reduces API costs
- Faster responses for repeated queries

### Async Operations

- Non-blocking API calls
- Concurrent event processing
- Efficient resource usage

### Cost Optimization

- Free APIs for polling (no cost)
- LLM only for intelligent responses
- Caching reduces redundant calls

## Extensibility

### Adding New Agents

1. Create agent file in `src/agents/`
2. Implement async response function
3. Add routing logic in `router.py`
4. Update `src/agents/__init__.py`

### Adding New Services

1. Create service file in `src/services/`
2. Implement service interface
3. Update `src/services/__init__.py`
4. Use in agents or CLI

### Customizing State

1. Extend models in `src/core/state.py`
2. Update initialization in `initialize_match_state()`
3. Update event handler for new fields

## Testing Strategy

### Unit Tests

- Test individual agents in isolation
- Mock external services
- Test state transitions

### Integration Tests

- Test agent coordination
- Test API integrations
- Test end-to-end flows

### Example Tests

See `tests/` directory for examples.

