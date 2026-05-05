# Sadaqah & Zakat Transparency Hub

A local-first Flask application for logging donations, browsing transparency-focused charity profiles, setting zakat goals, exporting PDF receipts, and exposing a small JSON API.

## Features

- Donation logger stored in local SQLite
- 20 pre-seeded charities on first run
- Dashboard with totals, trend chart, and goal progress
- Local reviews and transparency ratings for charities
- Zakat goal calculator and monthly sadaqah targets
- PDF receipt export with QR links to charity profiles
- Public JSON API with optional community-write passphrase
- Optional startup sync from a community `charities.json`
- Telegram reminder helper service for Hermes cron jobs

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.yaml.example config.yaml
python scripts/init_db.py
python app.py
```

Open http://127.0.0.1:5000

## Running tests

```bash
pytest --cov=. --cov-report=term-missing
```

## API

- `GET /api/charities`
- `GET /api/charities/<id>`
- `GET /api/charities/<id>/reports`
- `POST /api/charities`
- `POST /api/charities/<id>/reviews`

Write endpoints require the `X-Community-Passphrase` header matching `COMMUNITY_SHARED_PASSPHRASE` in `config.yaml`.

## Community JSON format

```json
{
  "charities": [
    {
      "name": "Example Relief",
      "website": "https://example.org",
      "registration_country": "France",
      "cause_areas": "water,food",
      "description": "Community maintained entry",
      "reports_json": ["https://example.org/report.pdf"]
    }
  ]
}
```

## Telegram reminder integration

Use `services/telegram_notifier.py` from a Hermes cron job. Example:

```bash
python -m services.telegram_notifier
```

The reminder message uses values from the primary giving goal record plus the configured nisab threshold.

## Docker

```bash
docker build -t sadaqah-hub .
docker run --rm -p 5000:5000 sadaqah-hub
```

## Notes

- `config.yaml` is local-only and ignored by git.
- The app works without internet after installation; community sync is optional.
- PDF generation is fully local.
