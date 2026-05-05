# Hunyuan3D-2mini Smoke Test

Date: 2026-05-05

## Goal

Create an isolated WSL conda environment for Hunyuan3D-2 and run the first local Hunyuan3D-2mini shape-only smoke test.

This phase intentionally avoids texture generation and does not modify the existing `sf3d` or `trellis310` environments.

## Environment

- Environment name: `hunyuan3d`
- Python: `3.10.20`
- PyTorch: `2.4.0+cu118`
- Torchvision: `0.19.0+cu118`
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU
- Available VRAM: about `8187.5 MB`
- Hunyuan3D source checkout: `code/third_party/Hunyuan3D-2`
- Hunyuan3D source commit: `f8db630`
- Hunyuan model: `tencent/Hunyuan3D-2mini`
- Subfolder: `hunyuan3d-dit-v2-mini`
- Variant: `fp16`

## Implementation

Added a reusable shape-only runner:

- `code/reconstruction/run_hunyuan3d_shape.py`

The runner:

- loads one input image;
- loads `Hunyuan3DDiTFlowMatchingPipeline`;
- runs shape-only inference;
- exports GLB;
- records runtime and peak CUDA memory;
- generates a mesh report using `code/postprocess/mesh_report.py`.

It does not load `Hunyuan3DPaintPipeline`.

## Commands

Environment setup:

```bash
source /home/anker/miniforge3/etc/profile.d/conda.sh
conda create -y -n hunyuan3d python=3.10
conda activate hunyuan3d
conda install -y pip
python -m pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu118
cd /mnt/d/Final_Project/code/third_party/Hunyuan3D-2
python -m pip install -r requirements.txt
python -m pip install -e .
conda install -y -c conda-forge libopengl
```

Smoke test:

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

## Smoke Test Result

Status: passed.

Input:

- `code/outputs/controlnet_render/usd247201s_sport_shoe/right_side_canny_render_seed115.png`

Output:

- `code/outputs/hunyuan3d_runs/phase5b_hunyuan2mini_patent_render/mesh.glb`

Reports:

- `code/outputs/hunyuan3d_runs/phase5b_hunyuan2mini_patent_render/reports/summary.json`
- `code/outputs/hunyuan3d_runs/phase5b_hunyuan2mini_patent_render/reports/mesh_report.json`

Runtime:

- First-run model download + load: `741.299 s`
- Inference after loading: `30.967 s`
- Peak CUDA memory: `4436.453 MB`

Mesh report:

- Valid GLB: yes
- Scene type: `Scene`
- Geometry count: `1`
- Vertices: `117700`
- Faces: `235396`
- Connected components: `1`
- Watertight: yes
- Bounds dimensions: `[1.996246, 0.729503, 0.621695]`
- Thickness proxy ratio: `0.311432`
- Surface area: `5.61856`
- Volume: `0.357143`

Warnings:

- `internal_structure_not_validated`

## Interpretation

Hunyuan3D-2mini is locally feasible for shape-only inference on the current 8GB GPU.

Compared with the earlier SF3D outputs, this first Hunyuan3D-2mini result is notable because:

- peak memory is lower than SF3D's observed approximately 6.17GB peak;
- the mesh is watertight;
- the mesh has a single connected component;
- the face count is much higher, so later UI display may require decimation or a lower-resolution export option.

This result does not prove that Hunyuan3D-2mini is visually superior for footwear. It only proves that the local shape-only path is technically viable and worth deeper comparison.

## Human Visual Review

User review result:

- The generated Hunyuan3D-2mini GLB was visually inspected by the project owner.
- The result is judged to be clearly better than the earlier SF3D output for the footwear case.

Implication:

- Hunyuan3D-2mini should be promoted from a research-only candidate to the current preferred shape-generation backend.
- SF3D should remain as a stable baseline/comparison backend, especially for textured GLB comparison and fallback.
- The next Hunyuan test should be Hunyuan3D-2mv, because it is more aligned with the project's single-view/three-view designer sketch target.
- Texture generation should remain disabled until shape generation and multi-view feasibility are stable.

## Known Issues

`pymeshlab` still prints plugin warnings about `libOpenGL.so.0` during shapegen import. Installing `libopengl` into the conda environment did not remove the warnings in this shell session.

Impact:

- Hunyuan3D shapegen import: not blocked.
- Hunyuan3D-2mini inference: not blocked.
- GLB export: not blocked.
- `trimesh` mesh report: not blocked.

Recommendation:

- Treat this as a non-blocking environment warning for now.
- Revisit only if Phase 6 mesh cleanup needs `pymeshlab` filters that fail at runtime.

## Phase 5B Decision

Phase 5B passed.

Recommended next step:

- Test Hunyuan3D-2mv shape-only with a three-view or pseudo-three-view input set, because 2mv is more aligned with the thesis target.
