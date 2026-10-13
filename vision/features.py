"""Frozen ResNet18 feature extraction (ADR 0001 / issue #5, "Plan A").

One forward-only pass per image at 224x224, no augmentation -- cached
features assume a single fixed deterministic transform per image.
"""

import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

FEATURE_TRANSFORM = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ]
)


class ManifestImageDataset(Dataset):
    def __init__(self, rows: list[dict], class_to_idx: dict[str, int], transform=FEATURE_TRANSFORM):
        self.rows = rows
        self.class_to_idx = class_to_idx
        self.transform = transform

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int):
        row = self.rows[idx]
        image = Image.open(row["path"]).convert("RGB")
        image = self.transform(image)
        label = self.class_to_idx[row["label"]]
        return image, label


def build_frozen_resnet18() -> nn.Module:
    backbone = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    backbone.fc = nn.Identity()  # expose the 512-dim pooled feature vector
    backbone.eval()
    for param in backbone.parameters():
        param.requires_grad_(False)
    return backbone


@torch.no_grad()
def extract_features(backbone: nn.Module, loader: DataLoader) -> tuple[torch.Tensor, torch.Tensor]:
    all_features, all_labels = [], []
    for images, labels in loader:
        all_features.append(backbone(images))
        all_labels.append(labels)
    return torch.cat(all_features), torch.cat(all_labels)
