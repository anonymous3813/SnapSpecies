import httpx

from config import get_settings

ANIMAL_DETECT_BASE = "https://www.animaldetect.com/api/v1"


async def detect_species(image_bytes: bytes, country: str | None = None) -> tuple[str, str, float] | None:
    key = get_settings().animal_detect_api_key
    if not key:
        return None
    url = f"{ANIMAL_DETECT_BASE}/detect"
    headers = {"Authorization": f"Bearer {key}"}
    files = {"image": ("image.jpg", image_bytes, "image/jpeg")}
    data: dict[str, str] = {}
    if country:
        data["country"] = country
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(url, headers=headers, files=files, data=data or None)
            resp.raise_for_status()
            body = resp.json()
        except Exception:
            return None
    detections = body.get("detections") or body.get("results") or body.get("predictions") or []
    if not detections:
        first = body.get("detection") or body.get("top_prediction")
        if isinstance(first, dict):
            detections = [first]
    if not detections:
        return None
    d = detections[0] if isinstance(detections[0], dict) else {}
    name = (
        d.get("common_name")
        or d.get("name")
        or d.get("label")
        or d.get("species")
        or "Unknown"
    )
    if isinstance(name, dict):
        name = name.get("common") or name.get("scientific") or "Unknown"
    sci = (
        d.get("scientific_name")
        or d.get("sci")
        or d.get("species")
        or d.get("taxon")
        or name
    )
    if isinstance(sci, dict):
        sci = sci.get("scientific") or sci.get("common") or name
    conf = float(d.get("confidence", 0) or d.get("score", 0))
    if conf <= 0 and isinstance(d.get("confidence"), (int, float)):
        conf = float(d["confidence"])
    conf_pct = conf * 100 if conf <= 1 else conf
    return (str(name).strip().title() or "Unknown", str(sci).strip() or name, round(conf_pct, 1))
