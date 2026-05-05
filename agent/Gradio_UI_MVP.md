# Gradio UI MVP

Date: 2026-05-05

## Goal

Build the first local Gradio interface around the validated CLI pipeline.

This phase is intentionally a thin UI wrapper. It does not duplicate model code and does not change the Hunyuan3D, SF3D, or ControlNet inference logic.

## Implementation

Added:

- `code/ui/app.py`
- `code/ui/__init__.py`

Runtime decision:

- The UI launches from the `hunyuan3d` conda environment because it already contains `gradio 6.14.0`.
- Each inference run calls the existing CLI through the `trellis310` conda environment.
- The CLI still switches into the `hunyuan3d` or `sf3d` backend environments as needed.

This keeps the UI layer lightweight and preserves the previously validated backend separation.

## UI Scope

Phase 7A supports:

- Single-view sketch/render upload.
- Input-path selector:
  - `direct`
  - `controlnet`
  - `both`
- Backend selector:
  - `hunyuan3d`
  - `sf3d`
  - `both`
- ControlNet prompt and core controls.
- Hunyuan3D step count, octree resolution, and seed.
- Generated GLB preview through `gr.Model3D`.
- File outputs:
  - generated GLB;
  - `summary.json`.
- Intermediate image previews:
  - copied input;
  - normalized image;
  - Canny control map;
  - ControlNet render when generated.
- Mesh metrics and warning tables from `code/postprocess/mesh_report.py`.

## Non-Scope

- Hunyuan3D-2mv multi-view inference is not exposed as a finished UI feature because local Phase 5C did not pass yet.
- Geometry-changing mesh cleanup is not enabled by default.
- Texture generation remains disabled.

## Launch Command

Run from WSL:

```bash
source /home/anker/miniforge3/etc/profile.d/conda.sh
conda activate hunyuan3d
cd /mnt/d/Final_Project
GRADIO_ANALYTICS_ENABLED=False python code/ui/app.py --host 127.0.0.1 --port 7860
```

Or use the helper script:

```bash
bash code/ui/run_gradio_ui.sh
```

Open:

```text
http://127.0.0.1:7860
```

## Validation

Static checks:

- `python -m py_compile code/ui/app.py`
- `build_demo()` construction smoke test
- HTTP launch check on `http://127.0.0.1:7860`

Phase 7B acceptance:

- See `agent/Gradio_UI_Acceptance.md`.
- Single-view `direct + hunyuan3d` UI-wrapper operation passed with a 5-step smoke test and a 30-step formal sample.

Expected runtime behavior:

- Uploading an image and pressing `Run` creates a new run directory under `code/outputs/pipeline_runs/`.
- The app reads `reports/summary.json`.
- The selected generated GLB is shown in the `Model3D` component.
- Mesh metrics and warnings are loaded from the shared mesh report.

## Phase 7A Decision

Phase 7A is implemented and Phase 7B single-view UI acceptance has passed.

Recommended review input:

- `code/test_assets/patent_sketches/usd247201s_sport_shoe/views/right_side_fig4_clean.png`

Recommended first settings:

- `Input path`: `direct`
- `3D backend`: `hunyuan3d`
- `Hunyuan steps`: `5` for UI smoke test, `30` for quality review
- `Octree resolution`: `256`
