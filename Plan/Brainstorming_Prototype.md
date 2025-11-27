# Agent-Oriented Real-Time Sports Commentary System
## Live Prototype: India vs South Africa Test Match (Day 5, Nov 26, 2025)

---

## Match Context (Your Real Use Case)

**Match**: 2nd Test, Guwahati (Barsapara Stadium)  
**Status**: End of Day 4. India needs 522 runs to win (target: 549).  
**Current Position**: India at 27/2 (Jaiswal 13, Rahul 6, Sudharsan 2*, Kuldeep 4*)  
**Time Zone**: Match in IST (India). You're in US. Day 5 starts ~9:00 PM US Eastern (Nov 25).  
**Match Outcome**: South Africa likely to win or India to survive for a draw.

### Why This Matters for Your Prototype
. You can track real match events as they unfold.
. Test cricket has slower pace than T20 (perfect for simulating agentic processing).
. Wickets, partnerships, and momentum shifts create natural "decision points" for your agents.
. Final day = high-stakes questions: "Can India survive?", "What are win odds now?", "Is a draw possible?".

---

## Core Concepts (from Tennis AI, adapted for Cricket)

### 1. **Agent Graph Operating on Live Events**
- **Tool Agent**: Extracts latest scorecard (runs, wickets, overs played).
- **Facts Agent**: Races two threads. one factual synopsis, one narrative commentary.
- **Judge Agent**: Picks best response based on accuracy + relevance.
- **Corrective Agent**: Fixes stylistic issues. ensures tone matches user expectation.

### 2. **Query Classification + Routing**
Your system should handle these live questions:
- **Match Stats**: "Who has scored most runs?" → Fetch scorecard data.
- **Win Probability**: "What are India's chances now?" → Update P(draw) / P(SA win) every wicket.
- **Momentum Narrative**: "Who has momentum right now?" → Synthesize run rate + recent dismissals.
- **Tactical Insight**: "Why did Jaiswal get out?" → Recall ball type, bowler, context.
- **Series Impact**: "Can India still level the series?" → Context-aware answer.

### 3. **Dual-Thread Racing with Timeout**
```
Thread A (Factual):
  "India: 27 for 2. Jaiswal (13) dismissed by Jansen cutting. 
   Rahul (6) bowled by Harmer. Target 549. Overs remaining: ~90."

Thread B (Narrative):
  "South Africa's dream day continues as India's openers fall 
   under pressure on a turning pitch. Marco Jansen's pace mixed 
   with Harmer's spin creating chaos. Can India bat 6 sessions to survive?"

Winner: First valid response within 2 seconds. Judge picks based on 
        user query type (factual vs narrative).
```

### 4. **Live Probability Updates**
- **Pre-Day-5 Model**: P(India draw) = 35%, P(SA win) = 65%.
- **Each wicket event**: Recalculate. Every run, update run rate burn.
- **Event Booster**: Jaiswal or Rahul scoring 50+ → P(draw) jumps 10%.
- **Time Decay**: Each passing over → P(draw) increases slightly (time working for batsmen).
- **Graph Visualization**: Show P(win) curve over time. dramatic swings when dismissals happen.

### 5. **Transparency + Confidence Signals**
- Show user what the agent is thinking: "Analyzing scorecard... classifying query... fetching win probability model..."
- Append confidence preamble if uncertain: "**Based on available data, likely answer**: India 27 for 2 at stumps. However, exact current score unavailable. Refresh for live updates."

---

## Prototype Project: Real-Time Cricket Agent

### Your Input Data
Live match events fed as JSON stream (simulated or from an API):
```json
{
  "event_type": "wicket",
  "timestamp": "2025-11-26T03:00:00Z",
  "batter_out": "Yashasvi Jaiswal",
  "bowler": "Marco Jansen",
  "runs_at_dismissal": 13,
  "ball_type": "short pitched",
  "dismissal_mode": "caught"
}
```

```json
{
  "event_type": "runs",
  "timestamp": "2025-11-26T03:15:00Z",
  "runs_scored": 4,
  "batter": "Sai Sudharsan",
  "over_number": 18
}
```

### System Architecture (Local, Python)

