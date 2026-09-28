"""Freshness/spoilage classifier: transfer learning on a frozen MobileNetV2
backbone with a small trained head. Training happens in scripts/train_classifier.py
once the dataset is downloaded; this module only builds the architecture and
runs inference from a saved checkpoint.

The checkpoint stores its own label list, so this module never hardcodes class
names or count — it reads whatever the training run actually produced.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torchvision import models, transforms

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "freshness_classifier.pt"
IMAGE_SIZE = 224

_transform = transforms.Compose(
    [
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


def build_model(num_classes: int, freeze_backbone: bool = True) -> nn.Module:
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    if freeze_backbone:
        for param in model.features.parameters():
            param.requires_grad = False
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model


@dataclass
class LoadedClassifier:
    model: nn.Module
    labels: list[str]


def is_trained(model_path: Path = DEFAULT_MODEL_PATH) -> bool:
    return model_path.exists()


def load_classifier(model_path: Path = DEFAULT_MODEL_PATH) -> LoadedClassifier:
    if not model_path.exists():
        raise FileNotFoundError(
            f"no trained classifier at {model_path}; run scripts/train_classifier.py first"
        )
    checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
    labels = checkpoint["labels"]
    model = build_model(num_classes=len(labels))
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return LoadedClassifier(model=model, labels=labels)


def classify_crop(image: Image.Image, loaded: LoadedClassifier) -> tuple[str, float]:
    tensor = _transform(image.convert("RGB")).unsqueeze(0)
    with torch.no_grad():
        logits = loaded.model(tensor)
        probs = torch.softmax(logits, dim=1)[0]
    best_idx = int(torch.argmax(probs))
    return loaded.labels[best_idx], float(probs[best_idx])
