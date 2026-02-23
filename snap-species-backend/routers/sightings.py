from fastapi import APIRouter

from database import get_db_conn
from deps import get_user_name
from schemas import SightingResponse

router = APIRouter(prefix="/api", tags=["sightings"])


def _parse_created_to_ts(created) -> int:
    """Return Unix timestamp in seconds (same as me.py for frontend formatTimestamp)."""
    if created is None:
        return 0
    try:
        if hasattr(created, "timestamp"):
            return int(created.timestamp())
        s = str(created)[:19]
        from datetime import datetime
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())
    except Exception:
        return 0


@router.get("/sightings", response_model=list[SightingResponse])
async def list_sightings(limit: int = 500):
    conn = await get_db_conn()
    try:
        rows = await conn.fetch("""
            SELECT s.id, s.user_id, s.name, s.sci, s.status, s.lat, s.lng, s.threat_score, s.created_at
            FROM sightings s
            ORDER BY s.created_at DESC
            LIMIT $1
        """, max(1, min(limit, 1000)))
        out = []
        for row in rows:
            reporter = await get_user_name(row["user_id"])
            out.append(SightingResponse(
                id=row["id"],
                name=row["name"],
                sci=row["sci"],
                status=row["status"] if row["status"] in ("CR", "EN", "VU", "NT", "LC") else "LC",
                lat=float(row["lat"]),
                lng=float(row["lng"]),
                timestamp=_parse_created_to_ts(row["created_at"]),
                threat_score=int(row["threat_score"]),
                reporter=reporter,
            ))
        return out
    finally:
        await conn.close()
