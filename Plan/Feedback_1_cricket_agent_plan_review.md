# Real-Time Cricket Commentary Agent. Plan Review & Comments

---

## ✅ What's Excellent

### 1. **Phase-Based Structure**
The 6-phase breakdown is solid. clear milestones. Good progression from data ingestion → routing → response generation → visualization.

### 2. **Modular Architecture**
Separating concerns into `agents/`, `models/`, `utils/`, `data/` is clean. Each agent has one job. Easy to test and iterate.

### 3. **Realistic Fallback Strategy**
Cricket API → Mock JSON is pragmatic. You won't get blocked by API downtime during match day.

### 4. **Dual-Thread Racing Design**
Thread A (factual) vs Thread B (narrative) with 2-second timeout mirrors the tennis system perfectly. Judge picking the winner is elegant.

### 5. **Probability Model Thinking**
Decay + boost factors show you understand how probabilities shift in Test cricket (time helps batsmen, wickets hurt).

---

## 🚩 Critical Issues to Address

### **Issue 1: OpenAI API Cost During Live Match**
**Problem**: Calling OpenAI for every user query + every event update will drain credits fast.
- Day 5 could have 50+ overs = 300+ balls minimum.
- If you query every 5 minutes, that's ~12 queries.
- Each call to gpt-3.5-turbo or gpt-4o-mini costs $0.001-0.005.
- Add 10-20 manual user queries throughout the day = real money.

**Recommendation**:
. Use OpenAI **only for narrative generation** (Thread B). Thread A stays pure logic (no LLM).
. **Cache responses**: Store generated narratives for identical match states. Reuse if state hasn't changed significantly.
. **Batch user queries**: Process user questions in groups every 10 minutes instead of real-time per-query.
. **Consider free alternative**: Use Hugging Face's `transformers` (DistilBERT) for local narrative generation (slower but zero cost).

---

### **Issue 2: Cricket API Reality Check**
**Problem**: Free cricket APIs are fragile. Cricscore and Cricket Data API often have:
. Rate limits (10-20 req/min).
. Lag (data 2-5 minutes behind actual play).
. Inconsistent schema (ball-by-ball format changes between formats).
. Unreliable uptime during high-traffic matches.

**Better Approach**:
. **Cricbuzz Unofficial API**: `https://www.cricbuzz.com/api/cricket/match/` + match_id. Very reliable. Check match_id from the URL you shared (117380).
. **ESPN Cricinfo Scraper**: Use BeautifulSoup + requests to scrape live commentary. Parse HTML for runs/wickets. (Slower but most reliable).
. **Manual Input Pipeline**: For Day 5, you (the user) copy-paste ball-by-ball updates from Cricbuzz. This is actually **better for learning**. You see exactly what data flows through agents.

**Recommendation**: Start with **manual JSON feed** (you type/paste events). Graduate to Cricbuzz API scraper later.

---

### **Issue 3: State Management Concurrency**
**Problem**: The plan mentions "thread-safe updates using locks or async patterns" but doesn't detail:
. How do you handle simultaneous event updates + user queries?
. What happens if a judge agent is evaluating while new events arrive?
. Lock contention could introduce latency (bad for "real-time" system).

