Note: this repo had no prior research-notes convention; this file is a new location introduced for this research task.

# Vision Pipeline dataset research: fresh vs. spoiled food classification

## Summary / Recommendation

For CPU-only transfer-learning under a ~2.5-week deadline, the best fit is **`sriramr/fruits-fresh-and-rotten-for-classification`** ("Fruits fresh and rotten for classification") as the primary/base dataset: it is the smallest of the candidates found (~13.6k images, 1.95 GB), already ships a ready-made `train/`+`test/` split with one folder per class, and is by far the most widely used and documented dataset of this kind (200K views, 40.6K downloads on Kaggle), which means abundant community reference code for troubleshooting. Its scope is narrow (apples, bananas, oranges only), so if time permits after a working baseline, extend with a slice of **`muhammad0subhan/fruit-and-vegetable-disease-healthy-vs-rotten`** (CC0, 14 produce types x healthy/rotten) to broaden category coverage — but treat that as a stretch goal, not the critical path, since it is ~2.7x larger on disk and its folder-count claims could not be independently cross-checked against a second live source (see flag in its section below). The `ulnnproject/food-freshness-dataset` (6.41 GB, 71.3k images) is oversized for the CPU/timeline constraints and was not chosen as primary despite an explicit Apache-2.0 license.

**Important caveat on methodology:** WebFetch (and direct `curl`) could not reach `kaggle.com` at all from this environment (`connect ECONNREFUSED` on every attempt, including the bare domain). I worked around this using the `r.jina.ai` read-proxy to render the actual live Kaggle dataset pages (title, creator, license field, size/file-count stat, and "About Dataset" text) — this is the real page content, not a blog. However, Kaggle's file/folder "Data Explorer" tree is JS-rendered and did not resolve through the proxy (it showed "this directory is empty" instead of the real tree), so exact per-class image counts and some folder listings below are corroborated by *multiple independent secondary sources* (GitHub repos that load and print the actual directory structure at runtime, academic papers citing the dataset) rather than a direct re-render of Kaggle's file browser. Each field below states which method it came from.

---

## 1. Fruits fresh and rotten for classification (sriramr)

- **URL:** https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification
- **Owner/slug:** `sriramr/fruits-fresh-and-rotten-for-classification`
- **Download method:** `kaggle datasets download -d sriramr/fruits-fresh-and-rotten-for-classification` (Kaggle API), or the page's "Download" button in browser.
- **License:** Shown as **"Unknown"** on the live page metadata (confirmed via two separate page fetches — the dataset landing page and its `/data` tab both report `License: Unknown`, no CC0/MIT/etc. tag set by the uploader). Kaggle's default fallback for datasets without an explicit license is typically treated as "all rights reserved by uploader unless stated otherwise," though in practice such academic/coursework re-use of unlicensed Kaggle datasets for a non-commercial college project is extremely common and low-risk. **Judgment: usable for non-commercial coursework, but not redistributable/commercial-safe; cite the source and do not republish the raw images.** A discussion thread on the page ("using the dataset for non-commercial educational purposes") corroborates that this exact question has been raised by other users, though the actual reply content wasn't retrievable through the proxy.
- **Size:** ~13,599 images total ("13.6k files" per live page stat), **1.95 GB** on disk (per live page stat).
- **Format:** Folder-per-class, pre-split into `train/` and `test/` folders (standard structure for this well-known dataset, corroborated by independent GitHub repos that load it directly, e.g. harshitkd/Fruit-Freshness-Prediction).
- **Classes (6 total):** `freshapples`, `freshbanana`, `freshoranges`, `rottenapples`, `rottenbanana`, `rottenoranges` — reported consistently across every independent secondary source found (multiple GitHub repos with runtime `os.listdir()` output, a Springer book chapter, ScienceDirect article). Not independently re-rendered from Kaggle's live JS file tree due to the network limitation above, but the folder-naming convention is corroborated by code that actually reads the extracted archive, not just a description.
- **Class balance (commonly reported per-class counts, secondary-sourced, not re-verified against a live Data Explorer):** train — freshapples ~1,693, freshbanana ~1,581, freshoranges ~1,466, rottenapples ~2,342, rottenbanana ~2,224, rottenoranges ~1,595; test — smaller held-out counts per class, totaling to the ~13,599 grand total. Treat exact per-class numbers as approximate.
- **Image resolution:** Not stated on the Kaggle page itself (page text says "No description available"). Commonly reported elsewhere as originals around 100x100–256x256 px depending on source photo; not independently confirmed here — plan to resize/normalize during preprocessing regardless (standard for transfer learning).
- **Source:** https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification (fetched via r.jina.ai proxy on 2026-09-29); corroborating structure from https://github.com/harshitkd/Fruit-Freshness-Prediction

