# Schema Review & Assessment: Screen 5 (Flavor & Quantity Selection)

**Date**: Sept 11, 2026  
**Author**: Sudhira  
**Review Target**: `app/db/schema.sql` (MogulMinds v2 session-stateful schema)  
**PRD Reference**: `Agents/MogulMinds_Screen_by_Screen_PRD-2.xlsx` (Screen 5 Row 11), `Agents/MOGUL-Project-Plan.pdf`  
**Jira Reference**: Foundation Sprint — MOGUL-2/3 Schema Review (Prep for MOGUL-12/13/14)  

---

## 1. Executive Summary

This document reviews the as-built database schema (`app/db/schema.sql`, verified live in Supabase in commit `88619be`) against the functional, architectural, and data requirements of **Screen 5 (Flavor & Quantity Selection)**.

Screen 5 is the primary inventory-sizing and demand-estimation stage in the MiniMogul lollipop stand simulation. Players select their flavor lineup and batch quantity before encountering sourcing costs (Screen 6) and location traffic conditions (Screen 7).

### Key Conclusions:
1. **Core Schema Viability**: The `decision_log` table is well-suited to capture Screen 5's composite selections (`selected_flavors`, `batch_quantity`, `nudge_fired_id`).
2. **Missing `level` in `kid_session`**: The PRD mandates that age maps to a `level` once at onboarding and all subsequent screens filter by `level`. `kid_session` currently lacks a dedicated `level` integer column.
3. **`age_tier` Constraint Gap**: `kid_session.age` allows `7` to `14`, but `age_tier` check only lists `'7-8', '9-10', '11-12'`, failing for ages `13` and `14`.
4. **Data Science Dependencies**: Screen 5 requires 3 reference tables from Data Science. While full endpoint build is blocked pending DS delivery (scheduled for Sept 20 under MOGUL-12/13/14), this document specifies the exact target schemas and a decoupled mock fallback provider.

---

## 2. Detailed Table-by-Table Schema Review

### 2.1. `kid_session` Table

```sql
create table if not exists kid_session (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references households(id) on delete cascade,
  name text,
  age int check (age between 7 and 14),
  age_tier text check (age_tier in ('7-8', '9-10', '11-12')),
  avatar_config jsonb,
  created_at timestamptz not null default now()
);
```

#### Observations & Issues:
- **Missing `level` Column**: Per the Frontend & Backend PRD notes, age resolves to `level` (1, 2, or 3) during Screen 3 (Profile/Onboarding) via the confirmed `age_level_mapping` table. This value is intended to be stored directly on `kid_session.level` so that Screen 5 (and all subsequent decision screens) query options by `level = :kid_session.level` without recalculating.
- **Age Tier Check Constraint Omission**: The check constraint `check (age_tier in ('7-8', '9-10', '11-12'))` rejects ages 13 and 14, even though `age between 7 and 14` is permitted.

#### Recommendation:
Add `level` column and update `age_tier` check constraint via migration:
```sql
alter table kid_session 
  add column if not exists level int not null default 1 check (level between 1 and 3);

alter table kid_session 
  drop constraint if exists kid_session_age_tier_check,
  add constraint kid_session_age_tier_check 
  check (age_tier is null or age_tier in ('7-8', '9-10', '11-12', '13-14'));
```

---

### 2.2. `decision_log` Table

```sql
create table if not exists decision_log (
  id uuid primary key default gen_random_uuid(),
  kid_session_id uuid not null references kid_session(id) on delete cascade,
  screen_id text not null,
  decision_key text not null,
  decision_value jsonb not null,
  created_at timestamptz not null default now()
);
```

#### Observations & Evaluation:
- **Append-Only Event Model**: The `decision_log` design allows players to adjust choices (e.g. going back from Screen 6 to Screen 5). Reading the latest decision is performed with `WHERE kid_session_id = :id AND screen_id = 'screen_5' ORDER BY created_at DESC LIMIT 1`.
- **Screen 5 Payload Structure**: The `decision_value` JSONB payload for Screen 5 must be structured consistently:
  ```json
  {
    "selected_flavors": ["flavor_cherry", "flavor_blue_raspberry"],
    "flavor_count": 2,
    "batch_quantity": 50,
    "nudge_fired_id": "nudge_high_qty_level1"
  }
  ```
