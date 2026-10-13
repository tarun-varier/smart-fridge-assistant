Type: task
Status: resolved

## Question

GitHub was network-unreachable when this map was charted (2026-09-29): `gh auth status` and a plain `curl` to github.com both timed out. Once connectivity is confirmed working:

1. Create a GitHub repo for this project (confirm name/visibility with Tarun) and push the existing local git history.
2. Migrate this map and its tickets from `.scratch/smart-fridge/` to GitHub issues (map issue labelled `wayfinder:map`, tickets as child issues), so the two teammates can see and comment on it without Claude Code.
3. Record the new repo URL and issue numbers back into this ticket's answer.

This is an AFK task where possible (repo creation, push, issue migration can all be scripted via `gh`), but confirm the repo name/visibility with Tarun first since that's a one-way, externally-visible action.

## Answer

**Repo created:** [tarun-varier/smart-fridge](https://github.com/tarun-varier/smart-fridge) (private, confirmed with Tarun). Local git history committed (one initial commit with `CONTEXT.md`, `docs/`, `.scratch/`) and pushed to `master`.

**Map and tickets migrated** to GitHub issues. Old local ticket number → new GitHub issue number:

- Map → [issue #1](https://github.com/tarun-varier/smart-fridge/issues/1)
- `01-vision-dataset-research` → [#2](https://github.com/tarun-varier/smart-fridge/issues/2) (closed)
- `02-receipt-dataset-ocr-research` → [#3](https://github.com/tarun-varier/smart-fridge/issues/3) (closed)
- `03-category-vocabulary-matching` → [#4](https://github.com/tarun-varier/smart-fridge/issues/4) (closed)
- `04-vision-pipeline-architecture` → [#5](https://github.com/tarun-varier/smart-fridge/issues/5) (closed)
- `05-receipt-pipeline-architecture` → [#6](https://github.com/tarun-varier/smart-fridge/issues/6) (closed)
- `06-shelf-life-table` → [#7](https://github.com/tarun-varier/smart-fridge/issues/7) (closed)
- `07-streamlit-demo-structure` → [#8](https://github.com/tarun-varier/smart-fridge/issues/8) (closed)
- `08-github-migration` (this ticket) → [#9](https://github.com/tarun-varier/smart-fridge/issues/9) (closed)
- `09-dev-environment-setup` → [#10](https://github.com/tarun-varier/smart-fridge/issues/10) (open, frontier)
- `10-vision-head-hyperparameters` → [#11](https://github.com/tarun-varier/smart-fridge/issues/11) (open, frontier)
- `11-receipt-finetuning-dataset-research` → [#12](https://github.com/tarun-varier/smart-fridge/issues/12) (closed)

All tickets linked as native GitHub sub-issues of the map; recorded blocking relationships wired as native GitHub issue dependencies. Labels created: `wayfinder:map`, `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling`, `wayfinder:task`.

**This local `.scratch/smart-fridge/` directory is now a historical snapshot, not the canonical tracker.** The GitHub map issue (#1 above) is canonical going forward; future `/wayfinder` sessions on this project should use the GitHub-tracker conventions.