**Better Approach**:
. Use **async/await** (Python's `asyncio`) instead of threads + locks.
. Event loop processes events sequentially (simple). User queries run concurrently.
. Queue-based architecture: Events enqueue to priority queue. Agents process FIFO. User queries get priority boost.

**Code pattern**:
```python
async def main():
    event_queue = asyncio.Queue()
    
    # Spawn event ingestion task
    asyncio.create_task(poll_cricket_api(event_queue))
    
    # Main loop processes events + queries
    while True:
        event = await event_queue.get()
        await process_event(event)
        
        # Check for user queries (non-blocking)
        if user_query_available():
            response = await route_query(user_query, state)
```

---

### **Issue 4: Judge Agent Criteria Too Vague**
**Problem**: "Evaluates outputs for accuracy and relevance" is unclear. How does judge actually decide?

**Better Spec**:
. **For stats queries**: Judge picks Thread A (factual) always. Narrative is noise here.
. **For momentum queries**: Judge picks Thread B (narrative) always. Pure facts are boring.
. **For probability queries**: Judge picks whichever includes actual P(draw) number. Reject if missing.
. **For tactical queries**: Judge picks response containing specific player names + ball context.

Add a **confidence score**:
```python
def judge_response(thread_a, thread_b, query_type):
    if query_type == "stats":
        return thread_a, confidence=0.95
    elif query_type == "momentum":
        return thread_b, confidence=0.85
    else:
        # Check which has more specificity
        return winner, confidence=0.70
```

---

### **Issue 5: Probability Model Too Simple**
**Problem**: The plan says "decay/boost factors" but doesn't define:
. How much does each wicket reduce P(draw)?
. How much does time passing increase P(draw)?
. When do you apply event booster vs time decay?

**Better Model** (Test cricket realistic):
```python
def update_probability(old_p_draw, event, overs_played, overs_remaining):
    # Time decay: More overs played = safer for batsmen
    time_factor = overs_remaining / 90  # If 90 overs in day
    
    # Event booster
    if event['type'] == 'wicket' and overs_remaining > 50:
        wicket_impact = 0.05  # Lose 5% on wicket if lots of time left
    else:
        wicket_impact = 0.02  # Lose 2% late in day
    
    # Combine
    new_p_draw = (old_p_draw * (1 - wicket_impact)) * time_factor
    return min(new_p_draw, 0.95)  # Cap at 95%
```

But you're not modeling this in detail. Recommend:
. Keep it simple for MVP (linear decay + fixed boost).
. Test against real Day 5 outcomes (did model predict correctly?).
. Refine after match ends.

---

### **Issue 6: No Error Handling Strategy**
**Problem**: Plan doesn't mention:
. What if API returns malformed JSON?
. What if OpenAI times out mid-match?
. What if user query is nonsensical ("abracadabra")?

**Add to spec**:
```python
# In router.py
try:
    category = classify_query(user_query)
except ValueError:
    return "I didn't understand that. Try: 'What are India's chances?', 'Who scored?', 'What happened?'"

# In facts_agent.py
try:
    thread_results = await asyncio.wait_for(race_threads(...), timeout=2.0)
except asyncio.TimeoutError:
    return "Thinking took too long. Here's what I know: " + fallback_response
except OpenAIError:
    return "Live updates paused. Last known: " + stale_data
```

---

### **Issue 7: Visualization Timing**
**Problem**: Plan says "plot P(draw) over time" but doesn't specify:
. When do you update the graph? Every event? Every 5 min?
. Is it saved as image or live dashboard?
. Can you view it from US while match runs in India?

**Recommendation**:
. Update plot every 10 overs (avoid noise).
. Save PNG to disk. Optional: Use `Flask` + `websocket` for live web dashboard.
. For MVP: Just print text updates + save static PNG. Visual enough.

---

## 🎯 Implementation Priority (Revised)

### **Must Build First** (Day 1-2, before match)
1. `models/state.py` - Match state schema
2. Manual event input pipeline (read JSON, no API yet)
3. `agents/router.py` - Query classification (keyword-based, no LLM)
4. `agents/stats_agent.py` - Fetch current score from state
5. `models/win_probability.py` - Simple probability calc
6. `main.py` - Wire everything together + basic CLI

**Why**: Teaches core agent concept. No external API dependency. Works offline. Ready for Day 5.

### **Build If Time** (Day 2-3, optional before match)
7. `agents/facts_agent.py` - Thread racing (without OpenAI, just mock narratives)
8. `agents/judge.py` - Pick winner between threads
9. Visualization - Plot P(draw) curve

### **Build After Match** (Post-Day-5, refinement)
10. OpenAI integration - Add real narrative generation
11. Live API scraper - Cricbuzz or ESPN Cricinfo parser
12. Advanced probability model - Calibrate against actual outcomes

---

## 📋 Specific File Recommendations

### **models/state.py** - Be More Specific
```python
from pydantic import BaseModel
from typing import List
from datetime import datetime

class Batter(BaseModel):
    name: str
    runs: int
    balls_faced: int
    is_on_strike: bool

class Event(BaseModel):
    timestamp: datetime
    event_type: str  # "wicket", "runs", "maiden", "boundary"
    runs_scored: int = 0
    batter: str = None
    bowler: str = None
    overs_played: float
    
class MatchState(BaseModel):
    match_id: str
    team_batting: str  # "India" or "SA"
    total_runs: int
    wickets_lost: int
    overs_played: float
    target: int
    current_batter: Batter
    recent_events: List[Event]
    p_draw: float  # Probability of draw
    p_sa_win: float
    last_updated: datetime
```

### **agents/router.py** - Keep It Simple Initially
```python
def route_query(query: str) -> str:
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["score", "runs", "wickets", "overs"]):
        return "stats"
    elif any(word in query_lower for word in ["momentum", "happening", "situation"]):
        return "momentum"
    elif any(word in query_lower for word in ["chance", "draw", "win", "probability", "odds"]):
        return "probability"
    elif any(word in query_lower for word in ["why", "how", "dismissed"]):
        return "tactical"
    else:
        return "stats"  # Default
```

No LLM needed. Pure regex/keyword matching. Add LLM classification later if needed.

---

## ⏰ Realistic Timeline for Day 5

**Nov 25 (Today)**, Evening (8 hours before match):
. Finish `models/state.py` and `agents/router.py`.
. Have mock events JSON ready.

**Nov 26 (Tomorrow)**, Morning (3 hours before match starts):
. Wire up `main.py`. Test with mock data.
. Ensure you can manually feed events + query system.

**Nov 26, 9 PM** (Day 5 starts):
. Open Cricbuzz in one tab. Python CLI in another.
. Paste ball-by-ball updates as events (copypaste JSON).
. Query system as match unfolds.
. Watch agents classify queries, fetch stats, update probabilities.

---

## 🚨 One More Thing: Scope Creep Warning

**Don't build all of this before Day 5.** The plan is comprehensive but you only have ~24 hours.

**MVP for Day 5**:
✅ Read live events (manual JSON).  
✅ Route user queries.  
✅ Fetch scorecard stats.  
✅ Update P(draw) with simple model.  
✅ Print responses to console.

**Nice-to-have but skip for now**:
❌ OpenAI narrative generation.  
❌ Thread racing + judge agent.  
❌ Fancy visualization.  
❌ Live API integration.  

You can add these after Day 5 when you understand the data flow better.

---

## Summary: Plan Grade

**Strengths**: A+ on architecture. Modular, well-organized, realistic phases.  
**Weaknesses**: Underestimates API fragility, vague on Judge criteria, OpenAI cost not addressed.  
**Recommendation**: Build MVP first (routing + stats + basic probability). Test with manual events during Day 5. Then extend post-match.

Ready to start coding?