# Fill Trial Photos

Place measured-trial photos here and reference them from `paper/fill_trials_template.csv` with repository-relative paths.

Recommended names:

- `P001_top.jpg`
- `P001_side.jpg`
- `P001_section.jpg`

Minimum publishable-row evidence requires an existing top-view photo. Side and section photos are optional per row, but any path entered in the CSV is checked by `make fill-summary`.

Use a scale reference, consistent lighting, and the same orientation/background across trials. `make fill-photo-panel` builds `output/figures/fill_trial_photo_panel.png` only from existing paths declared in `paper/fill_trials_template.csv`; when no measured photos exist, it removes any stale panel image and writes a NOT_READY check report instead.
