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

## Current Limitation

The local project does not yet contain a clean shoe image suitable for the SF3D shoe-specific test. Only the official SF3D sample image has been validated.

## Step 8 Status

Partial pass:

- SF3D environment: passed
- Hugging Face gated access: passed
- CUDA extension issue: fixed
- Official sample GLB export: passed
- 8GB VRAM feasibility: passed for the sample test
- Shoe image GLB test: pending input image

## Recommended Next Action

Provide or prepare one clean shoe image, preferably a side-view product image on a simple background, then run the same SF3D command to verify shoe-specific GLB output quality and VRAM usage.
