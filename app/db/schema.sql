-- app/db/schema.sql
-- MogulMinds v2 — session-stateful schema

create table if not exists households (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  auth_provider text not null check (auth_provider in ('email', 'google')),
  email_verified boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists kid_session (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references households(id) on delete cascade,
  name text,
  age int check (age between 7 and 14),
  age_tier text check (age_tier in ('7-8', '9-10', '11-12')),
  avatar_config jsonb,
  created_at timestamptz not null default now()
);

-- Append-only wallet transaction log — balance is SUM(amount_cents), never a single field
create table if not exists wallet_ledger (
  id uuid primary key default gen_random_uuid(),
  kid_session_id uuid not null references kid_session(id) on delete cascade,
  amount_cents int not null,  -- positive = fund, negative = deduct
  reason text not null,       -- e.g. 'initial_fund', 'ingredient_purchase', 'sign_cost'
  screen_id text,             -- which screen triggered this, for audit
  created_at timestamptz not null default now()
);

-- Per-screen decision log — one row per choice made on any screen
create table if not exists decision_log (
  id uuid primary key default gen_random_uuid(),
  kid_session_id uuid not null references kid_session(id) on delete cascade,
  screen_id text not null,
  decision_key text not null,
  decision_value jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists simulation_runs (
  id uuid primary key default gen_random_uuid(),
  kid_session_id uuid not null references kid_session(id) on delete cascade,
  status text not null default 'in_progress' check (status in ('in_progress', 'complete_profit', 'complete_loss')),
  final_profit_cents int,
  started_at timestamptz not null default now(),
  completed_at timestamptz
);

create index if not exists idx_kid_session_household on kid_session(household_id);
create index if not exists idx_wallet_ledger_kid on wallet_ledger(kid_session_id);
create index if not exists idx_decision_log_kid on decision_log(kid_session_id);
create index if not exists idx_simulation_runs_kid on simulation_runs(kid_session_id);