"""Person mask from SegFormer-B0 (ADE20K), soft and full resolution.

The model is 15 MB. It is parked on the CPU between jobs instead of being
re-read from disk every time.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F

MODEL_ID = "nvidia/segformer-b0-finetuned-ade-512-512"
PERSON = 12   # ADE20K "person"

_processor = None
_model = None


def _load():
    global _processor, _model
    if _model is None:
        from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor
        print("[Digital Mastering] Loading SegFormer-B0...")
        _processor = SegformerImageProcessor.from_pretrained(MODEL_ID)
        _model = SegformerForSemanticSegmentation.from_pretrained(MODEL_ID).eval()
    return _processor, _model


@torch.no_grad()
def person_mask(pil_image, device):
    """(1, 1, H, W) probability that each pixel is a person, 0..1."""
    processor, model = _load()
    model.to(device)
    inputs = processor(images=pil_image.convert("RGB"), return_tensors="pt")
    logits = model(pixel_values=inputs["pixel_values"].to(device)).logits   # (1, 150, 128, 128)
    # Softmax at the model's own 128x128, then upsample only the one channel
    # needed; all 150 class maps at 2048x2048 would be about 2.5 GB of VRAM.
    # The probability rather than argmax also gives a soft edge, so no extra
    # blur pass is needed.
    prob = logits.softmax(1)[:, PERSON:PERSON + 1].float()
    return F.interpolate(prob, size=(pil_image.height, pil_image.width),
                         mode="bilinear", align_corners=False)


def park():
    """Move the model off the GPU between jobs."""
    if _model is not None:
        _model.to("cpu")
