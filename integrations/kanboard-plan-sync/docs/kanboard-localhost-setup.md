# Kanboard Local Host — Setup Methodology

> Methodology only. This bundle does **not** ship Kanboard itself, its database,
> logs, API token, or the ThemeRevision/UI plugin. You provide a local Kanboard;
> `kanboard-plan-sync` only projects Markdown plans onto it via JSON-RPC.

## Goal
Stand up a local, single-user Kanboard that `kanboard-plan-sync` can reach at
`http://127.0.0.1:8080/jsonrpc.php`, with **no Docker Desktop** — just PHP's
built-in server + SQLite.

## Prerequisites
- PHP 8.x CLI (`php -v`)
- `sqlite3` CLI (for read-only token/inspection)
- A Kanboard checkout placed at a host-local path. Recommended:
  `~/.ai/infra/kanboard-local` with `app/` as the document root.

> Paths in this bundle's examples use `~/.ai/infra/...` and a pyenv Python
> absolute path. On another host/user, substitute your own paths.

## Run / stop
Use thin wrapper scripts in the runtime dir (not shipped here):

```sh
# foreground (Ctrl-C to stop)
php -S 127.0.0.1:8080 -t <kanboard>/app

# or detached helpers if present
./serve.sh        # foreground
./start.sh        # detached
./stop.sh         # stop detached
```

## Health check
```sh
curl -s http://127.0.0.1:8080/healthcheck.php
# expect: {"status":200,"message":"Database connection is OK"}
```

## Login & API access
- Default login on a fresh DB: **admin / admin** (change the password after first login).
- JSON-RPC endpoint: `http://127.0.0.1:8080/jsonrpc.php`.
- Auth: the application API token + username `jsonrpc`.
  - The token lives in the Kanboard `settings` table (`option = 'api_token'`).
  - `kanboard-plan-sync` resolves it automatically: env `KANBOARD_API_TOKEN`
    first, else read-only from the local Kanboard SQLite DB (`local_db_path`).
  - You can also copy it from **Settings → API** in the UI.
- The token is **never** stored in this bundle, plan files, or workspace config.

## Reset (clean slate)
Stop the server, back up and remove the SQLite DB, restart — Kanboard
re-initializes a fresh DB (admin/admin, new token):

```sh
./stop.sh
cp <kanboard>/data/db.sqlite <kanboard>/data/db.sqlite.bak-<ts>
rm <kanboard>/data/db.sqlite
./start.sh && curl -s http://127.0.0.1:8080/healthcheck.php
```

## Board visibility for single-user use
`kanboard-plan-sync` keeps a 1-user board usable with zero manual steps:
- `kanboard.board_members` (default `[admin]`) → auto-added as project members.
- `kanboard.board_assignee` (default = first member, `admin`) → every card assigned,
  so the default `assignee:me` filter never hides them.
- Sync ensures the 5 status columns (`TODO/진행중/검토 필요/보류/완료`); empty default
  Kanboard columns can be removed in the board's column settings for a cleaner view.

## Out of scope (not bundled)
- Kanboard application source, `data/` (DB/cache/files), logs, API token.
- ThemeRevision / any UI theme or custom plugin/hook.
