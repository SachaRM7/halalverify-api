# HalalVerify API

HalalVerify is a lightweight, open-source MVP for halal verification. It ships with:

- FastAPI backend with OpenAPI docs at `/docs`
- Async SQLAlchemy models for items, sources, submissions, reports, and users
- Alembic migration environment
- Telegram bot commands for `/verify`, `/barcode`, `/report`, and `/stats`
- Minimal browser extension popup for product lookups
- Docker and Docker Compose support
- Pytest coverage for verification, search, submissions, reports, and stats

## Project structure

This repository follows the PRD layout:

- `api/` — FastAPI application and database models
- `bot/` — Telegram bot worker
- `extension/` — Manifest V3 browser extension MVP
- `migrations/` — Alembic migration scripts
- `tests/` — API tests

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn api.main:app --reload
```

API will be available at `http://127.0.0.1:8000`.

Useful endpoints:

- `GET /health`
- `GET /v1/verify/barcode/040000001001`
- `GET /v1/search?q=snickers`
- `POST /v1/submissions`
- `POST /v1/reports`
- `GET /v1/stats`

## Run tests

```bash
pytest
```

## Telegram bot

Set `TELEGRAM_BOT_TOKEN` in `.env`, then run:

```bash
python bot/main.py
```

The bot expects the API to be reachable at `HALALVERIFY_API_URL`.

## Browser extension

Load the `extension/` directory as an unpacked Manifest V3 extension. The popup queries the local API at `http://localhost:8000`.

## Demo data

On first startup the API seeds a few records:

- Snickers Bar (verified halal)
- Marshmallow Gelatin Mix (questionable)
- Sakura Tokyo Halal Ramen (verified halal restaurant)

## Notes

- Verified status is distinct from community-sourced confidence.
- Barcode image recognition uses optional `pyzbar`/`pytesseract` if available; users can always provide barcode digits in the photo caption.
- This MVP includes the moderation/reporting primitives from the PRD, but keeps workflows intentionally simple for self-hosting.
