import io
import asyncio
import hashlib
import os
import secrets
import time
import httpx
from functools import lru_cache

import torch
import torchvision.transforms as T
from torchvision.models import mobilenet_v3_large, MobileNet_V3_Large_Weights
from PIL import Image

from fastapi import FastAPI, File, Header, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

try:
    import jwt
except ModuleNotFoundError:
    jwt = None  # pip install PyJWT

# Load .env for JWT_SECRET
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.isfile(_env_path):
        load_dotenv(_env_path)
except ImportError:
    pass

JWT_SECRET = os.environ.get("JWT_SECRET", "change-me-in-production").strip().strip("'\"")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 60 * 60 * 24 * 7  # 7 days

# Database module for users and sightings
import database as db

def _hash_password(password: str) -> str:
    salt = "snapspecies"
    return hashlib.sha256((salt + password).encode()).hexdigest()

def _get_jwt():
    global jwt
    if jwt is None:
        try:
            import jwt as _jwt
            jwt = _jwt
        except ModuleNotFoundError:
            pass
    return jwt

def _create_token(email: str) -> str:
    lib = _get_jwt()
    if lib is None:
        raise HTTPException(
            status_code=503,
            detail="PyJWT not found. In the same terminal where you run uvicorn, run: pip install PyJWT then restart the server."
        )
    payload = {"sub": email, "exp": int(time.time()) + JWT_EXPIRE_SECONDS}
    return lib.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def _decode_token(token: str) -> str | None:
    lib = _get_jwt()
    if lib is None:
        return None
    try:
        payload = lib.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None

