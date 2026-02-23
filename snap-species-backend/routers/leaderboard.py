from fastapi import APIRouter

from database import get_db_conn
from schemas import LeaderboardEntryResponse

router = APIRouter(prefix="/api", tags=["leaderboard"])


@router.get("/leaderboard", response_model=list[LeaderboardEntryResponse])
async def get_leaderboard(limit: int = 100):
    conn = await get_db_conn()
    try:
        rows = await conn.fetch("""
            SELECT
                u.id,
                u.name,
                u.created_at,
                COUNT(DISTINCT LOWER(TRIM(s.sci))) AS species_count,
                COUNT(DISTINCT CASE WHEN s.status IN ('CR', 'EN', 'VU') THEN LOWER(TRIM(s.sci)) END) AS endangered_species_count,
                COALESCE(AVG(s.threat_score), 0) AS avg_threat_score
            FROM users u
            LEFT JOIN sightings s ON s.user_id = u.id
            GROUP BY u.id, u.name, u.created_at
            ORDER BY endangered_species_count DESC, avg_threat_score DESC
            LIMIT $1
        """, max(1, min(limit, 500)))
        out = []
        for rank, row in enumerate(rows, start=1):
            created = str(row["created_at"]) if row["created_at"] else ""
            if created and len(created) >= 7:
                month = created[5:7]
                year = created[:4]
                months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
                try:
                    mi = int(month)
                    joined = f"{months[mi-1]} {year}"
                except (ValueError, IndexError):
                    joined = year
            else:
                joined = "—"
            endangered = int(row["endangered_species_count"] or 0)
            avg_score = float(row["avg_threat_score"] or 0)
            score = endangered * 100 + round(avg_score)
            out.append(LeaderboardEntryResponse(
                rank=rank,
                name=row["name"] or "Anonymous",
                score=score,
                species=int(row["species_count"] or 0),
                endangered_species=endangered,
                avg_threat_score=round(avg_score, 1),
                joined=joined,
            ))
        return out
    finally:
        await conn.close()