---

## 2. Food Freshness Dataset (ulnnproject)

- **URL:** https://www.kaggle.com/datasets/ulnnproject/food-freshness-dataset
- **Owner/slug:** `ulnnproject/food-freshness-dataset`
- **Download method:** `kaggle datasets download -d ulnnproject/food-freshness-dataset`, or browser download.
- **License:** **Apache 2.0**, as stated on the live page (fetched directly). **Judgment: clearly usable for coursework** — Apache 2.0 is a permissive open license, the cleanest license situation of all candidates found.
- **Size:** ~71,300 files, **6.41 GB** total (per live page).
- **Format:** Two top-level folders, `Fresh/` and `Rotten/`, each presumably containing per-food-type subfolders (page description implies this but exact nesting wasn't independently confirmed from a rendered file tree).
- **Classes:** 13 food categories stated on the page: Apple, Banana, Bell Pepper, Bitter Gourd, Capsicum, Carrot, Cucumber, Mango, Okra, Orange, Potato, Strawberry, Tomato — each crossed with Fresh/Rotten (so effectively up to 26 leaf classes if organized as `<Fruit>_Fresh`/`<Fruit>_Rotten`, or 2 top-level classes with a food-type label if organized as `Fresh/<fruit>`). Exact folder nesting not independently verified.
- **Class balance:** Page states images per folder range from ~300 to ~13,700 (large imbalance across categories) — exact per-class counts not listed.
- **Image resolution:** Page states images are standardized to **128x128 pixels**.
- **Note:** Page also mentions images "have undergone preprocessing including grayscale conversion, edge detection, and brightness adjustment" for some images — this could mean the dataset mixes raw and pre-processed image variants, which needs a closer look before use (risk of leaking pre-processed feature maps rather than plain photos).
- **Why not chosen as primary:** at 6.41 GB / 71K images it is the largest of the candidates, working against the CPU-only + 2.5-week constraint (both slower to download/extract and slower per-epoch even with a frozen backbone), despite having the cleanest license.
- **Source:** https://www.kaggle.com/datasets/ulnnproject/food-freshness-dataset (fetched via r.jina.ai proxy on 2026-09-29).

---

## 3. Fruit and Vegetable Disease (Healthy vs Rotten) (muhammad0subhan)

- **URL:** https://www.kaggle.com/datasets/muhammad0subhan/fruit-and-vegetable-disease-healthy-vs-rotten
- **Owner/slug:** `muhammad0subhan/fruit-and-vegetable-disease-healthy-vs-rotten`
- **Download method:** `kaggle datasets download -d muhammad0subhan/fruit-and-vegetable-disease-healthy-vs-rotten`, or browser download.
- **License:** **CC0: Public Domain**, as stated on the live page. **Judgment: excellent for coursework** — CC0 is the least restrictive license possible.
- **Size:** ~29,300 files, **5.21 GB** total (per live page fetch).
- **Format:** Folder-per-class, 28 total class folders (14 produce types x Healthy/Rotten).
- **Classes (28 total):** `Apple_Healthy`, `Apple_Rotten`, `Banana_Healthy`, `Banana_Rotten`, `Bellpepper_Healthy`, `Bellpepper_Rotten`, `Carrot_Healthy`, `Carrot_Rotten`, `Cucumber_Healthy`, `Cucumber_Rotten`, `Grape_Healthy`, `Grape_Rotten`, `Guava_Healthy`, `Guava_Rotten`, `Jujube_Healthy`, `Jujube_Rotten`, `Mango_Healthy`, `Mango_Rotten`, `Orange_Healthy`, `Orange_Rotten`, `Pomegranate_Healthy`, `Pomegranate_Rotten`, `Potato_Healthy`, `Potato_Rotten`, `Strawberry_Healthy`, `Strawberry_Rotten`, `Tomato_Healthy`, `Tomato_Rotten`.
- **Class balance:** Not listed on the page content that was retrievable.
- **Image resolution:** Page states images are JPEG/PNG "with varying sizes" — not a fixed resolution; page itself recommends resizing before training. Not a single stated resolution.
- **⚠ Data-quality flag:** This dataset's reported size (5.21 GB, ~29,300 files, 14 types x 2 classes) is **identical** to candidate #4 below (`zlatan599/fruitquality1`), fetched independently. This is very likely because both are re-uploads/derivatives of the same underlying combined community dataset (a common pattern on Kaggle for popular fresh/rotten produce collections), but I could not confirm this relationship from the pages themselves (no explicit "derived from" credit was retrievable). Treat the two as probably overlapping in image content, not as independent data sources, if considering combining them.
- **Source:** https://www.kaggle.com/datasets/muhammad0subhan/fruit-and-vegetable-disease-healthy-vs-rotten (fetched via r.jina.ai proxy on 2026-09-29).

---

## 4. Fruit and Vegetable (Fresh vs Rotten) (zlatan599 / fruitquality1)

- **URL:** https://www.kaggle.com/datasets/zlatan599/fruitquality1
- **Owner/slug:** `zlatan599/fruitquality1`
- **Download method:** `kaggle datasets download -d zlatan599/fruitquality1`, or browser download.
- **License:** **MIT**, as stated on the live page. **Judgment: usable for coursework** — MIT is permissive, though slightly unusual to see an MIT license applied to an image dataset (MIT is a software license; Kaggle allows uploaders to pick it anyway as a catch-all permissive option). Fine for non-commercial academic use.
- **Size:** ~29,300 files, **5.21 GB** total (per live page fetch) — see duplicate-size flag under candidate #3 above.
- **Format:** Folder-per-class, 14 produce types each with Fresh/Rotten subfolders.
- **Classes (14 types, implies 28 leaf classes if named `<Type>_Fresh`/`<Type>_Rotten` analogous to #3, exact folder-name casing not independently confirmed):** Apple, Banana, Bell pepper, Carrot, Cucumber, Grape, Guava, Jujube, Mango, Orange, Pomegranate, Potato, Strawberry, Tomato.
- **Class balance:** Not listed on the page content that was retrievable.
- **Image resolution:** Page states images were **resized to 224x224 pixels, stored in RGB** — this is the most CNN-ready of all candidates (224x224 matches common ImageNet-pretrained backbone input size, e.g. MobileNetV2/ResNet default).
- **Note:** Page describes this as "combines multiple smaller datasets into one comprehensive resource" with manual dedup — consistent with the likely overlap with candidate #3 flagged above.
- **Source:** https://www.kaggle.com/datasets/zlatan599/fruitquality1 (fetched via r.jina.ai proxy on 2026-09-29).

---

## 5. Fresh and Stale Classification (swoyam2609) — additional candidate found, not primary

- **URL:** https://www.kaggle.com/datasets/swoyam2609/fresh-and-stale-classification
- **Owner/slug:** `swoyam2609/fresh-and-stale-classification`
- **Download method:** `kaggle datasets download -d swoyam2609/fresh-and-stale-classification`, or browser download.
- **License:** **Community Data License Agreement – Permissive – Version 1.0** (CDLA-Permissive-1.0), as stated on the live page. **Judgment: usable for coursework** — CDLA-Permissive-1.0 is an open, permissive data license (similar spirit to MIT/CC0, drafted specifically for datasets), fine for academic use.
- **Size:** ~30.4k files, **3.09 GB** total (per live page).
- **Format/Classes:** Page text describes "apples, oranges, bananas, tomatoes, cucumbers, carrots, and more," each fresh/deteriorated, but the file-tree/class-folder names were not retrievable through the proxy (page showed a generic "folder dataset" parent node, not the expanded leaf names). **Not enough verified structural detail to safely hardcode a class list from this one** — flagged as a possible future option but not used for the recommendation below.
- **Image resolution:** Page describes "high-resolution images captured with professional-grade cameras" but states no pixel dimensions.
- **Source:** https://www.kaggle.com/datasets/swoyam2609/fresh-and-stale-classification (fetched via r.jina.ai proxy on 2026-09-29).

---

## Recommendation

**Primary dataset: `sriramr/fruits-fresh-and-rotten-for-classification`.**

Rationale against the two hard constraints:
- **CPU-only training:** at 1.95 GB / ~13.6k images it is the smallest candidate by a wide margin (next smallest verified candidate is 3.09 GB). With transfer learning (frozen or lightly fine-tuned MobileNetV2/ResNet18 backbone), this size trains in a reasonable number of CPU-hours, and the built-in `train/`+`test/` split avoids needing to write a custom splitter.
- **2.5-week deadline:** it is the most mature, most-used dataset of this shape on Kaggle (200K page views, 40.6K downloads, 6-year track record), meaning class-imbalance handling, common preprocessing pitfalls, and baseline accuracy numbers are all well documented elsewhere — de-risks the timeline versus a newer, less-battle-tested dataset like `ulnnproject/food-freshness-dataset` (1 year old) or the two 14-class combined datasets, whose class-folder naming and per-class counts could not be fully independently verified here.
- **License:** weakest point of this choice — the page shows "Unknown" rather than an explicit open license. For a non-commercial college coursework deliverable (not redistributing the raw images, only training a model and citing the source), this is standard practice and low-risk, but it should be explicitly cited in the project write-up/report as the data source with a link, and the raw dataset should not be re-published.

**Fixed class vocabulary to hardcode for the project** (6 classes, matching the dataset's own folder names so no relabeling step is needed):

```
freshapples
freshbanana
freshoranges
rottenapples
rottenbanana
rottenoranges
```

If a binary fresh/spoiled-only output is preferred for the product-level "Vision Pipeline" decision (rather than exposing the fruit type), collapse these 6 at the application layer into 2 output labels — `fresh` / `spoiled` — by stripping the `fresh`/`rotten` prefix, while still training the 6-way classifier for better signal (fruit identity is a useful auxiliary feature the CNN can learn from with no extra data-collection cost).

**Stretch/extension option:** if time remains after a working 6-class baseline, `muhammad0subhan/fruit-and-vegetable-disease-healthy-vs-rotten` (CC0, 5.21 GB, 28 classes across 14 produce types) is the next-best option to broaden category coverage beyond apples/bananas/oranges — its CC0 license is cleaner than sriramr's "Unknown," but its larger size and the unverified duplicate-content overlap with `zlatan599/fruitquality1` (see flag above) make it a second-phase addition rather than the base dataset for the initial CPU-constrained, time-boxed build.

**Not recommended as primary:** `ulnnproject/food-freshness-dataset` (too large at 6.41 GB for the CPU/timeline budget despite the cleanest Apache-2.0 license), and `swoyam2609/fresh-and-stale-classification` (usable license, but class-folder structure could not be verified well enough here to commit to a class vocabulary from it).
