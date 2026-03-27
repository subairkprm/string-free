-- String Free: Supabase Database Schema
-- Run this in Supabase SQL Editor to initialize all tables.

-- Enums
create type task_status as enum (
  'draft', 'pending_approval', 'approved', 'inprogress',
  'blocked', 'review', 'completed', 'archived'
);

create type severity as enum ('low', 'medium', 'high', 'critical');

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
