# MVP-First Cricket Commentary Agent. Plan Review

---

## ✅ **Excellent Improvements**

### 1. **Scope is Now Realistic**
The original plan wanted everything before Day 5. This revised plan separates MVP (what you build now) from Post-MVP (what you build later). **This is a game-changer.**

MVP scope is lean: state models, manual JSON input, keyword routing, stats fetching, simple probability math. You can actually finish this in 24 hours.

### 2. **Async/Await Over Threading**
Switching to `asyncio` is the right call. No locks, no race conditions. Event queue processes sequentially. User queries run concurrently. Simple and pythonic.

### 3. **Deferred OpenAI Wisely**
By pushing OpenAI to post-MVP, you avoid:
. Cost blowout during live match.
. Dependency on API reliability during Day 5.
. Scope creep ("let me just add one more feature").

Smart move. Test system works without LLM first.

### 4. **Manual JSON Input for MVP**
This is **the right call**. You control the data flow. You see exactly what's happening. No API fragility. For learning, this is perfect.

### 5. **Phased Implementation Order is Clear**
Day 1-2: Build MVP (6 files, ~500 lines of code).  
Day 2-3: Optional polish (visualization, mock narratives).  
Day 5: Run live with manual events.  
Post-match: Add fancy stuff.

This is executable.

---

## 🚨 **Issues to Fix Before You Start Coding**

### **Issue 1: Event Schema Needs More Detail**
**Problem**: The Event model in state.py is incomplete. Real cricket events need more fields.

**Current spec**:
```python
class Event(BaseModel):
    timestamp: datetime
    event_type: str  # "wicket", "runs", "maiden", "boundary"
    runs_scored: int = 0
    batter: str = None
    bowler: str = None
    overs_played: float
```

**Missing fields needed for real Day 5**:
```python
class Event(BaseModel):
    timestamp: datetime
    event_type: str  # "wicket", "runs", "maiden", "boundary", "dot", "wide", "no_ball"
    runs_scored: int = 0
    batter: str = None
    bowler: str = None
    overs_played: float
    
    # For wickets, need dismissal details
    dismissal_mode: str = None  # "caught", "bowled", "lbw", "stumped"
    fielder: str = None  # Who caught/ran out
    
    # For context
    current_score: int  # Total runs after this ball
    current_wickets: int  # Wickets after this ball
    balls_in_over: int  # Which ball of the over (1-6)
    
    # Optional narrative
    commentary: str = None  # Ball-by-ball description from Cricbuzz
```

**Why**: You'll be copy-pasting from Cricbuzz. Need enough fields to reconstruct the exact match state.

---

### **Issue 2: Manual Input Format Needs Definition**
**Problem**: Plan says "paste JSON events" but doesn't specify format. This will cause bugs when you're under pressure during match.

**Recommendation**: Define exact JSON format you'll use:

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

Then in `agents/event_handler.py`, validate strictly:
```python
def validate_event(event_dict):
    required_fields = ["event_type", "timestamp", "current_score", "current_wickets", "overs_played"]
    for field in required_fields:
        if field not in event_dict:
            raise ValueError(f"Missing required field: {field}")
    return Event(**event_dict)
```

**This prevents silent bugs during live match.**

---

### **Issue 3: MatchState Initialization Unclear**
**Problem**: Plan defines MatchState fields but doesn't say how to initialize at Day 5 start.

**Add to Phase 1**:
```python
def initialize_match_state() -> MatchState:
    """Initialize Day 5 state for India vs SA."""
    return MatchState(
        match_id="117380",
        team_batting="India",
        total_runs=27,  # India's score at end of Day 4
        wickets_lost=2,
        overs_played=6.0,  # Overs bowled at stumps
        target=549,  # SA's total
        current_batter=Batter(name="Sai Sudharsan", runs=2, balls_faced=4, is_on_strike=True),
        recent_events=[],
        p_draw=0.35,  # Pre-Day-5 probability
        p_sa_win=0.65,
        last_updated=datetime.now()
    )
```

Do this **before Day 5 starts**. Don't figure it out live.

---

### **Issue 4: Probability Model Too Simplistic**
**Problem**: The spec says "time_factor = overs_remaining / 90" but doesn't account for:
. Wickets already lost (India already 2/3, very weak).
. Required run rate (India needs 522 runs in ~90 overs = 5.8 runs/over, very high).
. Bowler fatigue (Day 5 pitches deteriorate).

