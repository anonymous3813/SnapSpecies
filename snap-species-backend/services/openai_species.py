import json
import logging
import os

import httpx

logger = logging.getLogger(__name__)

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_PATH = os.path.join(_BACKEND_DIR, ".env")

# Load .env from backend directory so OPENAI_KEY is in os.environ
try:
    from dotenv import load_dotenv
    load_dotenv(_ENV_PATH, override=True)
except Exception:
    pass


def get_openai_key() -> str:
    """Use config's key (env + .env file, multiple paths) so key is always found when .env is saved."""
    try:
        from config import get_openai_key as config_get_openai_key
        return config_get_openai_key()
    except Exception:
        pass
    key = (os.environ.get("OPENAI_KEY") or os.environ.get("OPENAI_API_KEY") or "").strip()
    if key:
        return key
    if os.path.isfile(_ENV_PATH):
        try:
            with open(_ENV_PATH, "r", encoding="utf-8-sig") as f:
                for line in f:
                    s = line.strip().strip("\r")
                    if not s or s.startswith("#"):
                        continue
                    if "=" in s:
                        k, _, v = s.partition("=")
                        if k.strip() in ("OPENAI_KEY", "OPENAI_API_KEY") and v:
                            return v.strip().strip('"').strip("'")
        except Exception as e:
            logger.warning("Could not read OPENAI key from .env: %s", e)
    return ""


def _extract_json(text: str) -> dict | None:
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    if start >= 0:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break
    return None


async def fetch_species_info_openai(name: str, sci: str, api_key: str | None = None) -> dict:
    """Call OpenAI for population, habitat, trend, threats, description, and optional threat_score (0-100)."""
    out = {
        "population": "Unknown",
        "habitat": "Unknown",
        "trend": "Unknown",
        "threats": [],
        "description": "",
        "threat_score": None,
    }
    key = (api_key or get_openai_key()).strip()
    if not key:
        logger.warning("OpenAI: no API key found. Set OPENAI_KEY or OPENAI_API_KEY in snap-species-backend/.env")
        return out
    species = (name or sci or "Unknown").strip()
    prompt = (
        f'For species "{species}" (scientific: {sci or name}), return ONLY a valid JSON object, no other text. '
        'Required keys: "population" (string, short wild estimate, e.g. "~5000" or "Unknown"), '
        '"habitat" (string, short habitat), '
        '"trend" (exactly one of: Increasing, Stable, Decreasing, Unknown), '
        '"threats" (array of 1-5 short strings), '
        '"description" (string, 1-2 sentences about the animal), '
        '"threat_score" (integer 0-100, conservation risk: 0-20 low, 21-40 moderate, 41-70 high, 71-100 critical). '
        'Example: {"population": "~5000", "habitat": "Tropical forest", "trend": "Decreasing", '
        '"threats": ["Habitat loss", "Poaching"], "description": "A large cat native to Asia.", "threat_score": 65}'
    )
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 600,
                },
            )
            if r.status_code != 200:
                if r.status_code == 429:
                    logger.warning("OpenAI API 429: quota exceeded. Check plan and billing at https://platform.openai.com/account/billing")
                else:
                    logger.warning("OpenAI API error %s: %s", r.status_code, r.text[:200])
                out["_quota_exceeded"] = r.status_code == 429
                return out
            data = r.json()
            content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
            parsed = _extract_json(content)
            if isinstance(parsed, dict):
                if isinstance(parsed.get("population"), str) and parsed["population"].strip():
                    out["population"] = parsed["population"].strip()
                if isinstance(parsed.get("habitat"), str) and parsed["habitat"].strip():
                    out["habitat"] = parsed["habitat"].strip()
                if isinstance(parsed.get("trend"), str) and parsed["trend"] in ("Increasing", "Stable", "Decreasing", "Unknown"):
                    out["trend"] = parsed["trend"]
                if isinstance(parsed.get("threats"), list):
                    out["threats"] = [str(t).strip() for t in parsed["threats"] if t][:10]
                if isinstance(parsed.get("description"), str) and parsed["description"].strip():
                    out["description"] = parsed["description"].strip()
                t = parsed.get("threat_score")
                if isinstance(t, int) and 0 <= t <= 100:
                    out["threat_score"] = t
                elif isinstance(t, (float, str)):
                    try:
                        n = int(float(t))
                        if 0 <= n <= 100:
                            out["threat_score"] = n
                    except (ValueError, TypeError):
                        pass
            else:
                logger.warning("OpenAI: could not parse JSON from response: %s", content[:200])
    except Exception as e:
        logger.warning("OpenAI request failed: %s", e)
    return out


def enrich_species(*args, **kwargs) -> dict | None:
    return None
