# Paper Screenshot Assets

Date: 2026-05-06

## Goal

Generate paper/demo-ready visual assets from the frozen Phase 8A evaluation sample set.

This phase uses existing outputs only. It does not rerun ControlNet, SF3D, or Hunyuan3D inference.

## Implementation

Added script:

- `paper/evaluation_samples/generate_phase8b_assets.py`

Generated assets:

- `paper/evaluation_samples/screenshots/phase8b_comparison_grid.png`
- `paper/evaluation_samples/screenshots/phase8b_metrics_table.png`
- `paper/evaluation_samples/screenshots/phase8b_s1_sample_sheet.png`
- `paper/evaluation_samples/screenshots/phase8b_s1_mesh_preview.png`
- `paper/evaluation_samples/screenshots/phase8b_s2_sample_sheet.png`
- `paper/evaluation_samples/screenshots/phase8b_s2_mesh_preview.png`
- `paper/evaluation_samples/screenshots/phase8b_s3_sample_sheet.png`
- `paper/evaluation_samples/screenshots/phase8b_s3_mesh_preview.png`
- `paper/evaluation_samples/screenshots/phase8b_s4_sample_sheet.png`
- `paper/evaluation_samples/screenshots/phase8b_s4_mesh_preview.png`
- `paper/evaluation_samples/screenshots/phase8b_screenshot_index.json`
- `paper/evaluation_samples/screenshots/README.md`

## Method

Input and preprocessing images are composed with `PIL`.

GLB previews are generated offline using:

- `trimesh`
- `numpy`
- `PIL`

The preview renderer uses a simple orthographic projection with face-depth sorting and basic directional shading. It is suitable for thesis figures and comparison sheets, but it is not a physically based renderer.

## Asset Dimensions

| Asset Type | Dimensions |
| --- | --- |
| Sample sheets | `1600 x 1120` |
| Standalone mesh previews | `1200 x 860` |
| Comparison grid | `1600 x 1420` |
| Metrics table | `1245 x 370` |

## Validation

Generated file count:

- `10` PNG assets
- `1` JSON index
- `1` screenshot README

All PNG files were opened with `PIL` to confirm dimensions and file integrity.

## Recommended Thesis Usage

- Use `phase8b_s1_sample_sheet.png` as the main result figure for the accepted UI route.
- Use `phase8b_comparison_grid.png` to compare Hunyuan3D-2mini and SF3D baselines.
- Use `phase8b_metrics_table.png` as the quantitative result table figure.
- Use standalone mesh previews when a larger 3D result image is needed.

## Phase 8B Decision

Phase 8B is locally complete.

Recommended next step:

- Review the generated PNGs visually.
- If the mesh preview angle is acceptable, proceed to paper text/evaluation writing.
- If a higher-fidelity 3D render is required, capture manual screenshots from Gradio/Blender later, using these offline previews as stable placeholders.
