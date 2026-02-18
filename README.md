# cricket-commentary-agents

A multi-agent system for real-time cricket match commentary. It polls a free cricket API every 30 seconds, maintains match state, and routes user queries to one of four specialized agents — stats, momentum, probability, or tactical — each backed by OpenAI with a keyword-based fallback.

No paid APIs required. OpenAI is optional; the system runs on keyword matching alone if no key is set.

## Running

```bash
pip install -r requirements.txt
```

```
# .env (optional)
OPENAI_API_KEY=your-key
```

```bash
python main.py
```

Once running, the system polls the API in the background and accepts queries in the terminal.

## Agents

| Agent | Handles |
|---|---|
| Stats | Scores, wickets, batting status |
| Momentum | Recent events, match flow |
| Probability | Win/draw/loss estimates |
| Tactical | Dismissals, field placements |

Queries are classified automatically and routed to the right agent.

## Structure

```
src/
├── core/         # state models and probability logic
├── agents/       # router + four specialized agents
├── services/     # API client, OpenAI integration
└── cli/          # main loop and orchestration
```

## License

MIT
