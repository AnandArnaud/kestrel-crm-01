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
