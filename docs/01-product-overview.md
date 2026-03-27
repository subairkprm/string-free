# String Free - Product Overview

## 1. Product Name and Mission

**Name:** String Free

**Mission:** Help individual builders and small teams ship serious software with fewer errors and less chaos by turning unstructured input (messages, ideas, crashes) into governed tasks, approvals, and improvement work, controlled primarily through Telegram and backed by an auditable backend.

## 2. Target Users and Problems

**Primary Users (Phase 1-2)**
- Solo developers and founders building SaaS, internal tools, or automation.
- Small teams (1-5 people) who manage work via chat, ad-hoc notes, and manual bug fixing.

**Key Problems**
- Ideas and instructions lost across Telegram/WhatsApp/voice notes.
- Errors repeat because there is no structured error-to-learning loop.
- Governance (approvals, release discipline) is either absent or too heavy.
- Existing tools (Jira, big dashboards) feel too complex for tiny teams.

## 3. Value Proposition

String Free provides:
- A Telegram-first command center for creating and approving tasks.
- An AI-assisted brain that converts free text into structured tasks and error traces into human-readable summaries with proposed fixes.
- A lightweight governance layer with structural vs non-structural task classification.
- An error learning loop that classifies, links, and reviews errors periodically.

## 4. Product Scope (Phase 1)

**In scope:**
- Single-user or single small team use.
- Telegram bot as the main interface.
- FastAPI backend with task/approval engine, error intake from Sentry, and AI services.
- Supabase as the primary database.

**Out of scope (Phase 1):**
- Full multi-tenant SaaS billing.
- Complex frontend web app.
- Deep enterprise integrations and SSO.

## 5. Key User Stories (Phase 1)

1. As a solo builder, I can send a message to a Telegram bot and get back a clean, structured task stored in the backend.
2. As the same builder, I can mark a task as structural and require explicit approval before deployment.
3. When my backend crashes, the system catches the error, summarizes it, proposes a fix, and notifies me in Telegram.
4. I can ask the bot for a daily or weekly summary of open tasks, recent errors, and improvement work.

## 6. Future Scope (Phase 2+)

- Workspaces/tenants for team isolation.
- Simple pricing plans and usage limits.
- Optional web dashboard or Telegram Mini App with modern UI.
- Additional integrations (GitHub, Jira, email, etc.).
