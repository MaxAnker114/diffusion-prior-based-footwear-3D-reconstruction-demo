# Code

This directory contains the project implementation modules, experiment utilities, and local test assets.

Planned and current modules:

- `preprocess/`: shoe sketch cropping, background cleanup, Canny/Scribble control map generation.
- `controlnet/`: 2D sketch-to-render adaptation before 3D reconstruction.
- `pipeline/`: command-line orchestration for the current MVP.
- `postprocess/`: non-destructive GLB/OBJ mesh reporting first; cleanup/smoothing will be added only after review.
- `reconstruction/`: reserved for future backend wrappers around SF3D and Hunyuan3D.
- `ui/`: reserved for the later Gradio demo.

`code/third_party/` is used for local third-party source checkouts such as Stable Fast 3D and is intentionally ignored by Git.

Runtime outputs are written under `code/outputs/` and are also ignored by Git.

## CLI MVP

Run from WSL:

```bash
source /home/anker/miniforge3/etc/profile.d/conda.sh
conda activate trellis310
cd /mnt/d/Final_Project
python code/pipeline/cli_mvp.py \
  code/test_assets/patent_sketches/usd247201s_sport_shoe/views/right_side_fig4_clean.png \
  --run-id phase4_cli_smoke_patent_side \
  --mode both \
  --controlnet-steps 8 \
  --texture-resolution 512
```

Modes:

- `direct`: normalized sketch -> SF3D.
- `controlnet`: sketch -> ControlNet render -> SF3D.
- `both`: run both paths and compare reports.

Each run writes:

- preprocessing outputs
- optional ControlNet render
- SF3D GLB output
- `reports/summary.json`
- `reports/mesh_report.json`

## Standalone Mesh Report

Generate a paper/UI-friendly mesh report for an existing GLB:

```bash
python code/postprocess/mesh_report.py \
  code/outputs/pipeline_runs/<run_id>/sf3d/direct_sketch/0/mesh.glb \
  --project-root /mnt/d/Final_Project \
  --output code/outputs/pipeline_runs/<run_id>/reports/direct_mesh_report_v2.json
```

The report is non-destructive. It records vertices, faces, bounds, dimensions, thickness proxy ratio, connected components, surface area, watertight status, reliable volume availability, and structured warnings.

## Hunyuan3D Shape-Only Runner

Run from WSL with the `hunyuan3d` environment active:

```bash
source /home/anker/miniforge3/etc/profile.d/conda.sh
conda activate hunyuan3d
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /mnt/d/Final_Project
python code/reconstruction/run_hunyuan3d_shape.py \
  code/outputs/controlnet_render/usd247201s_sport_shoe/right_side_canny_render_seed115.png \
  --run-id phase5b_hunyuan2mini_patent_render \
  --steps 30 \
  --octree-resolution 256 \
  --num-chunks 20000 \
  --seed 12345
```

The runner uses Hunyuan3D shape generation only. It does not load the texture pipeline.

For Hunyuan3D-2mv multi-view experiments, pass one or more named views:

```bash
python code/reconstruction/run_hunyuan3d_shape.py \
  --run-id phase5c_hunyuan2mv_patent_pseudo3view \
  --model-path tencent/Hunyuan3D-2mv \
  --subfolder hunyuan3d-dit-v2-mv \
  --variant fp16 \
  --steps 30 \
  --octree-resolution 256 \
  --num-chunks 20000 \
  --left code/test_assets/patent_sketches/usd247201s_sport_shoe/views/left_side_fig3_clean.png \
  --right code/test_assets/patent_sketches/usd247201s_sport_shoe/views/right_side_fig4_clean.png \
  --back code/test_assets/patent_sketches/usd247201s_sport_shoe/views/rear_fig5.png
```

Current note: Hunyuan3D-2mv has not passed local smoke testing yet on the current 8GB GPU.
