from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext

from config import get_settings
from database import get_db_conn
from schemas import LoginRequest, SignupRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def get_user_by_email(email: str) -> dict | None:
    conn = await get_db_conn()
    try:
        row = await conn.fetchrow(
            "SELECT id, email, name, password_hash FROM users WHERE email = $1",
            email.strip().lower(),
        )
        return dict(row) if row else None
    finally:
        await conn.close()


@router.post("/signup", response_model=TokenResponse)
async def signup(body: SignupRequest):
    email = body.email.strip().lower()
    if not body.name or len(body.name.strip().split()) < 2:
        raise HTTPException(status_code=400, detail="Please enter your full name.")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    existing = await get_user_by_email(email)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    conn = await get_db_conn()
    try:
        password_hash = hash_password(body.password)
        await conn.execute(
            "INSERT INTO users (email, name, password_hash) VALUES ($1, $2, $3)",
            email, body.name.strip(), password_hash,
        )
        row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
        user_id = row["id"]
    finally:
        await conn.close()

    token = create_access_token(str(user_id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    user = await get_user_by_email(body.email.strip().lower())
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    token = create_access_token(str(user["id"]))
    return TokenResponse(access_token=token)
