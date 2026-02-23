# SnapSpecies Backend

FastAPI backend for SnapSpecies: authentication, species scan with endangerment score, leaderboard, and map sightings.

## Features

- **Auth**: JWT signup/login (`/auth/signup`, `/auth/login`)
- **Scan**: `POST /api/scan` — upload image → species (MobileNet V3) + IUCN Red List endangerment status and **threat score** (0–100) used for leaderboard
- **Leaderboard**: `GET /api/leaderboard` — ranked by total conservation score (sum of sighting threat scores)
- **Map**: `GET /api/sightings` — list sightings for the map

## Classification & endangerment score

- **Species**: Pretrained **MobileNet V3 Large** (ImageNet) for robust animal/species labels.
- **Endangerment**: IUCN Red List API maps species to category (CR, EN, VU, NT, LC). Each category is converted to a **numeric threat score** (e.g. CR=95, EN=80, VU=65) used for:
  - Scan result `threatScore`
  - Stored on each sighting and summed per user for the **leaderboard**

No separate “endangered species only” model is required: we use a strong general classifier plus IUCN for conservation status and scoring.

## Setup

```bash
cd snap-species-backend
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set IUCN_API_KEY (https://apiv3.iucnredlist.org/api/v3/token) and JWT_SECRET
```

## Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Health: `GET http://localhost:8000/health`
- Docs: `http://localhost:8000/docs`

## Environment

| Variable        | Description |
|----------------|-------------|
| `IUCN_API_KEY` | IUCN Red List API token (required for real endangerment data) |
| `JWT_SECRET`    | Secret for JWT signing (use a long random string in production) |
| `DATABASE_PATH`| Optional; default `./snapspecies.db` |

Database is SQLite (file created automatically). Leaderboard and sightings use this DB.
