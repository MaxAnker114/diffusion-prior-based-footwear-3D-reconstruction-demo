# CLI MVP Evaluation

Date: 2026-05-05

## Goal

Build and validate the first end-to-end command-line MVP skeleton:

```text
designer shoe sketch
  -> preprocessing
  -> optional ControlNet render
  -> SF3D GLB export
  -> mesh validation report
```

This is a CLI skeleton for reproducible experiments. It is not the final UI.

## Implementation

Main CLI:

- `code/pipeline/cli_mvp.py`

Supporting modules:

- `code/preprocess/sketch_preprocess.py`
- `code/controlnet/render_from_control.py`

The CLI supports three modes:

- `direct`: preprocess sketch and send the normalized sketch directly to SF3D.
- `controlnet`: preprocess sketch, render with ControlNet, then send the render to SF3D.
- `both`: run both paths for comparison.

The CLI writes all runtime artifacts under:

- `code/outputs/pipeline_runs/<run_id>/`

This directory is ignored by Git.

## Smoke Test

Input:

- `code/test_assets/patent_sketches/usd247201s_sport_shoe/views/right_side_fig4_clean.png`

Command:

```bash
python code/pipeline/cli_mvp.py \
  code/test_assets/patent_sketches/usd247201s_sport_shoe/views/right_side_fig4_clean.png \
  --run-id phase4_cli_smoke_patent_side \
  --mode both \
  --controlnet-steps 8 \
  --controlnet-seed 116 \
  --texture-resolution 512
```

Result:

- Preprocessing completed.
- ControlNet rendering completed.
- SF3D from ControlNet render completed.
- SF3D direct from normalized sketch completed.
- Mesh validation completed.

Reports:

- `code/outputs/pipeline_runs/phase4_cli_smoke_patent_side/reports/summary.json`
- `code/outputs/pipeline_runs/phase4_cli_smoke_patent_side/reports/mesh_report.json`

## Mesh Validation Summary

### ControlNet Render -> SF3D

- Output GLB: `code/outputs/pipeline_runs/phase4_cli_smoke_patent_side/sf3d/controlnet_render/0/mesh.glb`
- Valid: yes
- Type: `Scene`
- Geometry count: `1`
- Vertices: `12087`
- Faces: `18860`
- Size: `707816 bytes`
- SF3D reported peak GPU memory: `6171.81103515625 MB`

### Direct Sketch -> SF3D

- Output GLB: `code/outputs/pipeline_runs/phase4_cli_smoke_patent_side/sf3d/direct_sketch/0/mesh.glb`
- Valid: yes
- Type: `Scene`
- Geometry count: `1`
- Vertices: `6866`
- Faces: `11536`
- Size: `438084 bytes`
- SF3D reported peak GPU memory: `6171.6015625 MB`

## Status

Phase 4A passed as a CLI skeleton:

- One command can run the MVP pipeline on a single-view patent sketch.
- Intermediate outputs are saved.
- Final GLB outputs are generated.
- Mesh reports are generated.
- Failure handling is basic but readable through command exceptions.

## Phase 4B Mesh Report Layer

Implementation:

- `code/postprocess/mesh_report.py`
- `code/pipeline/cli_mvp.py` now calls this module instead of the earlier minimal `validate_glb` helper.

The new report is non-destructive. It reads generated GLB files and records metrics intended for paper tables and later Gradio display:

- `geometry_count`
- `total_vertices`
- `total_faces`
- aggregate bounds and dimensions
- `smallest_to_longest_ratio` as a thickness/depth proxy
- connected-component count and largest component face count
- surface area
- watertight status
- reliable volume only when the mesh is watertight
- structured warnings, including the internal-structure limitation

Smoke test:

```bash
python code/pipeline/cli_mvp.py \
  code/test_assets/patent_sketches/usd247201s_sport_shoe/views/right_side_fig4_clean.png \
  --run-id phase4b_report_smoke_direct \
  --mode direct \
  --texture-resolution 512
```

Result:

- GLB generated successfully.
- New `mesh_report.json` generated successfully.
- Direct sketch output remained valid.
- Vertices: `6886`
- Faces: `11536`
- Bounds dimensions: `[0.962311, 0.319453, 0.146011]`
- Thickness proxy ratio: `0.15173`
- Connected components: `211`
- Warnings included:
  - `thin_geometry`
  - `many_components`
  - `non_watertight_mesh`
  - `internal_structure_not_validated`

Comparison note from earlier Phase 4A outputs:

- ControlNet render path thickness proxy ratio: approximately `0.34893`.
- Direct sketch path thickness proxy ratio: approximately `0.15173`.
- This supports the earlier observation that ControlNet-rendered input tends to produce fuller SF3D geometry than raw line input, while still requiring manual internal-structure review.

Remaining work before Phase 4 can be considered complete:

- Add a cleaner run manifest format with selected prompt/settings only, instead of storing full command stderr.
- Add optional geometry-changing post-processing once Phase 6 starts.
- Add better visual QA hooks for generated GLB.
- Test on a cleaner single-view designer sketch and a curated three-view set.
- Decide whether the default mode should be `controlnet` or `both` for paper experiments.
