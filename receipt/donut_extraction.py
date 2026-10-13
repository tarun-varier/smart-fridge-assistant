"""Donut zero-shot line-item extraction (ADR 0002, pass 1 of 2).

naver-clova-ix/donut-base-finetuned-cord-v2 used as-is -- zero-shot, no
fine-tuning -- and no custom image preprocessing; relies on Donut's own
built-in image processor.
"""

import re

import torch
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel

CHECKPOINT = "naver-clova-ix/donut-base-finetuned-cord-v2"
TASK_PROMPT = "<s_cord-v2>"

_processor: DonutProcessor | None = None
_model: VisionEncoderDecoderModel | None = None


def _load() -> tuple[DonutProcessor, VisionEncoderDecoderModel]:
    global _processor, _model
    if _model is None:
        _processor = DonutProcessor.from_pretrained(CHECKPOINT)
        _model = VisionEncoderDecoderModel.from_pretrained(CHECKPOINT)
        _model.eval()
    return _processor, _model


@torch.no_grad()
def extract_line_items(image: Image.Image) -> list[str]:
    """Run Donut zero-shot over one receipt image, return raw item-name strings.

    CORD-v2's schema nests items under "menu" as either a dict (one item)
    or a list of dicts (multiple items); both shapes are normalized to a
    flat list of name strings here.
    """
    processor, model = _load()

    pixel_values = processor(image.convert("RGB"), return_tensors="pt").pixel_values
    decoder_input_ids = processor.tokenizer(TASK_PROMPT, add_special_tokens=False, return_tensors="pt").input_ids

    outputs = model.generate(
        pixel_values,
        decoder_input_ids=decoder_input_ids,
        max_length=model.decoder.config.max_position_embeddings,
        pad_token_id=processor.tokenizer.pad_token_id,
        eos_token_id=processor.tokenizer.eos_token_id,
        use_cache=True,
        bad_words_ids=[[processor.tokenizer.unk_token_id]],
        return_dict_in_generate=True,
    )

    sequence = processor.batch_decode(outputs.sequences)[0]
    sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
    sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()
    parsed = processor.token2json(sequence)

    menu = parsed.get("menu", [])
    if isinstance(menu, dict):
        menu = [menu]

    return [item["nm"] for item in menu if isinstance(item, dict) and "nm" in item]
