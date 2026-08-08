-- Run this once in the Supabase project's SQL editor before deploying
-- online. Only 2 generic tables - every current AND future piece of app
-- state (divination history, notes, custom question templates, whatever
-- gets added later) reuses these under a new key, no further migrations
-- needed. Same schema as Tu Vi App's own Supabase project.

create table if not exists kv_store (
    key text primary key,
    value jsonb not null,
    updated_at timestamptz not null default now()
);

create table if not exists blobs (
    key text primary key,
    content text not null,
    updated_at timestamptz not null default now()
);

-- Keep updated_at accurate on every write (used for display purposes -
-- e.g. sorting - not for correctness).
create or replace function set_updated_at() returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists kv_store_set_updated_at on kv_store;
create trigger kv_store_set_updated_at
    before insert or update on kv_store
    for each row execute function set_updated_at();

drop trigger if exists blobs_set_updated_at on blobs;
create trigger blobs_set_updated_at
    before insert or update on blobs
    for each row execute function set_updated_at();

-- Single-user app, accessed only via its own server-side code using the
-- Supabase service_role key (Vercel env var) - Row Level Security stays
-- disabled so the service_role key can read/write freely. Do NOT expose
-- the anon/public key to any client-side code with these tables
-- world-writable; the app only ever uses the service_role key
-- server-side, never from the browser.
