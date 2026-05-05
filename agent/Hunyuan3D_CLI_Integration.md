# Hunyuan3D CLI Integration

Date: 2026-05-05

## Goal

Promote the validated Hunyuan3D-2mini shape-only path into the main CLI MVP while preserving SF3D as a baseline and fallback backend.

This step does not start the Gradio UI yet. It only stabilizes the command-line pipeline so the later UI can call one backend-agnostic entry point.

## Implementation

Updated:

- `code/pipeline/cli_mvp.py`

New CLI behavior:

- `--backend hunyuan3d` is now the default 3D reconstruction backend.
- `--backend sf3d` keeps the previous SF3D route available.
- `--backend both` can run both backends for comparison.
- `--mode direct`, `--mode controlnet`, and `--mode both` now describe which input path is reconstructed:
  - `direct`: normalized sketch or render image;
  - `controlnet`: ControlNet render;
  - `both`: both paths.
- Hunyuan3D output is written under `hunyuan3d/<input_path_name>/result/mesh.glb`.
- SF3D output remains under `sf3d/<input_path_name>/0/mesh.glb`.
- The CLI writes mesh reports for every generated GLB.

The Hunyuan3D subprocess sets:

```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
HF_HUB_OFFLINE=1
```

Reason:

- `expandable_segments` reduces CUDA allocation fragmentation risk.
- `HF_HUB_OFFLINE=1` prevents the already cached Hunyuan3D-2mini run from stalling on network/cache checks, especially after interrupted Hunyuan3D-2mv downloads.

The CLI summary now stores command output tails instead of full stdout/stderr. This keeps `reports/summary.json` readable and suitable for later Gradio display.

## Smoke Test

Command:

```bash
source /home/anker/miniforge3/etc/profile.d/conda.sh
conda activate trellis310
cd /mnt/d/Final_Project
python code/pipeline/cli_mvp.py \
  code/outputs/controlnet_render/usd247201s_sport_shoe/right_side_canny_render_seed115.png \
  --run-id phase5d_cli_hunyuan2mini_direct_render_offline \
  --mode direct \
  --backend hunyuan3d \
  --hunyuan-steps 30 \
  --hunyuan-octree-resolution 256 \
  --hunyuan-seed 12345
```

Result:

- Status: passed.
- Output directory: `code/outputs/pipeline_runs/phase5d_cli_hunyuan2mini_direct_render_offline/`
- Output mesh: `code/outputs/pipeline_runs/phase5d_cli_hunyuan2mini_direct_render_offline/hunyuan3d/direct_sketch/result/mesh.glb`
- Summary: `code/outputs/pipeline_runs/phase5d_cli_hunyuan2mini_direct_render_offline/reports/summary.json`
- Mesh report: `code/outputs/pipeline_runs/phase5d_cli_hunyuan2mini_direct_render_offline/reports/mesh_report.json`

Runtime:

- CLI command elapsed time: about `67.075 s`.
- Hunyuan3D model load time inside runner: about `23.879 s`.
- Hunyuan3D inference time inside runner: about `27.778 s`.
- Peak CUDA memory: `4436.453 MB`.

Mesh report:

- Valid GLB: yes.
- Geometry count: `1`.
- Vertices: `117700`.
- Faces: `235396`.
- Watertight: yes.
- Connected components: `1`.
- Bounds dimensions: `[1.996246, 0.729503, 0.621695]`.
- Thickness proxy ratio: `0.311432`.
- Volume: `0.357143`.

Warnings:

- `internal_structure_not_validated`

## Notes

Two earlier combined CLI attempts stalled while interrupted Hunyuan3D-2mv cache locks and incomplete blobs were still present. The stale 2mv lock and incomplete files were removed; the validated Hunyuan3D-2mini path now runs from the local cache in offline mode.

The tested input for this integration step was an existing ControlNet-rendered shoe image passed through `--mode direct`. This isolates Hunyuan3D backend integration. A full `--mode controlnet --backend hunyuan3d` smoke test should be run after the UI/progress layer is prepared, because it is longer and mixes two heavy inference stages.

## Phase 5D Decision

Phase 5D passed at the CLI backend-integration level.

Project route impact:

- Hunyuan3D-2mini is now the default CLI shape backend.
- SF3D remains available for baseline comparison and fallback.
- Hunyuan3D-2mv remains pending or cloud-assisted and should not block Phase 6/7 MVP work.

Recommended next step:

- Start the Gradio UI only after review of this stable CLI integration checkpoint.