def _require_user(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization[7:].strip()
    email = _decode_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return email

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return JSON 500 for unhandled errors; let HTTPException (401, 400, etc.) through."""
    if isinstance(exc, HTTPException):
        raise exc
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )

@lru_cache(maxsize=1)
def get_model():
    weights = MobileNet_V3_Large_Weights.IMAGENET1K_V2
    model = mobilenet_v3_large(weights=weights)
    model.eval()
    return model, weights

PREPROCESS = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def run_mobilenet(image_bytes: bytes) -> str:
    model, weights = get_model()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = PREPROCESS(img).unsqueeze(0)
    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)[0]
    top_idx = probs.argmax().item()
    return weights.meta["categories"][top_idx]


IUCN_API_KEY = os.environ.get("IUCN_API_KEY", "")
IUCN_BASE = "https://apiv3.iucnredlist.org/api/v3"

IUCN_LABELS = {
    "EX": "Extinct",
    "EW": "Extinct in the Wild",
    "CR": "Critically Endangered",
    "EN": "Endangered",
    "VU": "Vulnerable",
    "NT": "Near Threatened",
    "LC": "Least Concern",
    "DD": "Data Deficient",
    "NE": "Not Evaluated",
}

async def get_iucn_status(scientific_name: str) -> str:
    if not IUCN_API_KEY or not scientific_name:
        return "Unknown"
    encoded = scientific_name.replace(" ", "%20")
    url = f"{IUCN_BASE}/species/{encoded}?token={IUCN_API_KEY}"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("result"):
                return "Unknown"
            code = data["result"][0].get("category", "NE")
            return IUCN_LABELS.get(code, "Unknown")
        except Exception:
            return "Unknown"


OPENAI_KEY = os.environ.get("OPENAI_KEY", "").strip().strip("'\"")


async def get_species_info_openai(common_name: str, scientific_name: str) -> tuple[dict | None, bool]:
    """Call OpenAI for population, habitat, threats, trend. Returns (info_dict, quota_exceeded)."""
    if not OPENAI_KEY or not common_name:
        return None, False
    sci = scientific_name or common_name
    prompt = f"""For the species: {common_name} (scientific name: {sci}). Return a short JSON object only, no markdown, with these exact keys:
- "population": one short sentence on population size/trend (e.g. "Declining; about 1000 mature individuals").
- "habitat": one short sentence on primary habitat (e.g. "Tropical forests, grasslands").
- "threats": list of 1-3 short threat strings (e.g. ["Habitat loss", "Poaching"]).
- "trend": exactly one of "Increasing", "Stable", "Decreasing", "Unknown".
- "threat_score": a single integer from 0 to 100 representing overall extinction/conservation risk. Use conservation status, population trend, and threats: Critically Endangered 90-100, Endangered 70-89, Vulnerable 50-69, Near Threatened 30-49, Least Concern 0-29. Be specific per species, not always 20.
If unsure use "Unknown" or empty list; for threat_score use your best estimate."""
    import json
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 400,
                },
            )
            if resp.status_code == 429:
                return None, True
            resp.raise_for_status()
            data = resp.json()
            content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
            content = content.strip().strip("`").strip()
            if content.lower().startswith("json"):
                content = content[4:].strip()
            return json.loads(content), False
        except Exception:
            return None, False


def _threat_score_from_endangerment(endangerment: str) -> int:
    """Fallback threat score when OpenAI is not used or returns no score."""
    m = {
        "Critically Endangered": 95,
        "Endangered": 80,
        "Vulnerable": 65,
        "Near Threatened": 40,
        "Least Concern": 20,
        "Data Deficient": 30,
        "Not Evaluated": 20,
    }
    return m.get((endangerment or "").strip(), 20)


class AnimalResult(BaseModel):
    species: str
    endangerment: str
    sci: str = ""
    threat_score: int = 20
    population: str | None = None
    habitat: str | None = None
    threats: list[str] = []
    trend: str | None = None  # Increasing | Stable | Decreasing | Unknown
    openaiQuotaExceeded: bool = False


class SignupBody(BaseModel):
    username: str
    name: str
    email: str
    password: str


class LoginBody(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.post("/auth/signup", response_model=TokenResponse)
async def auth_signup(body: SignupBody):
    email = (body.email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
        if row:
            raise HTTPException(status_code=400, detail="Email already registered")
        await conn.execute(
            "INSERT INTO users (email, username, name, password_hash) VALUES ($1, $2, $3, $4)",
            email,
            (body.username or "").strip(),
            (body.name or "").strip(),
            _hash_password(body.password or ""),
        )
    token = _create_token(email)
    return TokenResponse(access_token=token)


@app.post("/auth/login", response_model=TokenResponse)
async def auth_login(body: LoginBody):
    email = (body.email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT password_hash, name FROM users WHERE email = $1", email)
    if not row or row["password_hash"] != _hash_password(body.password or ""):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = _create_token(email)
    return TokenResponse(access_token=token)


class MeResponse(BaseModel):
    id: str
    name: str
    email: str


@app.get("/api/me", response_model=MeResponse)
async def api_me(authorization: str | None = Header(None, alias="Authorization")):
    email = _require_user(authorization)
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id, name, email FROM users WHERE email = $1", email)
    if not row:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return MeResponse(id=str(row["id"]), name=row["name"] or email, email=row["email"])


class SightingResponse(BaseModel):
    id: int
    name: str
    sci: str
    status: str
    lat: float
    lng: float
    timestamp: int
    threat_score: int
    reporter: str


class UserStatsResponse(BaseModel):
    total_sightings: int
    endangered_species: int
    avg_threat_score: float


class LeaderboardEntryResponse(BaseModel):
    rank: int
    name: str
    score: int
    species: int
    joined: str


def _ts(created_at) -> int:
    if created_at is None:
        return 0
    if hasattr(created_at, "timestamp"):
        return int(created_at.timestamp())
    return 0


@app.get("/api/sightings", response_model=list[SightingResponse])
async def list_sightings():
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT s.id, s.name, s.sci, s.status, s.lat, s.lng, s.threat_score, s.created_at, u.name AS reporter_name
            FROM sightings s
            JOIN users u ON u.id = s.user_id
            ORDER BY s.created_at DESC
            LIMIT 500
        """)
    return [
        SightingResponse(
            id=r["id"],
            name=r["name"],
            sci=r["sci"],
            status=r["status"] if r["status"] in ("CR", "EN", "VU", "NT", "LC") else "LC",
            lat=float(r["lat"]),
            lng=float(r["lng"]),
            timestamp=_ts(r["created_at"]),
            threat_score=int(r["threat_score"]),
            reporter=r["reporter_name"] or "Unknown",
        )
        for r in rows
    ]


@app.get("/api/me/sightings", response_model=list[SightingResponse])
async def list_my_sightings(authorization: str | None = Header(None, alias="Authorization")):
    email = _require_user(authorization)
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        user_row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
        if not user_row:
            raise HTTPException(status_code=401, detail="Not authenticated")
        uid = user_row["id"]
        rows = await conn.fetch(
            "SELECT s.id, s.name, s.sci, s.status, s.lat, s.lng, s.threat_score, s.created_at FROM sightings s WHERE s.user_id = $1 ORDER BY s.created_at DESC LIMIT 200",
            uid,
        )
        u_name = await conn.fetchval("SELECT name FROM users WHERE id = $1", uid)
    reporter = u_name or email
    return [
        SightingResponse(
            id=r["id"],
            name=r["name"],
            sci=r["sci"],
            status=r["status"] if r["status"] in ("CR", "EN", "VU", "NT", "LC") else "LC",
            lat=float(r["lat"]),
            lng=float(r["lng"]),
            timestamp=_ts(r["created_at"]),
            threat_score=int(r["threat_score"]),
            reporter=reporter,
        )
        for r in rows
    ]


