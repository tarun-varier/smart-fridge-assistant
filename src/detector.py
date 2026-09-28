"""Localize candidate food items in a fridge photo with a pretrained (COCO) YOLOv8n.

We do not train a detector: COCO's food-related classes are sparse (no milk,
cheese, bread, or leafy greens), so this only finds produce/prepared-food
classes COCO knows about (apple, banana, orange, broccoli, carrot, sandwich,
hot dog, pizza, donut, cake). Anything else falls back to classifying the
whole photo. This tradeoff is spelled out in report.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

YOLO_WEIGHTS_PATH = Path(__file__).resolve().parent.parent / "models" / "yolov8n.pt"

FOOD_CLASS_NAMES = {
    "banana", "apple", "orange", "sandwich", "hot dog",
    "pizza", "donut", "cake", "broccoli", "carrot",
}

_model = None


def _get_model():
    global _model
    if _model is None:
        from ultralytics import YOLO

        _model = YOLO(str(YOLO_WEIGHTS_PATH))
    return _model


@dataclass
class FoodCrop:
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]
    image: Image.Image


def detect_food_crops(image_path: str, conf_threshold: float = 0.25) -> list[FoodCrop]:
    model = _get_model()
    results = model.predict(image_path, conf=conf_threshold, verbose=False)
    full_image = Image.open(image_path).convert("RGB")

    crops: list[FoodCrop] = []
    for result in results:
        names = result.names
        for box in result.boxes:
            class_name = names[int(box.cls[0])]
            if class_name not in FOOD_CLASS_NAMES:
                continue
            x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())
            crops.append(
                FoodCrop(
                    class_name=class_name,
                    confidence=float(box.conf[0]),
                    bbox=(x1, y1, x2, y2),
                    image=full_image.crop((x1, y1, x2, y2)),
                )
            )

    if not crops:
        crops.append(
            FoodCrop(
                class_name="unknown",
                confidence=0.0,
                bbox=(0, 0, full_image.width, full_image.height),
                image=full_image,
            )
        )
    return crops
