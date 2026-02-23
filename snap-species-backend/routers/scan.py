import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from config import get_openai_key as config_get_openai_key, get_settings
from database import get_db_conn
from deps import get_current_user_id
from schemas import ScanResultResponse, SpeciesIdentificationResponse
from services.animal_detect import detect_species as animal_detect_species
from services.classification import run_mobilenet
from services.iucn import (
    ENDANGERED_STATUSES,
    IUCN_LABELS,
    endangerment_score,
    endangerment_status,
    get_iucn_habitats,
    get_iucn_species,
    get_iucn_threats,
    population_from_result,
    population_trend_from_result,
)
from services.openai_species import fetch_species_info_openai

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["scan"])


def _species_from_label(raw_label: str) -> tuple[str, str]:
    parts = [p.strip() for p in raw_label.split(",")]
    name = parts[0].title() if parts else "Unknown"
    sci = name
    if len(parts) > 1 and len(parts[-1].split()) >= 2:
        sci = parts[-1]
    return name, sci


async def identify_species_from_image(image_bytes: bytes) -> tuple[str, str, float]:
    result = await animal_detect_species(image_bytes)
    if result:
        return result
    loop = asyncio.get_event_loop()
    raw_label, confidence = await loop.run_in_executor(None, run_mobilenet, image_bytes)
    name, sci = _species_from_label(raw_label)
    return name, sci, confidence


@router.post("/species", response_model=SpeciesIdentificationResponse)
async def species_from_image(image: UploadFile = File(...)):
    if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail="Use JPEG, PNG, or WebP.")
    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be under 10 MB.")
    try:
        name, sci, confidence = await identify_species_from_image(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not process image: {e}")
    return SpeciesIdentificationResponse(name=name, sci=sci, confidence=round(confidence, 1))


def _parse_float(s: str | None) -> float | None:
    if s is None or not str(s).strip():
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


@router.post("/scan", response_model=ScanResultResponse)
async def scan(
    image: UploadFile = File(...),
    lat: Annotated[str | None, Form()] = None,
    lng: Annotated[str | None, Form()] = None,
    user_id: int | None = Depends(get_current_user_id),
):
    lat_f = _parse_float(lat)
    lng_f = _parse_float(lng)
    if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail="Use JPEG, PNG, or WebP.")
    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be under 10 MB.")

    name, sci, confidence = await identify_species_from_image(image_bytes)

    # Key from config (env + .env file, multiple paths)
    openai_key = (get_settings().openai_api_key or config_get_openai_key() or "").strip()
    if not openai_key:
        logger.info("OpenAI key missing: population/habitat/trend/threats/description will be Unknown. Set OPENAI_KEY or OPENAI_API_KEY in snap-species-backend/.env")
    openai_info = await fetch_species_info_openai(name, sci, api_key=openai_key or None)
    population = openai_info.get("population") or "Unknown"
    habitat = openai_info.get("habitat") or "Unknown"
    trend = openai_info.get("trend") or "Unknown"
    threats = list(openai_info.get("threats") or [])
    description = (openai_info.get("description") or "").strip()

    iucn_result = await get_iucn_species(sci)
    threats_from_api: list[str] = []

    if iucn_result:
        raw_cat = (iucn_result.get("category") or iucn_result.get("code") or "NE")
        if isinstance(raw_cat, str):
            raw_cat = raw_cat.strip().upper()[:2]
        else:
            raw_cat = "NE"
        status = endangerment_status(raw_cat)
        threat_score = endangerment_score(raw_cat)
        if not trend or trend == "Unknown":
            trend = population_trend_from_result(iucn_result)
        if not population or population == "Unknown":
            population = population_from_result(iucn_result) or population
        if (not habitat or habitat == "Unknown") and isinstance(iucn_result.get("habitat"), str):
            habitat = iucn_result.get("habitat") or habitat
        if isinstance(iucn_result.get("threats"), list):
            for t in iucn_result["threats"]:
                if isinstance(t, dict) and t.get("title"):
                    threats_from_api.append(t["title"])
    else:
        status = "LC"
        # Use OpenAI threat_score when no IUCN data (0-100)
        openai_ts = openai_info.get("threat_score")
        if isinstance(openai_ts, int) and 0 <= openai_ts <= 100:
            threat_score = openai_ts
        else:
            threat_score = 20
        if not trend or trend == "Unknown":
            trend = "Unknown"
        if not population or population == "Unknown":
            population = "Unknown"
        if not habitat or habitat == "Unknown":
            habitat = "Unknown"

    if not threats and not threats_from_api:
        threats_from_api = await get_iucn_threats(sci)
    if threats_from_api and not threats:
        threats = threats_from_api
    if not habitat or habitat == "Unknown":
        habs = await get_iucn_habitats(sci)
        if habs:
            habitat = ", ".join(habs[:5])

    # Threat score and status come only from IUCN category (never from OpenAI).
    is_endangered = status in ENDANGERED_STATUSES
    endangerment_label = (
        IUCN_LABELS.get(status, "Not endangered")
        if is_endangered
        else "Not endangered"
    )

    nearby = 0
    conn = await get_db_conn()
    try:
        row = await conn.fetchrow(
            "SELECT COUNT(*) AS n FROM sightings WHERE LOWER(sci) = LOWER($1) OR LOWER(name) = LOWER($2)",
            sci, name,
        )
        nearby = row["n"] if row else 0
    finally:
        await conn.close()

    if user_id is not None:
        conn = await get_db_conn()
        try:
            await conn.execute(
                """INSERT INTO sightings (user_id, name, sci, status, lat, lng, threat_score)
                   VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                user_id,
                name,
                sci,
                status,
                lat_f if lat_f is not None else 0.0,
                lng_f if lng_f is not None else 0.0,
                threat_score,
            )
        finally:
            await conn.close()

    return ScanResultResponse(
        name=name,
        sci=sci,
        status=status,
        endangermentLabel=endangerment_label,
        confidence=round(confidence, 1),
        population=population,
        trend=trend,
        threatScore=threat_score,
        habitat=habitat,
        threats=threats[:10],
        nearbySightings=nearby,
        isEndangered=is_endangered,
        description=description,
        savedToMap=user_id is not None,
        openaiQuotaExceeded=bool(openai_info.get("_quota_exceeded")),
    )
