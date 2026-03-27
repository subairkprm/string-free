# String Free

**AI-Assisted Build Control Platform**

Telegram-first task, approval, and error learning engine powered by FastAPI + Supabase + Gemini.

## What is this?

String Free helps individual builders and small teams ship software with fewer errors and less chaos. Send a message to Telegram, get back a structured task. When your backend crashes, get an AI-generated summary and proposed fix delivered to your chat.

## Tech Stack

- **Backend:** FastAPI (Python 3.11+)
- **Database:** Supabase (Postgres + Auth + RLS)
- **AI:** Google Gemini API (Phase 1), optional local LLM (Phase 2)
- **Messaging:** Telegram Bot API + future Mini App
- **Error Tracking:** Sentry

## Project Structure

```
app/
  core/           # config, database, logging, security
  models/         # enums, Pydantic schemas
  services/       # task_orchestrator, ai_service, error_analyzer, telegram_service
  api/routes/     # health, tasks, errors, improvement_tasks, telegram, webhooks
  main.py
database/
  schema.sql      # Supabase schema (run in SQL Editor)
docs/
  01-product-overview.md
  02-architecture.md
```

## Quick Start

```bash
# Clone
git clone https://github.com/subairkprm/string-free.git
cd string-free

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in your Supabase, Gemini, Telegram, and Sentry keys

# Run the database schema in Supabase SQL Editor
# (paste contents of database/schema.sql)

# Start the server
uvicorn app.main:app --reload
```

Open http://localhost:8000/health/ to verify.

## Key Flows

1. **Task Creation:** Telegram message -> AI parses -> Task stored in Supabase -> Telegram confirmation
2. **Approval:** Structural tasks require explicit approve/reject via Telegram buttons
3. **Error Learning:** Sentry webhook -> AI summarizes crash + proposes fix -> Improvement task created -> Telegram alert

## Roadmap

- [x] Phase 1: Backend skeleton + health endpoint
- [ ] Phase 1: Task and approval engine
- [ ] Phase 1: AI service (Gemini text-to-task)
- [ ] Phase 1: Telegram bot integration
- [ ] Phase 1: Sentry error learning loop
- [ ] Phase 2: Multi-tenant SaaS foundation
- [ ] Phase 3: Web dashboard / Telegram Mini App

## License

MIT
