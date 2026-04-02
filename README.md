# String Free

**AI-Assisted Build Control Platform**

Telegram-first task, approval, and error learning engine powered by FastAPI + Supabase + Gemini.

## What is this?

String Free helps individual builders and small teams ship software with fewer errors and less chaos. Send a message to Telegram, get back a structured task. When your backend crashes, get an AI-generated summary and proposed fix delivered to your chat. Get AI-powered income opportunity insights based on your work patterns.

## Tech Stack

- **Backend:** FastAPI (Python 3.11+)
- **Database:** Supabase (Postgres + Auth + RLS)
- **AI:** Google Gemini API (Phase 1), optional local LLM (Phase 2)
- **Messaging:** Telegram Bot API + future Mini App
- **Error Tracking:** Sentry
- **Billing:** Lemon Squeezy (subscription management)

## Project Structure

```
app/
  core/           # config, database, auth, billing
  models/         # enums, Pydantic schemas
  services/       # task_orchestrator, ai_service, error_analyzer, telegram_service, opportunity_analyzer
  api/routes/     # health, tasks, telegram, webhooks, opportunities
  main.py
database/
  schema.sql      # Supabase schema (run in SQL Editor)
docs/
  01-product-overview.md
  02-architecture.md
tests/
  test_health.py
  test_tasks.py
  test_webhooks.py
  test_ai_service.py
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

## API Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health/` | System health check |

### Tasks
| Method | Path | Description |
|--------|------|-------------|
| GET | `/tasks/` | List tasks (query: `status`, `limit`, `offset`, `user_id`) |
| POST | `/tasks/` | Create a new task |
| GET | `/tasks/{task_id}` | Get a single task |
| PATCH | `/tasks/{task_id}` | Update task fields |
| DELETE | `/tasks/{task_id}` | Soft-delete (archive) a task |

### Telegram
| Method | Path | Description |
|--------|------|-------------|
| POST | `/telegram/webhook` | Receive Telegram bot updates |

### Webhooks
| Method | Path | Description |
|--------|------|-------------|
| POST | `/webhooks/sentry` | Receive Sentry error alerts |
| POST | `/webhooks/billing` | Receive Lemon Squeezy billing events |

### Income Opportunities
| Method | Path | Description |
|--------|------|-------------|
| GET | `/opportunities/` | List income opportunities (query: `user_id`, `status`, `type`, `limit`, `offset`) |
| GET | `/opportunities/{opportunity_id}` | Get a single opportunity |
| POST | `/opportunities/analyze` | Trigger AI analysis of recent tasks (body: `user_id`, `days`, `force_refresh`) |
| PATCH | `/opportunities/{opportunity_id}` | Update opportunity status or notes |
| POST | `/opportunities/{opportunity_id}/rate` | Rate an opportunity (1-5 stars) |
| DELETE | `/opportunities/{opportunity_id}` | Dismiss an opportunity |

## Telegram Bot Setup