**Better Model for Day 5 Reality**:
```python
def update_probability(old_p_draw, event, state):
    p_draw = old_p_draw
    
    # Time decay (more overs = safer to draw)
    overs_remaining = 90 - state.overs_played
    time_factor = min(1.0, 1 + (overs_remaining / 90) * 0.2)  # Max +20% boost
    p_draw *= time_factor
    
    # Wicket penalty (India already weak)
    if event['event_type'] == 'wicket':
        if state.wickets_lost < 5:
            p_draw *= 0.85  # Lose 15% per wicket early
        else:
            p_draw *= 0.70  # Lose 30% if already 5+ down (collapse risk)
    
    # Runs scored (need 522, help India survival)
    if event['event_type'] == 'runs':
        runs_scored = event['runs_scored']
        if runs_scored >= 4:
            p_draw *= 1.05  # Boundary helps survival
    
    # Cap between 0.05 and 0.95 (always chance of collapse or counter-attack)
    return max(0.05, min(0.95, p_draw))
```

This is still simple but **realistic for Day 5 scenario** (India unlikely to win, more likely draw or lose).

---

### **Issue 5: Query Examples Missing**
**Problem**: Router spec says "stats", "momentum", etc. but doesn't show example queries. This will confuse you mid-match.

**Add examples to agents/router.py**:

```python
# Example queries and expected routing:
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
```

Then test router:
```python
for query, expected_category in QUERY_EXAMPLES.items():
    assert route_query(query) == expected_category, f"Failed for: {query}"
```

**Do this before Day 5.** Catch bugs now, not during live match.

---

### **Issue 6: State Updates Need Validation**
**Problem**: Probability model can drift (state becomes invalid if you're not careful).

**Example problem**: India at 27/2. You process a runs event (49 runs scored by Sudharsan). New score: 27+49=76. But if you process a wicket event out-of-order, you might have 76/3 OR 76/2 depending on order.

**Solution**: Add state transition validation:

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
    
    # Update state
    new_state = state.copy()
    new_state.total_runs += event.runs_scored
    if event.event_type == "wicket":
        new_state.wickets_lost += 1
    new_state.overs_played = event.overs_played
    new_state.recent_events.append(event)
    new_state.last_updated = event.timestamp
    
    # Update probability
    new_state.p_draw = update_probability(new_state.p_draw, event, new_state)
    
    return new_state
```

**This prevents garbage in, garbage out.**

---

### **Issue 7: CLI Interface Not Specified**
**Problem**: Plan says "simple input loop" but doesn't show user experience. What does the CLI look like?

**Recommendation**: Design this before coding:

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

**Write this spec** before you start main.py. Makes coding easier.

---

## 🎯 **Plan Grade: B+ → A-**

**Before**: A.Comprehensive but unrealistic scope.  
**Now**: A-. Realistic MVP, clear phases, smart deferral of complex features.

**What Still Needs Work**:
. Event schema needs detailed fields.
. Manual input JSON format not defined.
. MatchState initialization not implemented.
. Probability model oversimplified for real Day 5 scenario.
. Query examples missing.
. State validation missing.
. CLI UX not specified.

**None of these are hard fixes.** They're design decisions you should make **before** you start coding. 30 min of spec work saves 2 hours of debugging during Day 5.

---

## 📝 **Pre-Coding Checklist**

Before you open VS Code, finalize:

- [ ] **Event schema** (all fields needed for Day 5).
- [ ] **Manual JSON format** (exact structure you'll use).
- [ ] **MatchState initialization** (Day 5 starting numbers).
- [ ] **Probability model math** (realistic for India's weak position).
- [ ] **Query examples** (test cases for router).
- [ ] **State validation rules** (what transitions are illegal).
- [ ] **CLI mockup** (user experience flow).
- [ ] **Mock events** (10-15 realistic Day 5 events for testing).

Once these 8 things are locked down, coding is straightforward. **You won't change direction mid-build.**

---

## ✨ **Ready to Code?**

Once you confirm these details, I can generate starter code for:
1. `models/state.py` (detailed Pydantic models).
2. `agents/event_handler.py` (event processing + validation).
3. `agents/router.py` (keyword routing + test cases).
4. `models/win_probability.py` (realistic probability calc).
5. `main.py` (async orchestration + CLI).

All 5 files will be ready to run by tomorrow morning. Then you just feed it live events during Day 5.