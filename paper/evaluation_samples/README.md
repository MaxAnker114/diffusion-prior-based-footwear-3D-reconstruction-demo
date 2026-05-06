# Phase 8A Evaluation Samples

Date: 2026-05-06

This folder records the frozen paper/demo evaluation sample set for the current MVP.

The actual generated images and GLB files are stored under `code/outputs/`, which is intentionally ignored by Git because these files are generated artifacts. This folder stores the sample manifest and metric table so the thesis/demo evidence can be reproduced and referenced consistently.

## Frozen Samples

| ID | Purpose | Source Run | Input | Output Mesh |
| --- | --- | --- | --- | --- |
| S1 | Main demo sample: patent side-view sketch to Hunyuan3D-2mini | `ui_20260505_214848` | `code/outputs/ui_uploads/ui_20260505_214848/input.png` | `code/outputs/pipeline_runs/ui_20260505_214848/hunyuan3d/direct_sketch/result/mesh.glb` |
| S2 | Sketch-domain adapted render to Hunyuan3D-2mini | `phase5d_cli_hunyuan2mini_direct_render_offline` | `code/outputs/controlnet_render/usd247201s_sport_shoe/right_side_canny_render_seed115.png` | `code/outputs/pipeline_runs/phase5d_cli_hunyuan2mini_direct_render_offline/hunyuan3d/direct_sketch/result/mesh.glb` |
| S3 | SF3D direct-sketch baseline | `phase4_cli_smoke_patent_side` | `code/outputs/pipeline_runs/phase4_cli_smoke_patent_side/preprocess/right_side_fig4_clean_normalized.png` | `code/outputs/pipeline_runs/phase4_cli_smoke_patent_side/sf3d/direct_sketch/0/mesh.glb` |
| S4 | SF3D ControlNet-render baseline | `phase4_cli_smoke_patent_side` | `code/outputs/pipeline_runs/phase4_cli_smoke_patent_side/controlnet/render.png` | `code/outputs/pipeline_runs/phase4_cli_smoke_patent_side/sf3d/controlnet_render/0/mesh.glb` |

## Metric Table

See:

- `phase8a_metrics.csv`
- `phase8a_manifest.json`

## Screenshot Assets

Phase 8B generated paper/demo-ready screenshots under:

- `screenshots/`

Recommended first figures:

- `screenshots/phase8b_s1_sample_sheet.png`
- `screenshots/phase8b_comparison_grid.png`
- `screenshots/phase8b_metrics_table.png`

## Thesis Notes

- S1 is the current main demo evidence because it runs through the Gradio UI route and uses Hunyuan3D-2mini as the preferred backend.
- S2 shows the ControlNet sketch-domain adaptation route before Hunyuan3D reconstruction.
- S3 and S4 are SF3D baselines for comparison.
- Internal shoe geometry remains an explicit limitation. The automatic mesh report can flag risks, but it cannot prove hidden internal structure correctness from a single exterior view.
