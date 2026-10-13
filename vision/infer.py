"""Single-photo Vision Pipeline inference (issue #11: Vision head
hyperparameters), reactive only -- the caller decides when a confirmation
photo is taken; this module never runs on its own (CONTEXT.md: Vision
Pipeline).
"""

from pathlib import Path

import torch
from PIL import Image

from vision.dataset import CLASSES
from vision.features import FEATURE_TRANSFORM, build_frozen_resnet18
from vision.model import VisionHead

CHECKPOINT_PATH = Path(__file__).resolve().parent.parent / "models" / "vision_head_best.pt"

# CONTEXT.md: Category is the classifier label with its fresh/rotten
# prefix stripped (freshapples/rottenapples -> apple) -- spelled out
# explicitly since the label set doesn't singularize "apples"/"oranges".
_LABEL_TO_CATEGORY = {
    "freshapples": "apple",
    "rottenapples": "apple",
    "freshbanana": "banana",
    "rottenbanana": "banana",
    "freshoranges": "orange",
    "rottenoranges": "orange",
}

_backbone: torch.nn.Module | None = None
_head: torch.nn.Module | None = None


def _load() -> tuple[torch.nn.Module, torch.nn.Module]:
    global _backbone, _head
    if _head is None:
        _backbone = build_frozen_resnet18()
        _head = VisionHead()
        checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu")
        _head.load_state_dict(checkpoint["state_dict"])
        _head.eval()
    return _backbone, _head


@torch.no_grad()
def classify(image: Image.Image) -> tuple[str, bool]:
    """Classify one confirmation photo. Returns (category, is_fresh)."""
    backbone, head = _load()
    pixel_values = FEATURE_TRANSFORM(image.convert("RGB")).unsqueeze(0)
    features = backbone(pixel_values)
    label = CLASSES[head(features).argmax(dim=1).item()]
    return _LABEL_TO_CATEGORY[label], label.startswith("fresh")
