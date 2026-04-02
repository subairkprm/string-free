-- String Free: Supabase Database Schema
-- Run this in Supabase SQL Editor to initialize all tables.

-- Enums
create type task_status as enum (
  'draft', 'pending_approval', 'approved', 'inprogress',
  'blocked', 'review', 'completed', 'archived'
);

create type severity as enum ('low', 'medium', 'high', 'critical');

create type opportunity_type as enum (
  'monetization',
  'consulting',
  'saas',
  'marketplace',
  'affiliate',
  'education'
);

create type opportunity_status as enum (
  'identified',
  'evaluating',
  'pursuing',
  'implemented',
  'dismissed'
);

-- Tasks
create table if not exists tasks (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text,
  status task_status not null default 'draft',
  structural_flag boolean not null default false,
  priority text,
  source text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Approvals
create table if not exists approvals (
  id uuid primary key default gen_random_uuid(),
  task_id uuid not null references tasks(id) on delete cascade,
  result text not null default 'pending',
  requested_by text,
  decided_by text,
  note text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Errors
create table if not exists errors (
  id uuid primary key default gen_random_uuid(),
  timestamp timestamptz not null default now(),
  environment text,
  module text,
  category text,
  severity severity,
  source_layer text,
  trigger_action text,
  summary text,
  raw_detail text,
  probable_cause text,
  status text default 'open',
  linked_task_id uuid references tasks(id),
  linked_improvement_task_id uuid,
  created_at timestamptz not null default now()
);

-- Improvement Tasks
create table if not exists improvement_tasks (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  error_summary text,
  proposed_fix text,
  priority text,
  structural_flag boolean not null default true,
  status task_status not null default 'draft',
  source_error_id uuid references errors(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Income Opportunities
create table if not exists income_opportunities (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  title text not null,
  description text not null,
  opportunity_type opportunity_type not null,
  status opportunity_status not null default 'identified',

  -- Analysis metadata
  confidence_score decimal(3,2),
  estimated_effort text,
  estimated_revenue_potential text,

  -- Source tracking
  source_task_ids uuid[],
  analysis_date timestamptz not null default now(),
  ai_reasoning text,

  -- User feedback
  user_notes text,
  user_rating int,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Index for efficient user queries
create index if not exists idx_opportunities_user_status
  on income_opportunities(user_id, status);

-- Opportunity Insights
create table if not exists opportunity_insights (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  insight_type text not null,
  insight_text text not null,
  supporting_data jsonb,
  created_at timestamptz not null default now()
);