```
┌──────────────────────────────────────┐
│  LIVE EVENT STREAM (JSON)            │
│  (Wickets, runs, overs ticking)      │
└──────────────────┬───────────────────┘
                   │
         ┌─────────▼──────────┐
         │  ROUTER AGENT      │
         │ (Classify query)   │
         └─────────┬──────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
  STATS          MOMENTUM      PROBABILITY
  AGENT          AGENT         AGENT
     │             │             │
     ▼             ▼             ▼
┌────────┐  ┌──────────┐  ┌────────────┐
│Fetch   │  │Narrative │  │Update P()  │
│scorecard   │race:    │  │with decay+ │
│data    │  │fact vs  │  │event boost │
└────────┘  │narrative│  │            │
            └──────────┘  └────────────┘
                   │             │
                   └─────┬───────┘
                         │
              ┌──────────▼────────────┐
              │  JUDGE AGENT         │
              │  Pick best output    │
              │  Check confidence    │
              └──────────┬───────────┘
                         │
              ┌──────────▼────────────┐
              │  CORRECTIVE AGENT    │
              │  Fix tone/style      │
              │  Add context         │
              └──────────┬───────────┘
                         │
              ┌──────────▼────────────┐
              │  RETURN TO USER      │
              │  + Visualization    │
              └──────────────────────┘
```

### Core Components to Build

**1. Event Ingestion Loop** (`event_handler.py`)
. Read live cricket events every 30 seconds (or real-time if API available).
. Update shared state object (current score, wickets, overs).

**2. Query Router** (`router.py`)
. User asks: "What's happening now?"
. Classify into: `stats` / `momentum` / `probability` / `tactical`.
. Route to appropriate agent pipeline.

**3. Facts Agent** (`facts_agent.py`)
```python
def thread_a_factual():
    """Extract pure data."""
    score = get_current_scorecard()
    return f"India {score['runs']}/{score['wickets']} in {score['overs']} overs."

def thread_b_narrative():
    """Generate story."""
    recent_events = get_last_3_wickets()
    return synthesize_narrative(recent_events)

# Race with 2-second timeout
winner = race_threads([thread_a_factual, thread_b_narrative], timeout=2)
```

**4. Probability Model** (`win_probability.py`)
```python
def update_probability(event):
    # Decay pre-match prior
    p_draw = old_p_draw * 0.98  # Small decay per over
    
    # Event booster
    if event['type'] == 'wicket' and event['is_key_player']:
        p_draw *= 0.85  # Key dismissal hurts draw chances
    
    if event['type'] == 'boundary' and event['batter_runs'] >= 50:
        p_draw *= 1.10  # Partnership building helps
    
    return p_draw
```

**5. Visualization** (`visualize.py`)
. Plot P(draw) over overs played.
. Mark wickets as red dots, half-centuries as green.
. Update every 5 minutes.

### Minimal Example: Day 5 Morning Simulation

```python
# Simulate first 3 hours of Day 5
events = [
    {"type": "runs", "runs": 6, "batter": "Sudharsan", "over": 18},
    {"type": "wicket", "batter_out": "Sudharsan", "bowler": "Harmer", "over": 22},
    {"type": "runs", "runs": 12, "batter": "Pant", "over": 25},
    {"type": "runs", "runs": 4, "batter": "Pant", "over": 28},
]

for event in events:
    # Update state
    state = update_match_state(state, event)
    
    # User query comes in
    user_query = "How are India doing?"
    
    # Route + execute agents
    response = agentic_pipeline(user_query, state)
    
    # Update probability visualization
    visualize(state.probability_history)
    
    print(response)
```

---

## Why This Works for You

✅ **Real match data**: Track India's actual Day 5 unfold in real-time.  
✅ **Modular agents**: Each handles one job. easy to test individually.  
✅ **Racing threads**: Teaches async + concurrency patterns.  
✅ **Probability tracking**: See win odds shift with every wicket.  
✅ **Narrative generation**: LLM synthesizes stats into human-readable commentary.  
✅ **Time zone aware**: Run local, but handle IST. to EST conversions.  
✅ **Fallback graceful**: If API fails, return stale data with confidence warning.

---

## Execution Plan

1. **Hour 1**: Build router + event ingestion. Classify sample queries.
2. **Hour 2**: Wire up facts agent. create threads A & B.
3. **Hour 3**: Build judge. add corrective agent.
4. **Hour 4**: Implement probability model. test with mock events.
5. **Hour 5**: Add visualization. test end-to-end.
6. **Day 5 Morning**: Run live as match unfolds. Stream events. watch agents work in real-time.

You'll have a live, functioning multi-agent system running locally by the time Day 5 starts. Then feed it real events and watch it react.

---

## Data Sources (Free APIs or Manual)

- **Cricbuzz/ESPN Cricinfo**: Scrape ball-by-ball or use their unofficial API.
- **Manual JSON feed**: Type events as they happen (best for learning).
- **Mock events**: Pre-generate realistic event sequence for testing.

Start with **mock events** (fastest). move to **manual feed** (best teaching tool). graduate to **API** later.