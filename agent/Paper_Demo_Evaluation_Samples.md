# Paper/Demo Evaluation Samples

Date: 2026-05-06

## Goal

Freeze a small, reproducible evidence set for the thesis and demo based on the current accepted MVP route.

This phase does not introduce new model work. It organizes existing validated outputs so screenshots, metric tables, and defense demo claims all refer to the same artifacts.

## Frozen Sample Set

The sample index is stored in:

- `paper/evaluation_samples/README.md`
- `paper/evaluation_samples/phase8a_metrics.csv`
- `paper/evaluation_samples/phase8a_manifest.json`

The generated artifacts remain under `code/outputs/`, which is ignored by Git.

## Samples

### S1 - Main UI Hunyuan3D Sample

Purpose:

- Primary demo sample for the current system.
- Shows the accepted Gradio route using Hunyuan3D-2mini.

Run:

- `ui_20260505_214848`

Input:

- `code/outputs/ui_uploads/ui_20260505_214848/input.png`

Outputs:

- Normalized image: `code/outputs/pipeline_runs/ui_20260505_214848/preprocess/input_normalized.png`
- Canny map: `code/outputs/pipeline_runs/ui_20260505_214848/preprocess/input_canny_control.png`
- Mesh: `code/outputs/pipeline_runs/ui_20260505_214848/hunyuan3d/direct_sketch/result/mesh.glb`
- Summary: `code/outputs/pipeline_runs/ui_20260505_214848/reports/summary.json`

Metrics:

- Backend: Hunyuan3D-2mini
- Path: direct
- Vertices: `96774`
- Faces: `193544`
- Connected components: `1`
- Bounds dimensions: `[1.993879, 0.728017, 0.722295]`
- Thickness proxy ratio: `0.362256`
- Watertight: yes
- Volume: `0.571747`
- Runtime from CLI command: about `65.5 s`
- Peak VRAM from Hunyuan runner: `4436.453 MB`

Warnings:

- `internal_structure_not_validated`

### S2 - ControlNet Render to Hunyuan3D

Purpose:

- Shows the sketch-domain-adaptation route before Hunyuan3D reconstruction.
- Useful for explaining why ControlNet remains part of the architecture even though the UI acceptance sample used the direct path.

Run:

- `phase5d_cli_hunyuan2mini_direct_render_offline`

Input:

- `code/outputs/controlnet_render/usd247201s_sport_shoe/right_side_canny_render_seed115.png`

Outputs:

- Mesh: `code/outputs/pipeline_runs/phase5d_cli_hunyuan2mini_direct_render_offline/hunyuan3d/direct_sketch/result/mesh.glb`
- Summary: `code/outputs/pipeline_runs/phase5d_cli_hunyuan2mini_direct_render_offline/reports/summary.json`

Metrics:

- Backend: Hunyuan3D-2mini
- Path: direct from ControlNet render
- Vertices: `117700`
- Faces: `235396`
- Connected components: `1`
- Bounds dimensions: `[1.996246, 0.729503, 0.621695]`
- Thickness proxy ratio: `0.311432`
- Watertight: yes
- Volume: `0.357143`
- Runtime from CLI command: about `67.1 s`
- Peak VRAM from Hunyuan runner: `4436.453 MB`

Warnings:

- `internal_structure_not_validated`

### S3 - SF3D Direct Baseline

Purpose:

- Baseline comparison for direct sketch/image input.

Run:

- `phase4_cli_smoke_patent_side`

Input:

- `code/outputs/pipeline_runs/phase4_cli_smoke_patent_side/preprocess/right_side_fig4_clean_normalized.png`

Output:

- `code/outputs/pipeline_runs/phase4_cli_smoke_patent_side/sf3d/direct_sketch/0/mesh.glb`

Metrics:

- Backend: SF3D
- Path: direct
- Vertices: `6866`
- Faces: `11536`
- Bounds dimensions: approximately `[0.962311, 0.319453, 0.146011]`
- Thickness proxy ratio: approximately `0.151731`
- Runtime from CLI command: about `21.9 s`
- Peak VRAM from SF3D stdout: `6171.602 MB`

Notes:

- This is a legacy Phase 4 report and does not include the newer connected-component and watertight fields.

### S4 - SF3D ControlNet Baseline

Purpose:

- Baseline comparison for ControlNet-rendered input.

Run:

- `phase4_cli_smoke_patent_side`

Input:

- `code/outputs/pipeline_runs/phase4_cli_smoke_patent_side/controlnet/render.png`

Output:

- `code/outputs/pipeline_runs/phase4_cli_smoke_patent_side/sf3d/controlnet_render/0/mesh.glb`

Metrics:

- Backend: SF3D
- Path: ControlNet render
- Vertices: `12087`
- Faces: `18860`
- Bounds dimensions: approximately `[0.959802, 0.355144, 0.334904]`
- Thickness proxy ratio: approximately `0.348921`
- Runtime from CLI command: about `23.2 s`
- Peak VRAM from SF3D stdout: `6171.811 MB`

Notes:

- This sample supports the claim that ControlNet-rendered input can give SF3D a fuller geometry than direct line-art input.

## Interpretation for Thesis/Demo

Current claims supported by these samples:

- The full local pipeline can produce inspectable GLB output on an RTX 4060 Laptop GPU with 8GB VRAM.
- Hunyuan3D-2mini is the current preferred backend for the demo because it passed the Gradio route and produces denser, watertight mesh reports in the accepted samples.
- SF3D remains a useful baseline and fallback, especially for comparing direct sketch input against ControlNet-rendered input.
- ControlNet remains useful as a sketch-domain adaptation layer, even if the first accepted UI route uses direct Hunyuan3D input.
- Internal shoe structure is not solved. It should be documented as a hidden-geometry limitation rather than overclaimed as CAD-level reconstruction.

## Phase 8A Decision

Phase 8A sample freezing is locally complete.

Recommended next step:

- Produce paper-ready screenshots from S1-S4:
  - input image;
  - normalized/Canny/control image;
  - optional ControlNet render;
  - generated GLB preview screenshot;
  - metrics table.
- After visual screenshots are captured, decide whether Phase 6 optional cleanup is needed for display quality.
