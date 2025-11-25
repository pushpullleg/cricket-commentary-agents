# Core Concepts from Tennis AI Agent System

## 1. **Agent-Oriented Architecture (Directed Graph)**
- Multiple discrete computational agents working as nodes.
- Information flows between agents via edges.
- Each agent has a specific responsibility (tool selection, fact-checking, judgment, correction).
- Agents execute in parallel using threads and timeouts.

## 2. **Real-Time Decision Tree Routing**
- User query gets classified into categories (match stats, live insights, etc.).
- Confidence thresholds determine which pipeline to follow.
- Fallback mechanisms activate when confidence is low.
- Moderation gates ensure safety (HAP filters for harmful content).

## 3. **Dual-Output Racing System**
- Multiple threads race to produce answers.
- First valid response wins. within a timeout.
- Judge agent evaluates outputs on factuality and relevance.
- Corrective agents fix stylistic/consistency issues.

## 4. **Streaming Data + Probabilistic Modeling**
- Real-time events trigger model updates (every point in tennis).
- Combines historical priors with live performance metrics.
- Likelihood-to-Win updates as match unfolds (time-decayed + event boosters).
- Data serialized to CDN for async access.

## 5. **Transparency & UX Priming**
- Visual indicators show LLM thinking process.
- Fact-checking displays confidence in responses.
- Pre-curated entry-level questions lower engagement barriers.
- Open-ended query field for custom questions.

---

# Small Prototype Project: **Live Sports Commentary Agent**

## Concept
Build a **multi-agent system that generates real-time commentary for a hypothetical sports match** (cricket, basketball, or simplified tennis). The system:
- Takes live scoring events as input.
- Routes queries through different agent pipelines.
- Races two response generators (one factual, one narrative).
- Updates win probability predictions.
- Returns user-friendly commentary.

## Tech Stack (Local, Minimal)
- **Python** (main orchestration).
- **LangChain** or simple function calls (agent logic).
- **Pydantic** (data structures for state management).
- **Matplotlib** (simple probability visualization).
- **JSON** (event streaming simulation).

## Project Structure

```
sports-agent/
├── agents/
│   ├── router.py          # Classify query → category
│   ├── fact_checker.py    # Verify data accuracy
│   ├── judge.py           # Evaluate outputs
│   └── synthesizer.py     # Generate commentary
├── models/
│   ├── win_probability.py # Track P(win) over time
│   └── state.py           # Shared context object
├── data/
│   ├── match_events.json  # Simulated live score data
│   └── sample_queries.py  # Pre-defined test questions
├── main.py                # Orchestrate agent flow
└── visualize.py           # Plot win probability trends
```

## Key Features to Implement

1. **Event Ingestion**: Simulate live score updates (wickets, points, etc.).
2. **Query Classification**: Map user questions → data categories (stats, momentum, predictions).
3. **Dual Generators**:
   - Thread A: Extract JSON. create factual summary.
   - Thread B: Generate narrative-style commentary.
   - Race them with a 2-second timeout. use the first valid response.
4. **Probabilistic Model**: Update win% after each event using a simple formula.
   - `new_prob = (old_prob * decay_factor) + (live_metric * event_boost)`
5. **Fallback Logic**: If confidence < threshold, return pre-trained response from knowledge base.
6. **Visualization**: Plot probability curve as match progresses.

## Example Flow (Cricket Match)

**Match starts**: Player A: 52% win probability. Player B: 48%.

**Event 1**: Team A scores 10 runs.
→ Router classifies query: "Who's winning?"
→ Tool agent fetches score data.
→ Facts agent races synthesizer.
→ Judge picks best output: *"Team A has taken the lead with 10 runs. Updated win probability: 58%."*
→ System stores update. visualizes trend.

**Event 2**: Team B loses a wicket.
→ Query: "What just happened?"
→ Model boosts event impact.
→ New probability: 62% for Team A.
→ Synthesizer adds narrative: *"A critical breakthrough for Team A... momentum has shifted."*

---

## Why This Works as a Learning Project

✅ **Modular agent design** mirrors the real system.
✅ **Parallel execution + racing** teaches async patterns.
✅ **Fallback pipelines** show resilience patterns.
✅ **Probability updates** introduce real-time state management.
✅ **Runs locally** with simulated data. no APIs needed.
✅ **Visuals** make outputs tangible and satisfying.

## Next Steps
1. Start with the router agent. classify a handful of questions.
2. Build the dual-thread synthesizer with mock data.
3. Implement the judge to pick winners.
4. Add probability model updates.
5. Visualize the full match journey.

This scales from a simple script to a genuinely useful system as you add complexity!