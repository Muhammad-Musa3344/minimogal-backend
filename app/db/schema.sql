create table if not exists accounts (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  auth_provider text not null check (auth_provider in ('email', 'google')),
  email_verified boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists child_profiles (
  id uuid primary key default gen_random_uuid(),
  account_id uuid not null references accounts(id) on delete cascade,
  name text,
  age int check (age between 7 and 14),
  default_level int not null default 1,
  avatar_config jsonb,
  wallet_balance_cents int check (wallet_balance_cents between 2500 and 10000),
  created_at timestamptz not null default now()
);

create table if not exists playthroughs (
  id uuid primary key default gen_random_uuid(),
  child_id uuid not null references child_profiles(id) on delete cascade,
  business text not null default 'lollipop_stand',
  level int not null default 1,
  seed text,
  status text not null default 'in_progress',
  started_at timestamptz not null default now(),
  completed_at timestamptz
);
create table if not exists answer_bank (
  id uuid primary key default gen_random_uuid(),
  touchpoint text not null,
  input_state_hash text not null,
  approved_text text not null,
  audio_url text,
  status text not null default 'approved' check (status in ('pending', 'approved', 'rejected')),
  created_at timestamptz not null default now(),
  unique (touchpoint, input_state_hash)
);
create table if not exists decision_log (
  id uuid primary key default gen_random_uuid(),
  playthrough_id uuid not null references playthroughs(id) on delete cascade,
  screen_id text not null,
  decision_key text not null,
  decision_value jsonb not null,
  created_at timestamptz not null default now()
);