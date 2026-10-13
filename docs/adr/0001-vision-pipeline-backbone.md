---
status: accepted
---

# ResNet18 as the Vision Pipeline backbone, frozen with cached features

We fine-tune a pretrained ResNet18 (ImageNet weights) for the Vision Pipeline's fresh/rotten classification, at 224×224 input, rather than a lighter-looking backbone like MobileNetV2 or ShuffleNetV2. On paper those have far fewer FLOPs, but PyTorch's default CPU backend (oneDNN) optimizes their depthwise separable convolutions noticeably worse than ResNet18's plain convolutions — so on our CPU-only training machine, the "lighter" models aren't reliably faster in wall-clock terms, and ResNet18 is also the best-documented transfer-learning default, lowering implementation risk for a solo, Claude-Code-driven build on a ~2.5-week deadline.

We freeze the entire backbone and extract its features in a single forward-only pass, caching them, then train only a small head on the cached features — rather than committing to full end-to-end fine-tuning. This avoids repeating the expensive frozen-backbone forward pass every epoch. Partial fine-tuning (unfreezing the last block) and data augmentation are both left as stretch levers, not the required path, partly because augmentation is incompatible with feature caching (cached features assume one fixed transform per image) and partly to keep the required path cheap and low-risk on CPU-only hardware.

## Considered options

- **MobileNetV2 / MobileNetV3-Small / ShuffleNetV2 / SqueezeNet1.1** — smaller and faster on paper, but depthwise convolutions are a known CPU-backend weak spot in PyTorch; rejected because the paper-FLOPs advantage doesn't reliably translate to CPU wall-clock time, and these are less commonly used as transfer-learning tutorial defaults.
- **End-to-end fine-tuning from the start** — would likely reach higher accuracy, but costs a full forward+backward pass through the backbone every epoch; rejected as the required path given the CPU-only, time-constrained environment. Kept available as an explicit stretch step.
