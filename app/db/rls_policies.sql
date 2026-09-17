-- app/db/rls_policies.sql
-- MOGUL-4 — Row Level Security across all 5 core tables

alter table households enable row level security;
alter table kid_session enable row level security;
alter table wallet_ledger enable row level security;
alter table decision_log enable row level security;
alter table simulation_runs enable row level security;

-- households: a household can only see its own row
create policy "household_owns_self" on households
  for select using (auth.uid() = id);

-- kid_session: only accessible if it belongs to the authenticated household
create policy "household_owns_kid_session" on kid_session
  for all using (household_id = auth.uid());

-- wallet_ledger: only accessible via a kid_session that belongs to the household
create policy "household_owns_wallet_ledger" on wallet_ledger
  for all using (
    kid_session_id in (select id from kid_session where household_id = auth.uid())
  );

-- decision_log: same pattern
create policy "household_owns_decision_log" on decision_log
  for all using (
    kid_session_id in (select id from kid_session where household_id = auth.uid())
  );

-- simulation_runs: same pattern
create policy "household_owns_simulation_runs" on simulation_runs
  for all using (
    kid_session_id in (select id from kid_session where household_id = auth.uid())
  );