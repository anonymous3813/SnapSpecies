import os
import asyncio

_pool = None

def get_db_url() -> str:
    url = os.environ.get("DB_URL", "postgresql://postgres:postgres@localhost:5432/snapspecies").strip()
    if url.startswith("postgresql://"):
        return url
    return "postgresql://postgres:postgres@localhost:5432/snapspecies"

async def get_pool():
    global _pool
    if _pool is None:
        import asyncpg
        _pool = await asyncpg.create_pool(get_db_url(), min_size=1, max_size=4, command_timeout=60)
    return _pool

async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL DEFAULT '',
                name TEXT NOT NULL DEFAULT '',
                password_hash TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sightings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                sci TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'LC',
                lat DOUBLE PRECISION NOT NULL DEFAULT 0,
                lng DOUBLE PRECISION NOT NULL DEFAULT 0,
                threat_score INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_sightings_user_id ON sightings(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_sightings_created_at ON sightings(created_at DESC)")
        # Migrate existing users table if it was created without username
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT NOT NULL DEFAULT ''")

async def close_db():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
