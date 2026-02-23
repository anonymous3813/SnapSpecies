import io
import os
from functools import lru_cache

import torch
import torchvision.transforms as T
from torchvision.models import mobilenet_v3_large, MobileNet_V3_Large_Weights
from PIL import Image

try:
    import certifi
    if not os.environ.get("SSL_CERT_FILE"):
        os.environ["SSL_CERT_FILE"] = certifi.where()
    if not os.environ.get("REQUESTS_CA_BUNDLE"):
        os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
except Exception:
    pass

PREPROCESS = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


@lru_cache(maxsize=1)
def get_model():
    weights = MobileNet_V3_Large_Weights.IMAGENET1K_V2
    model = mobilenet_v3_large(weights=weights)
    model.eval()
    return model, weights


def run_mobilenet(image_bytes: bytes) -> tuple[str, float]:
    model, weights = get_model()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = PREPROCESS(img).unsqueeze(0)
    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)[0]
    top_idx = probs.argmax().item()
    confidence = probs[top_idx].item() * 100
    return weights.meta["categories"][top_idx], confidence
