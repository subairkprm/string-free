# String Free - Architecture Overview

## 1. Architectural Style

Backend-first, service-oriented system built around:
- Stateless HTTP API (FastAPI)
- Managed relational database (Supabase Postgres)
- External providers: AI (Gemini), Error collection (Sentry), Messaging (Telegram Bot)

## 2. Components

- **FastAPI Backend** - REST endpoints and webhooks, task/approval/error logic
- **Supabase (Postgres)** - Tasks, approvals, errors, improvement tasks
- **Telegram Bot** - Primary user interface via commands and inline keyboards
- **Sentry** - Error capture and webhook delivery
- **AI Provider** - Phase 1: Gemini API; Phase 2: Optional local LLM

## 3. Key Flows

### Task Creation
User message -> Telegram webhook -> FastAPI -> AI parses text -> TaskOrchestrator -> Supabase -> Telegram confirmation

### Approval
Telegram callback -> FastAPI -> Update approvals + tasks -> Edit Telegram message

### Error Learning
App crash -> Sentry webhook -> FastAPI -> AI summarize + propose fix -> Create improvement_task -> Telegram alert

## 4. Project Structure

```
app/
  core/       - config, database, logging, security
  models/     - enums, Pydantic schemas
  services/   - task_orchestrator, ai_service, error_analyzer, telegram_service
  api/routes/ - health, tasks, errors, improvement_tasks, telegram, webhooks
  main.py
database/
  schema.sql
docs/
  01-product-overview.md
  02-architecture.md
```

## 5. Technology Stack

- Python 3.11+
- FastAPI
- Supabase (Postgres + Auth + RLS)
- google-generativeai (Phase 1 AI)
- python-telegram-bot / httpx
- sentry-sdk
- pydantic / pydantic-settings

## 6. Quality Attributes

- **Security** - Secrets from env vars, webhook auth, no AI write access to production
- **Reliability** - Sentry monitoring, error learning loop
- **Maintainability** - Layered architecture, docs-as-code
- **Extensibility** - Pluggable AI service, easy to add web/mobile clients
