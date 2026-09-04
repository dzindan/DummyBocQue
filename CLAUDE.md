# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Vietnamese I Ching (Kinh Dịch) divination app — cast/interpret hexagrams
(Lục Hào, Mai Hoa methods), browse the 64 hexagram reference, save
divination history and personal notes. Flask, deployable both as a local
desktop exe (PyInstaller) and on Vercel.

## Commands

- Dev server: `python main_devserver.py`
- Vercel entrypoint: `wsgi.py` (`app = create_app()`), routed via
  `vercel.json` (`@vercel/python` builder)
- No automated test suite exists for this project.
- Pull deployment secrets: `vercel env pull .env.local` (from Vercel CLI,
  logged into the right project) — gives `SUPABASE_URL`/`SUPABASE_KEY`, see
  Architecture below. `.env*` is gitignored; never remove that line.
- Rebuild the desktop exe: `pyinstaller build.spec --noconfirm --clean`
  (produces `KinhDichApp`, always `rm -rf build dist` first)
- Regenerate bundled reference data (hexagrams/trigrams/nap_am/content
  JSON in `app/data/`): `python scripts/generate_data.py`

No linter/formatter is configured in this project.

## Architecture essentials

- **Storage is backend-swappable** (`app/storage/`): `StorageBackend` (ABC
  in `base.py`) exposes just two generic operations — a JSON value by key,
  a byte blob by path-like key — deliberately generic so a new feature
  needs zero new backend methods on either implementation. `get_backend()`
  (`storage/__init__.py`) picks `SupabaseBackend` when `SUPABASE_URL`/
  `SUPABASE_KEY` are set, else `LocalFileBackend` (desktop/local dev).
  Running on Vercel with neither var set falls back to local files under
  `/tmp` — ephemeral and NOT shared across cold starts — and logs a loud
  `RuntimeWarning` rather than silently losing data.
- **Shares its Supabase project with Tu Vi App (alias TVA)**: same
  `kv_store`/blobs tables, same project — every key this app writes is
  prefixed `"kinhdich_"` (`app/kinhdich/records.py`,
  `DIVINATIONS_KEY`/`NOTES_KEY`/`CUSTOM_QUESTIONS_KEY`) specifically so the
  two apps' data doesn't collide. Never drop that prefix, and check
  `records.py` before adding a new persisted key.
- **No login** — unlike Tarot Reader/Tu Vi App, this app has no auth layer;
  `app.secret_key` is a fresh random value per process. All 6 POST routes
  (delete history/notes, add notes) are CSRF-protected (`CSRFProtect`,
  hidden `csrf_token` field in each form) since there's no auth in front of
  them to rely on otherwise.
- `app/paths.py` distinguishes three runtime contexts: frozen desktop exe
  (`sys._MEIPASS`), Vercel (`is_vercel()`, read-only FS outside `/tmp`),
  and local dev — `get_app_data_dir()`/`get_bundle_dir()` branch on these,
  don't assume a fixed filesystem layout when touching storage paths.
- Divination logic lives under `app/kinhdich/` (one module per concern:
  `luc_hao.py`, `maihoa.py`, `the_dung.py`, `ngu_hanh.py`, `canchi.py`,
  `nap_am.py`, `lunar.py`) separate from `app/routes/` (Flask blueprints)
  and `app/storage/` (persistence) — keep new divination-method logic in
  `kinhdich/`, not in routes.
