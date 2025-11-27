# Cricket Commentary Agent System

A professional, educational multi-agent system that generates real-time cricket match commentary using automated API event fetching, intelligent query routing, and probability calculations.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Learning Resources](#learning-resources)
- [Development](#development)

## Overview

This system is a **multi-agent architecture** for real-time cricket match analysis. It automatically fetches match events from free cricket APIs, maintains match state, and provides intelligent responses to user queries through specialized agents.

### Current State (Latest Version)

The system has evolved from a basic MVP to an **intelligent multi-agent system** with:

- ✅ **Automated Event Fetching**: Automatically polls free cricket APIs (Cricscore) every 30 seconds
- ✅ **Intelligent Agents**: All agents use OpenAI for natural language understanding with graceful fallback
- ✅ **Real-time State Management**: Maintains accurate match state with Pydantic models
- ✅ **Probability Calculations**: Dynamic win/draw probability updates based on match events
- ✅ **Historical Data Integration**: Can initialize with historical dismissed players from APIs
- ✅ **Professional Structure**: Clean, organized codebase perfect for learning

## Features

### Core Capabilities

1. **Automated API Polling**
   - Fetches events from free cricket APIs (no API keys required)
   - Polls every 30 seconds (configurable)
   - Detects new events and updates state automatically
   - Zero cost - uses only free APIs

2. **Intelligent Query Routing**
   - Classifies queries into 4 categories: stats, momentum, probability, tactical
   - Routes to specialized agents automatically

3. **Specialized Agents**
   - **Stats Agent**: Answers questions about scores, wickets, runs, batting status
   - **Momentum Agent**: Analyzes recent events and match momentum
   - **Probability Agent**: Calculates and explains win/draw probabilities
   - **Tactical Agent**: Analyzes dismissals and tactical situations
   - All agents use OpenAI for intelligent responses with keyword-based fallback

4. **State Management**
   - Pydantic models ensure type safety and validation
   - Atomic state updates prevent inconsistencies
   - Tracks dismissed players, recent events, and probabilities

5. **Probability Model**
   - Real-time win/draw probability calculations
   - Updates based on wickets, runs, overs remaining
   - Realistic probability adjustments

## Project Structure

```
AI_Agent_System/
├── src/                          # Source code
│   ├── core/                     # Core domain models
│   │   ├── state.py              # State models (Batter, Event, MatchState)
│   │   └── probability.py        # Probability calculations
│   ├── agents/                   # Specialized agents
│   │   ├── router.py             # Query classification
│   │   ├── event_handler.py      # Event processing
│   │   ├── stats_agent.py        # Statistics queries
│   │   ├── momentum_agent.py     # Momentum analysis
│   │   ├── probability_agent.py  # Probability analysis
│   │   └── tactical_agent.py     # Tactical analysis
│   ├── services/                 # External integrations
│   │   ├── cricket_api.py        # Free API client
│   │   ├── llm_client.py         # OpenAI integration
│   │   └── historical_data.py    # Historical data fetching
│   └── cli/                       # Command-line interface
│       └── main.py                # Main orchestration
├── tests/                         # Test suite
├── examples/                      # Usage examples
│   ├── basic_usage.py            # Basic usage example
│   └── custom_agent.py            # Custom agent example
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md            # Architecture documentation
│   └── LEARNING_GUIDE.md          # Learning guide
├── Plan/                          # Project planning (untouched)
├── main.py                        # Entry point
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables (optional):**
```bash
# Create .env file with:
OPENAI_API_KEY=your_key_here  # For intelligent agent responses
AUTO_POLL=true                 # Enable automatic API polling (default: true)
POLL_INTERVAL=30              # Seconds between API polls (default: 30)
FETCH_HISTORY=true            # Fetch historical data on startup (default: true)
```

## Usage

### Running the System

```bash
python main.py
```

The system will:
1. Initialize match state (with historical data if enabled)
2. Start automatic API polling (if enabled)
3. Display current match state
4. Accept user queries in real-time

### Example Queries

**Stats Queries:**
- "What's the score?"
- "How many wickets remaining?"
- "Who is batting now?"
- "How many runs has Jaiswal scored?"

**Momentum Queries:**
- "What just happened?"
- "Is India in trouble?"
- "Who has the momentum?"

**Probability Queries:**
- "Can India draw?"
- "What are India's chances?"
- "What's the win probability?"

**Tactical Queries:**
- "Why did Jaiswal get out?"
- "What was the dismissal?"
- "How was Sudharsan dismissed?"

### Running Examples

```bash
# Basic usage example
python examples/basic_usage.py

# Custom agent example
python examples/custom_agent.py
```

### Running Tests

```bash
# Run system tests
python tests/test_system.py

# Test API integration
python tests/test_free_api.py
```

## Architecture

The system follows a **layered architecture** with clear separation of concerns:

1. **Core Layer** (`src/core`): Domain models and business logic
2. **Service Layer** (`src/services`): External integrations (APIs, LLM)
3. **Agent Layer** (`src/agents`): Specialized query handlers
4. **CLI Layer** (`src/cli`): User interface and orchestration

### Key Design Patterns

- **Multi-Agent Pattern**: Specialized agents for different query types
- **Repository Pattern**: Service layer abstracts data sources
- **Strategy Pattern**: Different agents use different strategies
- **Observer Pattern**: Event queue for async processing

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Learning Resources

This codebase is designed to be **educational** and **learnable**. Key resources:

- **[Architecture Documentation](docs/ARCHITECTURE.md)**: Detailed system architecture
- **[Learning Guide](docs/LEARNING_GUIDE.md)**: Step-by-step learning path
- **[Examples](examples/)**: Working code examples
- **[Tests](tests/)**: Test examples showing usage

### Learning Path

1. **Beginner**: Read `src/core/state.py` → Understand data models
2. **Intermediate**: Read `src/agents/stats_agent.py` → Understand agent pattern
3. **Advanced**: Read `src/core/probability.py` → Understand probability model

See [docs/LEARNING_GUIDE.md](docs/LEARNING_GUIDE.md) for a complete learning path.

## Development

### Adding a New Agent

1. Create agent file in `src/agents/`
2. Implement async response function
3. Add routing logic in `src/agents/router.py`
4. Update `src/cli/main.py` to handle new category

### Adding a New Service

1. Create service file in `src/services/`
2. Implement service interface
3. Update `src/services/__init__.py`

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_system.py
```

## Configuration

Environment variables control system behavior:

- `AUTO_POLL`: Enable/disable automatic API polling (default: `true`)
- `POLL_INTERVAL`: Seconds between API polls (default: `30`)
- `FETCH_HISTORY`: Fetch historical dismissed players on startup (default: `true`)
- `OPENAI_API_KEY`: Required for intelligent agent responses (optional - falls back to keyword matching)

## Technical Details

### State Models

The system uses Pydantic models for type safety:

- `Batter`: Current batsman state (name, runs, balls faced)
- `Event`: Single cricket event (runs, wickets, etc.)
- `DismissedPlayer`: Information about dismissed players
- `MatchState`: Complete match state at any point

### Event Types

Events can be:
- `runs`: Runs scored (1-6, boundaries)
- `wicket`: Player dismissal
- `maiden`: Maiden over
- `boundary`: Four or six
- `dot`: Dot ball
- `wide`: Wide ball
- `no_ball`: No ball

### API Integration

The system uses **free cricket APIs**:
- **Primary**: Cricscore API (no API key required)
- **Fallback**: Cricbuzz scraping (if Cricscore unavailable)
- **Cost**: $0.00 - All free, no paid APIs for polling

### Probability Model

Win/draw probabilities are calculated based on:
- Wickets remaining
- Overs remaining
- Runs needed
- Recent event patterns

Probabilities update in real-time as events occur.

## Development Status

### Implemented Features ✅

- [x] Multi-agent architecture with query routing
- [x] Automated API polling from free sources
- [x] Intelligent agents with OpenAI integration
- [x] Graceful fallback mechanisms
- [x] Real-time state management
- [x] Probability calculations
- [x] Historical data integration
- [x] Event validation and processing
- [x] Response caching
- [x] Professional code organization
- [x] Comprehensive documentation

### Future Enhancements (Not Yet Implemented)

- [ ] Dual-thread racing system
- [ ] Judge and corrective agents
- [ ] Live Cricbuzz scraper integration
- [ ] Visualization (probability plots)
- [ ] Advanced narrative generation
- [ ] Multi-match support

## Notes

- The system is designed for **Test cricket** matches
- Default match is India vs South Africa, Day 5
- All API polling uses **free APIs only** - no costs
- OpenAI is optional - system works with keyword fallback
- State is maintained in memory (not persisted)

## License

MIT

---

**Built for learning and reference** - This codebase is organized to be educational, professional, and easy to understand. Perfect for studying multi-agent systems, async programming, and clean architecture patterns.