@app.get("/api/me/stats", response_model=UserStatsResponse)
async def get_my_stats(authorization: str | None = Header(None, alias="Authorization")):
    email = _require_user(authorization)
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        user_row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
        if not user_row:
            raise HTTPException(status_code=401, detail="Not authenticated")
        uid = user_row["id"]
        row = await conn.fetchrow("""
            SELECT COUNT(*) AS total_sightings,
                   COUNT(*) FILTER (WHERE s.status IN ('CR','EN','VU')) AS endangered_species,
                   COALESCE(AVG(s.threat_score)::numeric, 0) AS avg_threat_score
            FROM sightings s WHERE s.user_id = $1
        """, uid)
    return UserStatsResponse(
        total_sightings=row["total_sightings"] or 0,
        endangered_species=row["endangered_species"] or 0,
        avg_threat_score=float(row["avg_threat_score"] or 0),
    )


class CreateSightingBody(BaseModel):
    name: str
    sci: str
    status: str = "LC"
    lat: float = 0.0
    lng: float = 0.0
    threat_score: int = 0


@app.post("/api/sightings", response_model=SightingResponse)
async def create_sighting(
    body: CreateSightingBody,
    authorization: str | None = Header(None, alias="Authorization"),
):
    email = _require_user(authorization)
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        user_row = await conn.fetchrow("SELECT id, name FROM users WHERE email = $1", email)
        if not user_row:
            raise HTTPException(status_code=401, detail="Not authenticated")
        uid = user_row["id"]
        status = body.status if body.status in ("CR", "EN", "VU", "NT", "LC") else "LC"
        row = await conn.fetchrow(
            """INSERT INTO sightings (user_id, name, sci, status, lat, lng, threat_score)
               VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id, name, sci, status, lat, lng, threat_score, created_at""",
            uid, body.name, body.sci, status, body.lat, body.lng, min(100, max(0, body.threat_score)),
        )
    return SightingResponse(
        id=row["id"],
        name=row["name"],
        sci=row["sci"],
        status=row["status"],
        lat=float(row["lat"]),
        lng=float(row["lng"]),
        timestamp=_ts(row["created_at"]),
        threat_score=int(row["threat_score"]),
        reporter=user_row["name"] or email,
    )


@app.get("/api/leaderboard", response_model=list[LeaderboardEntryResponse])
async def get_leaderboard():
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT u.name, u.created_at,
                   COUNT(s.id) AS species,
                   COALESCE(SUM(s.threat_score), 0)::int AS score
            FROM users u
            LEFT JOIN sightings s ON s.user_id = u.id
            GROUP BY u.id, u.name, u.created_at
            HAVING COUNT(s.id) > 0
            ORDER BY score DESC
            LIMIT 100
        """)
    out = []
    for i, r in enumerate(rows, 1):
        joined = r["created_at"]
        if hasattr(joined, "strftime"):
            joined = joined.strftime("%b %Y")
        else:
            joined = str(joined)[:7] if joined else "—"
        out.append(LeaderboardEntryResponse(
            rank=i,
            name=(r["name"] or "Observer").strip() or "Observer",
            score=int(r["score"] or 0),
            species=int(r["species"] or 0),
            joined=joined,
        ))
    return out


@app.on_event("startup")
async def startup_event():
    import sys
    await db.init_db()
    if _get_jwt() is None:
        print("Auth: PyJWT not installed. Run this in the same environment:", sys.executable, "-m pip install PyJWT")
    else:
        print("Auth: PyJWT OK")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, get_model)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/identify", response_model=AnimalResult)
async def identify(file: UploadFile = File(...)):
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail="Use JPEG, PNG, or WebP.")

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be under 10 MB.")

    loop = asyncio.get_event_loop()
    try:
        raw_label = await loop.run_in_executor(None, run_mobilenet, image_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not process image: {e}")

    parts = [p.strip() for p in raw_label.split(",")]
    species = parts[0].title()
    scientific_name = parts[-1] if len(parts) > 1 and len(parts[-1].split()) == 2 else species

    endangerment = await get_iucn_status(scientific_name)
    threat_score = _threat_score_from_endangerment(endangerment)

    population, habitat, threats, trend, openai_quota = None, None, [], None, False
    if OPENAI_KEY:
        try:
            info, openai_quota = await get_species_info_openai(species, scientific_name)
            if info:
                population = info.get("population") or None
                habitat = info.get("habitat") or None
                threats = info.get("threats") if isinstance(info.get("threats"), list) else []
                t = (info.get("trend") or "").strip()
                if t in ("Increasing", "Stable", "Decreasing", "Unknown"):
                    trend = t
                raw = info.get("threat_score")
                if isinstance(raw, (int, float)):
                    threat_score = min(100, max(0, int(raw)))
        except Exception:
            pass
    return AnimalResult(
        species=species,
        endangerment=endangerment,
        sci=scientific_name,
        threat_score=threat_score,
        population=population,
        habitat=habitat,
        threats=threats or [],
        trend=trend,
        openaiQuotaExceeded=openai_quota,
    )
