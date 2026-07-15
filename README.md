# ai-slack-agent

Production-ready **Slack bot powered by an LLM with tool use**. Mention the bot in a channel or DM it, and it answers questions — calling real tools (a database lookup and an external API) when it needs live data, then summarising the result in natural language.

## What it demonstrates

- **LLM tool use / function calling** — the model decides when to call a tool, the app executes it, and the result is fed back for a final answer.
- **A clean tool registry** — adding a new capability is one decorator, no branching logic.
- **Real integrations** — a SQLite product database and a live weather API, both easy to swap for your own.
- **Production concerns** — timeouts and retry/backoff on network calls, structured logging, input guards, graceful error replies, tests, CI, and Docker.

## How it works

```
  Slack message
       │
       ▼
  ┌───────────┐      ┌───────────────┐     ┌────────────┐
  │  Bolt    │ →    │  Agent loop   │ ───→│  LLM        │
  │  handler │      │  (tool use)   │←───│             │
  └───────────┘      └─────┬───────┘     └───────────┘
       ▲                 │  tool_use
       │                 ▼
       │          ┌──────────────┐
       └── answer ── │  Tool        │  →  DB / weather API
                  │  registry    │
                  └──────────────┘
```

## Tech stack

- **Slack**: `slack-bolt` (Socket Mode — no public URL needed)
- **LLM**: Anthropic Claude with tool use — pluggable client
- **Data**: SQLite (demo product catalogue) + a weather HTTP API
- **Tests**: pytest
- **CI**: GitHub Actions
- **Packaging**: Docker

## Setup

### 1. Create a Slack app

1. Go to <https://api.slack.com/apps> → **Create New App** → *From scratch*.
2. Enable **Socket Mode** (Settings → Socket Mode) and generate an **App-Level Token** with `connections:write` → this is `SLACK_APP_TOKEN` (`xapp-…`).
3. Under **OAuth & Permissions**, add bot scopes: `app_mentions:read`, `chat:write`, `im:history`, `im:read`, `im:write`.
4. Under **Event Subscriptions** → *Subscribe to bot events*: `app_mention`, `message.im`.
5. Install the app to your workspace → copy the **Bot User OAuth Token** → `SLACK_BOT_TOKEN` (`xoxb-…`).

### 2. Configure and run

```bash
cp .env.example .env      # fill in the Slack + Anthropic tokens
pip install -e ".[dev]"
python -m app.main
```

Or with Docker:

```bash
docker build -t ai-slack-agent .
docker run --env-file .env ai-slack-agent
```

Now mention the bot in a channel: `@yourbot what's the weather in Pune?` or
`@yourbot how many units of SKU-100 are in stock?`

## Configuration

| Variable | Description |
|---|---|
| `SLACK_BOT_TOKEN` | Bot User OAuth token (`xoxb-…`) |
| `SLACK_APP_TOKEN` | App-level token for Socket Mode (`xapp-…`) |
| `ANTHROPIC_API_KEY` | LLM API key |
| `CHAT_MODEL` | Model id (default `claude-sonnet-5`) |
| `WEATHER_API_URL` | Weather API base URL |
| `DATABASE_PATH` | Path to the SQLite file |
| `LOG_LEVEL` | Logging level (default `INFO`) |

See [`.env.example`](.env.example).

## Adding a tool

Tools live in [`app/tools.py`](app/tools.py). Register one with the decorator:

```python
@registry.register(
    name="get_order_status",
    description="Look up the status of an order by its id.",
    schema={
        "type": "object",
        "properties": {"order_id": {"type": "string"}},
        "required": ["order_id"],
    },
)
def get_order_status(order_id: str) -> dict:
    ...
```

The agent will automatically offer it to the model.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

## License

MIT — see [LICENSE](LICENSE).
