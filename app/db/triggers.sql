-- app/db/triggers.sql
-- MogulMinds v2 — Database Triggers
-- Automatically sync auth.users with public.households to prevent foreign key violations on kid_session

-- 1. Trigger function: creates or updates a public.households record whenever a user is created in auth.users
create or replace function public.handle_new_user_household()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.households (id, email, auth_provider, email_verified, created_at)
  values (
    new.id,
    new.email,
    coalesce(new.raw_app_meta_data->>'provider', 'email'),
    coalesce((new.email_confirmed_at is not null), false),
    coalesce(new.created_at, now())
  )
  on conflict (id) do update set
    email = excluded.email,
    email_verified = excluded.email_verified;
  return new;
end;
$$;

-- 2. Trigger definition on auth.users
drop trigger if exists on_auth_user_created_household on auth.users;
create trigger on_auth_user_created_household
  after insert on auth.users
  for each row execute function public.handle_new_user_household();

-- 3. Idempotent backfill: populate public.households for any existing auth.users missing a row
insert into public.households (id, email, auth_provider, email_verified, created_at)
select 
  id, 
  email, 
  coalesce(raw_app_meta_data->>'provider', 'email'),
  (email_confirmed_at is not null),
  created_at
from auth.users
where id not in (select id from public.households)
on conflict (id) do nothing;