- **Indexing**: Current index `idx_decision_log_kid` covers `kid_session_id`. A composite index on `(kid_session_id, screen_id, created_at desc)` is recommended for optimal read performance when resuming screens.

#### Recommendation:
```sql
create index if not exists idx_decision_log_kid_screen 
  on decision_log(kid_session_id, screen_id, created_at desc);
```

---

### 2.3. `wallet_ledger` Table

```sql
create table if not exists wallet_ledger (
  id uuid primary key default gen_random_uuid(),
  kid_session_id uuid not null references kid_session(id) on delete cascade,
  amount_cents int not null,
  reason text not null,
  screen_id text,
  created_at timestamptz not null default now()
);
```

#### Observations:
- **Screen 5 Non-Deduction Verification**: Confirmed with the PRD mechanics: Screen 5 is **read-only** with respect to the wallet. The wallet balance (`SUM(amount_cents)`) is retrieved and displayed alongside the avatar, but no transaction is written to `wallet_ledger` until Screen 6 (Prep Level - Buy vs Make).

---

## 3. Data Science (DS) Pending Tables Specification

Data Science is delivering 3 tables/datasets for Screen 5 and its downstream dependencies. The proposed database schemas for these tables in Supabase are defined below:

### 3.1. `ref_screen5_options` (Flavor & Quantity Catalog by Level)
Stores the available flavor choices and batch quantity steps for each gameplay level.

```sql
create table if not exists ref_screen5_options (
  id uuid primary key default gen_random_uuid(),
  level int not null check (level between 1 and 3),
  option_type text not null check (option_type in ('flavor', 'quantity')),
  option_code text not null,
  display_label text not null,
  description text,
  color_hex text,
  icon_url text,
  batch_units int,              -- populated for option_type = 'quantity'
  is_recommended boolean not null default false,
  is_unlocked boolean not null default true,
  sort_order int not null default 0,
  created_at timestamptz not null default now(),
  unique(level, option_type, option_code)
);

create index if not exists idx_ref_screen5_options_level 
  on ref_screen5_options(level, option_type);
```

### 3.2. `ref_flavor_costs` (Screen 6 Cost Calculation Reference)
Defines ingredient sourcing costs per flavor unit, referenced downstream by Screen 6 Prep Level calculations.

```sql
create table if not exists ref_flavor_costs (
  flavor_code text primary key,
  cost_per_unit_cents int not null check (cost_per_unit_cents >= 0),
  is_premium boolean not null default false,
  updated_at timestamptz not null default now()
);
```

### 3.3. `ref_screen5_nudges` (AI Nudge Rule Bank)
Stores heuristic trigger thresholds and copy bank for AI contextual hints.

```sql
create table if not exists ref_screen5_nudges (
  id text primary key,
  level int not null check (level between 1 and 3),
  trigger_condition text not null check (trigger_condition in ('high_quantity', 'low_flavor_variety', 'high_flavor_low_qty')),
  threshold_min_qty int,
  threshold_max_qty int,
  threshold_flavor_count int,
  copy_text text not null,
  audio_url text,
  created_at timestamptz not null default now()
);
```

---

## 4. Fallback Architecture for MOGUL-12/13/14

If Data Science's 3 tables are not fully verified in Supabase by Sept 20:
- The backend will use `MockFlavorQuantityProvider` (`app/schemas/screen_5.py`), returning deterministic, level-aware options matching the exact API contract.
- Once DS migrations are executed in Supabase, the repository layer swaps from `MockFlavorQuantityProvider` to `SupabaseFlavorQuantityProvider` without altering any Pydantic schemas, routes, or frontend contracts.

---

## 5. Review Checklist & Approvals

| Item | Status | Action Required |
| :--- | :---: | :--- |
| `kid_session` level mapping | Flagged | Add `level` int column and update `age_tier` constraint |
| `decision_log` suitability | Approved | Add composite index `(kid_session_id, screen_id, created_at desc)` |
| `wallet_ledger` non-deduction | Verified | Ensure Screen 5 endpoint does not write ledger rows |
| AI Nudge logging | Approved | Persist `nudge_fired_id` within `decision_value` JSONB |
| DS Table Contract | Documented | Ready for Supabase migration execution by DS team |
