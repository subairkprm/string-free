# 04 - Supabase Schema Explained

String Free uses four tables in Supabase Postgres in Phase 1.
To initialise: paste `database/schema.sql` into the Supabase SQL Editor and run it.

---

## Tables at a Glance

- **tasks** - every piece of work tracked by the system
- **approvals** - approval/rejection decisions on structural tasks
- **errors** - raw crash events received from Sentry
- **improvement_tasks** - AI-generated fix tasks created from errors

> `users` and `subscriptions` are Phase 2 features. In Phase 1, `user_id` is a plain text field defaulting to `default`.

---

## tasks

The core table. Every task - from Telegram, API, or auto-created from an error - lives here.

**Columns:**

- `id` (UUID) - unique ID, auto-generated
- `title` (text) - short description of the work
- `description` (text, optional) - more detail, may include AI notes
- `status` (enum) - current stage: draft, pending_approval, approved, inprogress, review, completed, blocked, or archived
- `structural_flag` (boolean) - when `true`, requires human approval before work begins
- `priority` (text, optional) - low, medium, high, or critical
- `source` (text) - origin: telegram, api, error_auto, or manual
- `created_at` / `updated_at` (timestamptz)

**Key rule:** Tasks with `structural_flag = true` always get a matching row in `approvals`.

---

## approvals

Every structural task needs a human go-ahead. This table records that decision.

**Columns:**

- `id` (UUID)
- `task_id` (UUID) - links to `tasks`, cascades on delete
- `result` (text) - pending, approved, or rejected
- `requested_by` (text, optional) - e.g. telegram_bot
- `decided_by` (text, optional) - who made the decision
- `note` (text, optional) - free-text reason
- `created_at` / `updated_at` (timestamptz)

When a Telegram Approve button is tapped, the bot updates `result` to `approved` and writes `decided_by`.

---

## errors

Whenever Sentry fires a webhook, the raw event is stored here before AI processing - a permanent audit log.

**Columns:**

- `id` (UUID)
- `timestamp` (timestamptz) - when the error occurred
- `environment` (text) - production, staging, etc.
- `module` (text) - file/transaction where it crashed (Sentry `culprit` field)
- `category` (text) - integration, logic, validation, data, workflow, etc.
- `severity` (enum) - low, medium, high, or critical (mapped from Sentry levels)
- `summary` (text) - AI-generated plain-English description
- `raw_detail` (text) - first 5,000 chars of the raw Sentry payload
- `probable_cause` (text) - AI-suggested root cause
- `status` (text) - open or resolved
- `linked_task_id` (UUID, optional) - the `tasks` row created from this error
- `linked_improvement_task_id` (UUID, optional) - the `improvement_tasks` row

**Sentry level mapping:** fatal=critical, error=high, warning=medium, info/debug=low

---

## improvement_tasks

AI-generated fix suggestions. Every processed Sentry error auto-creates one row here.

**Columns:**

- `id` (UUID)
- `title` (text) - auto-generated as: `Fix: <AI summary>` (max 80 chars)
- `error_summary` (text) - plain-English crash description
- `proposed_fix` (text) - AI-suggested fix steps
- `priority` (text) - inherited from error severity
- `structural_flag` (boolean) - **always `true`** - always requires human review
- `status` (enum) - same as tasks, starts at draft
- `source_error_id` (UUID) - which `errors` row triggered this
- `created_at` / `updated_at` (timestamptz)

Always review every AI-proposed fix before applying it to production.

---

## Enum Values

`task_status`: draft, pending_approval, approved, inprogress, blocked, review, completed, archived

`severity`: low, medium, high, critical

---

## Row Level Security (RLS)

RLS is not configured in Phase 1 (single-user mode). For Phase 2 multi-tenant:

1. Enable RLS on all tables in the Supabase dashboard.
2. Add a proper `user_id` foreign key to `tasks` and `approvals`.
3. Write policies so each user can only query their own rows.
