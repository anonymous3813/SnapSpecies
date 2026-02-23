from __future__ import annotations

import httpx

from config import get_settings

IUCN_BASE = "https://apiv3.iucnredlist.org/api/v3"

ENDANGERED_STATUSES = {"CR", "EN", "VU"}

CATEGORY_TO_STATUS = {
    "EX": "CR",
    "EW": "CR",
    "CR": "CR",
    "EN": "EN",
    "VU": "VU",
    "NT": "NT",
    "LC": "LC",
    "DD": "LC",
    "NE": "LC",
}

CATEGORY_TO_THREAT_SCORE = {
    "EX": 100,
    "EW": 98,
    "CR": 95,
    "EN": 80,
    "VU": 65,
    "NT": 45,
    "LC": 20,
    "DD": 25,
    "NE": 25,
}

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

TREND_MAP = {
    "Increasing": "Increasing",
    "Stable": "Stable",
    "Decreasing": "Decreasing",
    "Unknown": "Unknown",
}


def _encode_name(name: str) -> str:
    return name.strip().replace(" ", "%20")


async def _iucn_get(path: str) -> dict | list | None:
    key = get_settings().iucn_api_key
    if not key:
        return None
    path = path if path.startswith("/") else f"/{path}"
    url = f"{IUCN_BASE}{path}?token={key}"
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None


async def get_iucn_species(scientific_name: str) -> dict | None:
    if not scientific_name or not scientific_name.strip():
        return None
    for name in (scientific_name.strip(), _genus_species(scientific_name)):
        if not name:
            continue
        data = await _iucn_get(f"/species/{_encode_name(name)}")
        if data and data.get("result"):
            return data["result"][0]
    return None


def _genus_species(scientific_name: str) -> str | None:
    parts = scientific_name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"
    return None


async def get_iucn_threats(scientific_name: str) -> list[str]:
    if not scientific_name or not scientific_name.strip():
        return []
    for name in (scientific_name.strip(), _genus_species(scientific_name)):
        if not name:
            continue
        data = await _iucn_get(f"/species/threats/{_encode_name(name)}")
        if not data or not isinstance(data.get("result"), list):
            continue
        out = []
        for row in data["result"]:
            if isinstance(row, dict):
                if row.get("title"):
                    out.append(str(row["title"]))
                elif row.get("code"):
                    out.append(str(row["code"]))
        if out:
            return out[:15]
    return []


async def get_iucn_habitats(scientific_name: str) -> list[str]:
    if not scientific_name or not scientific_name.strip():
        return []
    for name in (scientific_name.strip(), _genus_species(scientific_name)):
        if not name:
            continue
        data = await _iucn_get(f"/species/habitats/{_encode_name(name)}")
        if not data or not isinstance(data.get("result"), list):
            continue
        out = []
        for row in data["result"]:
            if isinstance(row, dict):
                if row.get("habitat"):
                    out.append(str(row["habitat"]))
                elif row.get("code"):
                    out.append(str(row["code"]))
        if out:
            return out
    return []


def population_from_result(result: dict) -> str:
    for key in ("population", "population_trend", "rationale"):
        val = result.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return "Unknown"


def endangerment_status(raw_category: str) -> str:
    return CATEGORY_TO_STATUS.get(raw_category, "LC")


def endangerment_score(raw_category: str) -> int:
    return CATEGORY_TO_THREAT_SCORE.get(raw_category, 25)


def population_trend_from_result(result: dict) -> str:
    trend = (result.get("population_trend") or "").strip() or "Unknown"
    return TREND_MAP.get(trend, "Unknown")
