from fastapi import APIRouter, Depends

from database import get_db_conn
from deps import get_user_name, require_user
from schemas import SightingResponse, UserProfileResponse, UserStatsResponse

router = APIRouter(prefix="/api", tags=["me"])


@router.get("/me", response_model=UserProfileResponse)
async def get_me(user_id: int = Depends(require_user)):
    conn = await get_db_conn()
    try:
        row = await conn.fetchrow(
            "SELECT id, name, email FROM users WHERE id = $1", user_id
        )
        if not row:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="User not found")
        return UserProfileResponse(id=row["id"], name=row["name"], email=row["email"])
    finally:
        await conn.close()


def _parse_created_to_ts(created) -> int:
    if created is None:
        return 0
    try:
        if hasattr(created, "timestamp"):
            return int(created.timestamp())
        from datetime import datetime
        s = str(created)[:19]
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())
    except Exception:
        return 0


@router.get("/me/sightings", response_model=list[SightingResponse])
async def get_my_sightings(user_id: int = Depends(require_user)):
    conn = await get_db_conn()
    try:
        rows = await conn.fetch("""
            SELECT id, name, sci, status, lat, lng, threat_score, created_at
            FROM sightings WHERE user_id = $1 ORDER BY created_at DESC LIMIT 200
        """, user_id)
        reporter = await get_user_name(user_id)
        return [
            SightingResponse(
                id=r["id"],
                name=r["name"],
                sci=r["sci"],
                status=r["status"] if r["status"] in ("CR", "EN", "VU", "NT", "LC") else "LC",
                lat=float(r["lat"]),
                lng=float(r["lng"]),
                timestamp=_parse_created_to_ts(r["created_at"]),
                threat_score=int(r["threat_score"]),
                reporter=reporter,
            )
            for r in rows
        ]
    finally:
        await conn.close()


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_my_stats(user_id: int = Depends(require_user)):
    conn = await get_db_conn()
    try:
        row = await conn.fetchrow("""
            SELECT
                COUNT(*) AS total_sightings,
                COUNT(DISTINCT CASE WHEN status IN ('CR', 'EN', 'VU') THEN LOWER(TRIM(sci)) END) AS endangered_species,
                COALESCE(AVG(threat_score), 0) AS avg_threat_score
            FROM sightings
            WHERE user_id = $1
        """, user_id)
        return UserStatsResponse(
            endangered_species=int(row["endangered_species"] or 0),
            total_sightings=int(row["total_sightings"] or 0),
            avg_threat_score=round(float(row["avg_threat_score"] or 0), 1),
        )
    finally:
        await conn.close()
