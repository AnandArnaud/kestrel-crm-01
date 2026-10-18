# Kestrel CRM

Kestrel CRM, a small contacts CRM with a nightly digest task. Django serves a contact list page and a JSON
API; a Celery task runs every night at 02:00 UTC and logs how many contacts were added in the last day.

## Run locally

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_contacts
python manage.py runserver 0.0.0.0:${PORT:-8000}
```

Production web process: `gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}`.

The worker and the scheduler need Redis reachable at `REDIS_URL`:

```sh
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
```

## Routes

| Path             | Description                                            |
| ---------------- | ------------------------------------------------------ |
| `/`              | contact list page                                      |
| `/api/contacts/` | JSON list of contacts                                  |
| `/health/`       | `{"ok": true}`                                         |
| `/admin/`        | Django admin (`python manage.py createsuperuser` first) |

## Environment

| Variable        | Default                           | Purpose                                     |
| --------------- | --------------------------------- | ------------------------------------------- |
| `DATABASE_URL`  | SQLite file `kestrel.sqlite3`     | Postgres URL in production                  |
| `REDIS_URL`     | `redis://127.0.0.1:6379/0`        | Celery broker                               |
| `SECRET_KEY`    | a development-only value          | set a long random value in production       |
| `DEBUG`         | `1`                               | set `0` in production                       |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1`             | comma-separated hostnames the site answers for |
| `PORT`          | `8000`                            | port the web process listens on             |

`python manage.py migrate` must run before a new version takes traffic. The worker exits at startup when the
broker is unreachable rather than retrying forever, so a missing Redis shows up immediately in its log.

## Deployment

`render.yaml` is a [Render Blueprint](https://render.com/docs/blueprint-spec) that provisions everything: a web
service (gunicorn), a Celery worker, a Celery beat scheduler, a managed Postgres database, and a managed Redis
("Key Value") broker. Launch it with `render blueprint launch`, or connect the repo in the Render dashboard.
`DATABASE_URL`, `REDIS_URL`, and a generated `SECRET_KEY` are wired in automatically; `DEBUG` is `0`. Set any
real `ALLOWED_HOSTS` yourself — the service's own `*.onrender.com` hostname is trusted automatically.

### Migrations run before the new release takes traffic — with no downtime

Each deploy goes through three phases:

1. **Build** — install dependencies and `collectstatic`, producing the new image. The running version is
   untouched.
2. **Pre-deploy** — `python manage.py migrate --noinput` runs *once* against the live database (the web
   service's `preDeployCommand`). The old version is still serving traffic at this point. If `migrate` fails,
   the deploy aborts and the old version keeps running.
3. **Deploy** — the new instance boots and must pass the `/health/` check before Render routes traffic to it;
   the old instance is drained and retired only afterwards. That health-gated handover is what makes the
   release zero-downtime.

So migrations are always applied *before* the new code serves a request, and the old code keeps serving until
the new code is proven healthy.

### Write backward-compatible migrations

Between phases 2 and 3 the **old** code runs against the **already-migrated** schema for a short window. For
that window to be safe, each migration must be backward compatible with the currently-deployed code — the
standard expand/contract approach:

- **Adding** a column: make it nullable or give it a default (don't add a `NOT NULL` column with no default in
  the same release that starts writing to it).
- **Removing** a column/table: first ship a release that stops using it, then drop it in a *later* release.
- **Renaming**: add the new name, migrate reads/writes across two releases, then remove the old name.

Deploys that can't be made backward compatible need a maintenance window instead; that's the one case where
"no downtime" doesn't apply.

### Porting to another platform

The contract is platform-neutral — run `manage.py migrate` as a release/pre-deploy step (not inside the web
start command, which would race across instances), and gate the traffic cutover on `/health/`:

- **Heroku**: a `release:` process in the `Procfile` (`release: python manage.py migrate --noinput`) runs
  before the new release boots; dyno restarts are rolling.
- **Fly.io**: `[deploy] release_command = "python manage.py migrate --noinput"` in `fly.toml`, with a
  `rolling` or `bluegreen` strategy and an HTTP check on `/health/`.
- **Kubernetes**: a migration `Job` as a Helm `pre-upgrade` hook (or an init container), a `Deployment` with
  `RollingUpdate`, and a readiness probe on `/health/`.
