import io
import asyncio
import httpx
from functools import lru_cache

import torch
import torchvision.transforms as T
from torchvision.models import mobilenet_v3_large, MobileNet_V3_Large_Weights
from PIL import Image

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


import os
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


class AnimalResult(BaseModel):
    species: str
    endangerment: str

@app.on_event("startup")
async def startup_event():
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

    return AnimalResult(species=species, endangerment=endangerment)