1. Create a bot via [@BotFather](https://t.me/BotFather) and get the token
2. Set `TELEGRAM_BOT_TOKEN` in your `.env`
3. Set `TELEGRAM_CHAT_ID` to your chat/group ID
4. Set the webhook URL with:
   ```bash
   curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.com/telegram/webhook"}'
   ```

### Bot Commands
- `/start` — Welcome message and quick guide
- `/task <message>` — AI parses your message into a structured task
- `/list` — Show your active tasks with status
- `/done <id>` — Mark a task as complete
- `/opportunities` — List income opportunities identified from your work
- `/opportunity <id>` — Get details on a specific opportunity
- `/pursue <id>` — Mark an opportunity as actively pursuing
- `/help` — Command reference

## Sentry Webhook Configuration

1. In your Sentry project, go to **Settings > Integrations > Webhooks**
2. Add a new webhook with URL: `https://your-domain.com/webhooks/sentry`
3. Select the alert types you want to forward (recommended: all issue alerts)
4. Set `SENTRY_DSN` in `.env` to enable client-side error tracking

When Sentry fires an alert, String Free will:
- Extract the error details
- Use Gemini AI to summarize the error and propose a fix
- Create an improvement task in Supabase
- Send a Telegram notification with the summary

## Lemon Squeezy Billing Setup

1. Create products/variants in your [Lemon Squeezy](https://www.lemonsqueezy.com/) store for each plan tier (Solo, Pro, Team)
2. Set the variant IDs in `.env`:
   - `LEMON_SQUEEZY_SOLO_VARIANT_ID`
   - `LEMON_SQUEEZY_PRO_VARIANT_ID`
   - `LEMON_SQUEEZY_TEAM_VARIANT_ID`
3. Set `LEMON_SQUEEZY_WEBHOOK_SECRET` from your Lemon Squeezy webhook settings
4. Add webhook URL: `https://your-domain.com/webhooks/billing`
5. Subscribe to events: `subscription_created`, `subscription_updated`, `subscription_cancelled`

### Plan Tiers
| Tier | Tasks/month | Error Analyses/month | Opportunity Analyses/month | Team Members |
|------|-------------|----------------------|----------------------------|--------------|
| Free | 10 | 5 | 0 | 1 |
| Solo | Unlimited | 50 | 5 | 1 |
| Pro | Unlimited | Unlimited | Unlimited | 1 |
| Team | Unlimited | Unlimited | Unlimited | 5 |

## Key Flows

1. **Task Creation:** Telegram message -> AI parses -> Task stored in Supabase -> Telegram confirmation
2. **Approval:** Structural tasks require explicit approve/reject via Telegram buttons
3. **Error Learning:** Sentry webhook -> AI summarizes crash + proposes fix -> Improvement task created -> Telegram alert
4. **Billing:** Lemon Squeezy webhook -> Plan tier updated -> Feature limits enforced
5. **Income Opportunities:** Tasks analyzed -> AI identifies patterns -> Opportunities suggested -> User can pursue or dismiss

## Running Tests

```bash
pytest tests/ -v
```

## Deployment (Cloud Run)

String Free deploys to Google Cloud Run (me-central1, Doha) via GitHub Actions.

### Prerequisites

1. **GCP Project** with Cloud Run API and Artifact Registry enabled
2. **Service Account** with roles: `roles/run.admin`, `roles/iam.serviceAccountUser`
3. **GitHub Secrets** configured in your repo settings:
   - `GCP_SA_KEY` — Service account JSON key

### Environment Variables on Cloud Run

Set these in the Cloud Run console or via `gcloud`:

```bash
gcloud run services update string-free \
  --region me-central1 \
  --set-env-vars "SUPABASE_URL=<your-url>,SUPABASE_KEY=<your-key>,GEMINI_API_KEY=<your-key>,TELEGRAM_BOT_TOKEN=<your-token>,TELEGRAM_CHAT_ID=<your-chat-id>,LEMON_SQUEEZY_WEBHOOK_SECRET=<your-secret>,SENTRY_DSN=<optional>"
```

### Manual Deploy

Push to `main` triggers automatic deployment. For manual:

```bash
# Via GitHub Actions
gh workflow run deploy.yml

# Via gcloud CLI
gcloud run deploy string-free \
  --source . \
  --region me-central1 \
  --allow-unauthenticated
```

### Landing Page

The `landing/` directory contains the marketing site. Deploy it separately to any static host (Vercel, Netlify, Cloudflare Pages) or serve from a CDN.

## Roadmap

- [x] Phase 1: Backend skeleton + health endpoint
- [x] Phase 1: Task CRUD engine
- [x] Phase 1: AI service (Gemini text-to-task + error analysis)
- [x] Phase 1: Telegram bot integration
- [x] Phase 1: Sentry error learning loop
- [x] Phase 1: Lemon Squeezy billing integration
- [x] Landing page
- [x] CI/CD pipeline (GitHub Actions)
- [x] Cloud Run deployment config
- [x] Phase 2.5: Income opportunity analysis (AI-powered monetization insights)
- [ ] Phase 2: Multi-tenant SaaS foundation
- [ ] Phase 3: Web dashboard / Telegram Mini App with opportunity visualization
- [ ] Phase 3: Advanced opportunity tracking and trend analysis

## License

MIT
