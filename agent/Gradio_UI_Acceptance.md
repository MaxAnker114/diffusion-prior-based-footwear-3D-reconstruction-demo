# Gradio UI Acceptance

Date: 2026-05-05

## Goal

Validate that the Gradio UI layer can drive the current single-view footwear reconstruction pipeline and return usable demo artifacts.

The accepted path for this checkpoint is:

```text
single-view shoe sketch -> UI wrapper -> CLI MVP -> Hunyuan3D-2mini -> mesh report -> UI outputs
```

## Page Check

The local Gradio page was opened at:

```text
http://127.0.0.1:7860
```

Visible UI sections were confirmed:

- input image upload;
- `direct / controlnet / both` input-path selector;
- `hunyuan3d / sf3d / both` backend selector;
- ControlNet prompt and controls;
- Hunyuan3D controls;
- generated mesh preview;
- GLB and summary JSON outputs;
- copied input, normalized image, Canny map, and ControlNet render previews;
- mesh metrics and warning tables.

## Validation Input

Input:

```text
code/test_assets/patent_sketches/usd247201s_sport_shoe/views/right_side_fig4_clean.png
```

Settings:

- Input path: `direct`
- Backend: `hunyuan3d`
- Octree resolution: `256`
- Seed: `12345`

## Smoke Test: Hunyuan Steps 5

Run id:

```text
ui_20260505_214712
```

Status: passed.

Outputs:

- Mesh: `code/outputs/pipeline_runs/ui_20260505_214712/hunyuan3d/direct_sketch/result/mesh.glb`
- Summary: `code/outputs/pipeline_runs/ui_20260505_214712/reports/summary.json`

Runtime:

- Hunyuan3D command elapsed time from UI status: `61.8 s`

Mesh metrics:

- Geometry count: `1`
- Vertices: `132920`
- Faces: `265836`
- Connected components: `6`
- Bounds dimensions: `[1.997896, 0.754515, 1.136305]`
- Thickness proxy ratio: `0.377655`
- Surface area: `6.333801`
- Volume: `n/a`

Warnings:

- `non_watertight_mesh`
- `internal_structure_not_validated`

Interpretation:

- The UI backend path is functional.
- A 5-step run is suitable as a fast interaction smoke test but not a quality baseline.

## Formal UI Sample: Hunyuan Steps 30

Run id:

```text
ui_20260505_214848
```

Status: passed.

Outputs:

- Mesh: `code/outputs/pipeline_runs/ui_20260505_214848/hunyuan3d/direct_sketch/result/mesh.glb`
- Summary: `code/outputs/pipeline_runs/ui_20260505_214848/reports/summary.json`

Runtime:

- Hunyuan3D command elapsed time from UI status: `65.5 s`

Mesh metrics:

- Geometry count: `1`
- Vertices: `96774`
- Faces: `193544`
- Connected components: `1`
- Bounds dimensions: `[1.993879, 0.728017, 0.722295]`
- Thickness proxy ratio: `0.362256`
- Surface area: `4.645912`
- Volume: `0.571747`

Warnings:

- `internal_structure_not_validated`

Interpretation:

- Phase 7B passes for single-view direct Hunyuan3D-2mini UI operation.
- The 30-step result is the better current candidate for demo and paper evidence.
- The hidden/internal shoe-structure limitation remains explicitly reported and should stay in the thesis discussion.

## Incident Note

One earlier UI-wrapper attempt created partial output under `ui_20260505_214258` and then WSL returned `Wsl/Service/E_UNEXPECTED`. After `wsl --shutdown`, WSL recovered and subsequent CLI/UI-wrapper runs passed.

That partial run is not treated as an accepted validation sample.

## Phase 7B Decision

Phase 7B passed for the current single-view MVP route.

Accepted demo route:

```text
single-view sketch -> direct -> Hunyuan3D-2mini -> GLB + mesh report -> Gradio display
```

Recommended next step:

- Move to Phase 8A: collect and freeze paper/demo evaluation samples.
- Keep Phase 6 geometry-changing cleanup optional until after visual comparison, because automatic cleanup may damage shoe design details.
