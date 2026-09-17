"""Original model logo assets, placed as small images on native-vector charts.

Assets are copied from the repository's paper-writing skill. No runtime access
to that skill is required. Text, data marks and backgrounds are never rasterized.
"""
from functools import lru_cache
from hashlib import sha256
from math import isfinite
from pathlib import Path

from PIL import Image

ASSET_DIR = Path(__file__).resolve().parents[1]/"assets/logos/models"
MODEL_LOGOS = {
    "anthropic": {"label":"Claude", "color":"#A36840"},
    "openai": {"label":"GPT", "color":"#3E846B"},
    "gemini": {"label":"Gemini", "color":"#4874C5"},
    "deepseek": {"label":"DeepSeek", "color":"#7261D3"},
    "qwen": {"label":"Qwen", "color":"#927333"},
    "glm": {"label":"GLM", "color":"#3E8495"},
    "kimi": {"label":"Kimi", "color":"#8760BA"},
    "grok": {"label":"Grok", "color":"#5B6070"},
    "mimo": {"label":"MiMo", "color":"#49798D"},
    "minimax": {"label":"MiniMax", "color":"#BE5378"},
}


def logo_path(provider):
    if provider not in MODEL_LOGOS:
        raise ValueError(f"Unknown model logo: {provider!r}; choose from {', '.join(MODEL_LOGOS)}")
    path=ASSET_DIR/(provider+".png")
    if not path.is_file():
        raise FileNotFoundError(f"Missing bundled model logo: {path.name}")
    return path


def draw_model_logo(f,provider,cx,cy, *, size=17):
    """Place an original PNG, centered in a square, preserving alpha and aspect.

    Coordinates and size use Figure's logical units. Model names should be drawn
    separately with f.text(); the logo is an identity aid, not a replacement.
    """
    if not all(isfinite(v) for v in (cx,cy,size)) or not 0<size<=32:
        raise ValueError("Logo size must be finite and within (0, 32] logical units")
    if cx-size/2<0 or cx+size/2>f.width or cy-size/2<0 or cy+size/2>f.height:
        raise ValueError("Logo must fit inside the artboard")
    f.c.saveState()
    f.c.drawImage(str(logo_path(provider)),cx-size/2,f.height-cy-size/2,
                  width=size,height=size,preserveAspectRatio=True,anchor="c",mask="auto")
    f.c.restoreState()


@lru_cache(maxsize=1)
def approved_logo_pixels():
    """Decoded RGB + alpha fingerprints for the PDF verifier's small-logo exception.

    Hash image pixels rather than PNG file bytes because PDF uses a different
    lossless container. Geometry is checked separately by the verifier.
    """
    result={}
    for provider in MODEL_LOGOS:
        with Image.open(logo_path(provider)) as source:
            rgba=source.convert("RGBA")
            rgb=rgba.convert("RGB").tobytes()
            alpha=rgba.getchannel("A").tobytes()
            key=(rgba.width,rgba.height,sha256(rgb).hexdigest(),sha256(alpha).hexdigest())
            result[key]=provider
    return result
