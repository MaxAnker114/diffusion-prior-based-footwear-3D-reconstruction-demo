# SF3D Baseline Evaluation

Date: 2026-05-04

## Goal

Evaluate whether Stable Fast 3D can run locally in WSL on the RTX 4060 Laptop GPU with 8GB VRAM and export a usable GLB.

## Environment

- Runtime: WSL Ubuntu
- Conda environment: `sf3d`
- Python: 3.10
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU
- VRAM: 8188 MiB
- PyTorch: `torch 2.4.0+cu118`
- Torchvision: `torchvision 0.19.0+cu118`
- SF3D source: `code/third_party/stable-fast-3d`

`code/third_party/` and `code/outputs/` are intentionally ignored by Git.

## Installation Notes

The official SF3D dependencies installed successfully, but `texture_baker` initially built as CPU-only because `nvcc` was unavailable in the conda environment.

Required fixes:

- Installed CUDA 11.8 compiler/development components in the `sf3d` environment.
- Installed GCC/G++ 11 for CUDA 11.8 compatibility.
- Installed CUDA dev headers required by PyTorch CUDA extension compilation:
  - `libcusparse-dev`
  - `libcublas-dev`
  - `libcusolver-dev`
  - `libcurand-dev`
  - `libcufft-dev`
- Rebuilt `texture_baker` with CUDA support.

## Hugging Face Access

The `stabilityai/stable-fast-3d` model is gated.

Access check result:

- `huggingface-cli whoami` returned the expected user.
- `huggingface-cli download stabilityai/stable-fast-3d config.yaml` succeeded after login.

No Hugging Face token is stored in this repository.

## Smoke Test

Command:

```bash
python run.py demo_files/examples/chair1.png \
  --output-dir /mnt/d/Final_Project/code/outputs/sf3d_smoke \
  --texture-resolution 512 \
  --remesh_option none \
  --batch_size 1
```

Result:

- Inference completed successfully.
- SF3D reported peak GPU memory: `6171.84375 MB`.
- Output GLB: `code/outputs/sf3d_smoke/0/mesh.glb`
- Output GLB size: `737968 bytes`

`trimesh` validation:

- Loaded as `Scene`
- Geometry count: `1`
- Vertices: `12858`
- Faces: `20000`

## Shoe-Specific Test

Input:

- File: `code/test_assets/worn_shoe_commons.png`
- Source page: https://commons.wikimedia.org/wiki/File:Worn_Shoe.png
- License: CC0 1.0 Universal / Public Domain Dedication

Command:

```bash
python run.py /mnt/d/Final_Project/code/test_assets/worn_shoe_commons.png \
  --output-dir /mnt/d/Final_Project/code/outputs/sf3d_worn_shoe \
  --texture-resolution 512 \
  --remesh_option none \
  --batch_size 1
```

Result:

- Inference completed successfully.
- SF3D reported peak GPU memory: `6172.10009765625 MB`.
- Output GLB: `code/outputs/sf3d_worn_shoe/0/mesh.glb`
- Output GLB size: `1049856 bytes`

`trimesh` validation:

- Loaded as `Scene`
- Geometry count: `1`
- Vertices: `18572`
- Faces: `28956`
- Bounds: `[[-0.48638999462127686, -0.33011168241500854, -0.350563645362854], [0.40707024931907654, 0.4387977123260498, 0.24115651845932007]]`

## Baseline Status

Passed for technical feasibility:

- SF3D environment: passed
- Hugging Face gated access: passed
- CUDA extension issue: fixed
- Official sample GLB export: passed
- Public shoe image GLB export: passed
- 8GB VRAM feasibility: passed for both the sample test and the shoe-specific test

Remaining quality work:

- Test more shoe categories and viewpoints.
- Visually inspect generated GLB outputs in the later UI/viewer phase.
- Compare direct shoe image input against ControlNet-adapted sketch/render input.

## Recommended Next Action

Proceed to ControlNet sketch-domain adaptation, then compare direct SF3D input against ControlNet-rendered input.
