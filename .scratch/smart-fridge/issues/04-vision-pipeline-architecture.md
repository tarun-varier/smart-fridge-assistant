Type: grilling
Status: resolved
Assignee: Tarun Varier
Blocked by: 01

## Question

Given the Vision Pipeline dataset chosen in the vision-dataset-research ticket, decide the concrete architecture and training plan: which pretrained backbone to fine-tune (e.g. MobileNetV2, EfficientNet-lite, or another CPU-friendly option), input resolution, what layers get frozen vs. fine-tuned, train/val/test split, and a rough CPU training-time budget that fits the Oct 15, 2026 deadline.

## Answer

**Backbone: ResNet18** (torchvision, ImageNet-pretrained) at **224×224**. Chosen over MobileNetV2/MobileNetV3-Small/ShuffleNetV2/SqueezeNet1.1 despite those having fewer FLOPs on paper: depthwise separable convolutions (what makes those models "lighter") are a known weak spot in PyTorch's default CPU backend, so the paper-FLOPs advantage doesn't reliably translate into CPU wall-clock speed. ResNet18 is also the most battle-tested transfer-learning default, lowering implementation risk for a solo, Claude-Code-driven build. Full reasoning and rejected alternatives recorded in `docs/adr/0001-vision-pipeline-backbone.md`.

**Train/val/test:** the dataset ships only `train/`+`test/`. Carve an **85/15 stratified split** out of `train/` into train/val; the shipped `test/` folder stays fully held out, used only for final reported metrics.

**Fine-tuning plan — "Plan A" (required/graded approach):** freeze the entire ResNet18 backbone, run one forward-only pass over every image to extract its feature vector, cache those vectors, then train only a small new classification head on the cached features. Avoids re-running the expensive frozen backbone every epoch.

**"Plan B" (explicit stretch, not required):** after Plan A works, optionally unfreeze the backbone's last conv block/stage and fine-tune end-to-end at a low learning rate for a few more epochs, only if time/accuracy pressure justifies it.

**Data augmentation: skipped for v1.** Incompatible with Plan A's feature caching (cached features assume one fixed deterministic transform per image). Left as a stretch lever tied to Plan B if accuracy disappoints.

**Training time ceiling: a few hours** (committed budget). Expected to actually land well under an hour via Plan A, but that estimate is unverified — web research was unavailable when this was decided — hence the wider committed ceiling as a safety margin.

Backbone/CPU-tradeoff reasoning recorded as an ADR (`docs/adr/0001-vision-pipeline-backbone.md`) since it's hard to reverse, non-obvious, and a real trade-off; not added to `CONTEXT.md` since it's implementation detail, not domain vocabulary.
