Type: research
Status: resolved

## Question

For the Vision Pipeline (fresh vs. spoiled classification on a single food-item photo/crop), investigate the candidate datasets named in the original project idea:

- The Kaggle "Food Freshness Dataset"
- Any well-known "rotten vs. fresh" fruit/vegetable image-pair datasets on Kaggle

For each candidate found, establish:
- Direct URL and how it's downloaded (Kaggle API vs. direct link)
- License and whether it's usable for a college coursework project
- Size (image count, disk size) and format (folder-per-class, CSV + images, etc.)
- The actual list of food Categories covered (exact class names) — this directly determines the Category vocabulary used elsewhere in this project
- Class balance (fresh vs. spoiled counts) and image resolution/quality, since training happens on CPU only

Write findings to a Markdown file (cite sources) and note where you saved it. Flag clearly which dataset (or combination) looks like the strongest fit given CPU-only training and a ~2.5 week deadline.

## Answer

Recommended primary dataset: **`sriramr/fruits-fresh-and-rotten-for-classification`** ("Fruits fresh and rotten for classification" on Kaggle) — 6 classes (`freshapples`, `freshbanana`, `freshoranges`, `rottenapples`, `rottenbanana`, `rottenoranges`), ~13,599 images / 1.95 GB, pre-split `train/`+`test/` folders, license shown as "Unknown" on the live Kaggle page (standard low-risk for non-commercial coursework with citation, not for redistribution). It's the smallest and most battle-tested candidate found, which best fits CPU-only training and the ~2.5-week deadline. As a stretch extension (not on the critical path), `muhammad0subhan/fruit-and-vegetable-disease-healthy-vs-rotten` (CC0, 28 classes across 14 produce types, 5.21 GB) can broaden category coverage later. Two other candidates (`ulnnproject/food-freshness-dataset`, Apache-2.0 but 6.41 GB/71k images, and `swoyam2609/fresh-and-stale-classification`, CDLA-Permissive-1.0 but unverifiable class-folder structure) were investigated and set aside for the reasons detailed in the findings file.

Full findings, license/size/format details for all 5 candidates investigated, and the reasoning behind the class-vocabulary choice: `.scratch/smart-fridge/issues/01-research-findings.md`
