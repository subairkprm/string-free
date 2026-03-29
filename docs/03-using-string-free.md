# 03 — Using String Free: Your First Controlled Workflow

This guide walks through the most important pattern in String Free: a **controlled workflow** where a structural task requires explicit approval before any work begins. Think of it as a safety gate for changes that matter.

---

## What Is a Structural Task?

A regular task (`structural_flag: false`) flows automatically: it is created as `draft` and you can move it forward freely.

A **structural task** (`structural_flag: true`) is flagged for human review. It is held at `pending_approval` status until someone explicitly approves or rejects it via Telegram. Use this for anything that could break your system — schema migrations, API-breaking changes, new billing logic, etc.

---

## Concrete Example: "Add a new Supabase table"

### Step 1 — You send a Telegram message

```
/task Add users table to Supabase with email, plan_tier, and created_at columns
```

String Free's Telegram service receives this and calls the AI service (Gemini) to parse it into a structured task.

### Step 2 — AI parses into a task

Gemini returns:

```json
{
  "title": "Add users table to Supabase",
  "description": "Columns: email (text, unique), plan_tier (text, default 'free'), created_at (timestamptz, default now())",
  "priority": "high",
  "tags": ["database", "schema"]
}
```

### Step 3 — Task stored in Supabase

Because the title contains a keyword that triggers the structural flag (or you manually set `structural_flag: true`), the task is saved with:

```json
{
  "id": "a1b2c3d4-...",
  "title": "Add users table to Supabase",
  "status": "pending_approval",
  "structural_flag": true,
  "priority": "high",
  "source": "telegram"
}
```

An approval record is also created:

```json
{
  "task_id": "a1b2c3d4-...",
  "result": "pending",
  "requested_by": "telegram_bot"
}
```

### Step 4 — Telegram confirmation with action buttons

You receive a message in your Telegram chat:

```
⚠️ Structural Task — Approval Required

Add users table to Supabase

Columns: email (text, unique), plan_tier (text, default 'free'), created_at...

[✅ Approve]  [❌ Reject]
```

### Step 5 — You tap Approve

The bot updates the approval record to `approved` and moves the task status to `approved`. You can then begin the actual database work, knowing there is a logged, timestamped record of who approved it.

### Step 6 — You mark it complete

Once the table is created and verified:

```
/done a1b2c3d4
```

Status moves to `completed`. The full audit trail lives in Supabase: task creation → pending_approval → approved → completed.

---

## Full Status Lifecycle

```
draft ──► pending_approval ──► approved ──► inprogress ──► review ──► completed
                          └──► rejected
                                                    └──► blocked (if something blocks progress)
                                                                 └──► archived (soft-delete)
```

- **draft** — just created, no action required yet
- **pending_approval** — structural task waiting for your go-ahead
- **approved / rejected** — human decision recorded
- **inprogress** — actively being worked on
- **blocked** — something is blocking progress (dependency, missing info)
- **review** — done, needs a check before closing
- **completed** — finished
- **archived** — soft-deleted, not shown in default list views

---

## Tip: When to Use Structural Flag

| Use `structural_flag: true` | Use `structural_flag: false` |
|-----------------------------|------------------------------|
| Database schema changes      | Writing a new function       |
| API contract changes         | Fixing a typo                |
| New billing/plan logic       | Adding a log line            |
| Deleting data or tables      | Updating README              |
| Changing auth flow           | Running local tests          |
