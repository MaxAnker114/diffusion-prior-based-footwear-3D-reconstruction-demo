# Diffusion-Prior-Based Footwear 3D Reconstruction Demo

A research-oriented demo for reconstructing 3D footwear models from single-view or multi-view shoe sketches/images.

The project is being developed as a graduation project. Its current priority is to build a reproducible local pipeline that can run on an RTX 4060 Laptop GPU with 8GB VRAM and export inspectable 3D assets such as GLB/OBJ files.

## Status

Current stage: Hunyuan3D-2mini CLI backend integration.

The original TRELLIS-first route has been revised after local VRAM testing. TRELLIS can be imported and can run limited Gaussian output on the current machine, but mesh extraction is not reliable within 8GB VRAM. The MVP route is now:

- **ControlNet** for sketch-to-render adaptation before 3D reconstruction.
- **Hunyuan3D-2mini** as the current preferred local shape-generation backend after visual review and CLI integration.
- **Hunyuan3D-2mv** as a pending multi-view candidate for the three-view shoe sketch path.
- **Stable Fast 3D (SF3D)** as a stable baseline/fallback backend.

## Goals

- Generate a usable 3D footwear model from a single-view shoe sketch or image.
- Preserve a path for three-view input and multi-view evaluation.
- Export GLB as the primary preview format, with OBJ support considered when useful.
- Build a local demo UI for inspection, comparison, and paper screenshots.
- Record model feasibility, runtime, VRAM usage, and reconstruction quality.

## Planned Pipeline

```text
Input shoe sketch/image
        |
        v
Preprocessing
  - crop and normalize
  - background cleanup
  - Canny/Scribble control map
        |
        v
ControlNet sketch-domain adaptation
        |
        v
Image-to-3D backend
  - Hunyuan3D-2mini preferred shape backend
  - Hunyuan3D-2mv pending multi-view candidate
  - SF3D baseline/fallback
  - TRELLIS experimental comparison
        |
        v
Mesh post-processing
  - diagnostics
  - optional cleanup/smoothing
  - GLB/OBJ export
        |
        v
Gradio demo and paper evaluation assets
```

## Repository Structure

```text
.
|-- agent/
|   |-- Dev_Plan.md
|   |-- System_Architecture.md
|   |-- Hunyuan3D_CLI_Integration.md
|-- code/
|   |-- README.md
|   |-- ui/
|-- paper/
|   |-- graduation midterm PDF and paper assets
|-- .gitattributes
|-- .gitignore
|-- README.md
```

## Key Documents

- [System Architecture](agent/System_Architecture.md)
- [Development Plan](agent/Dev_Plan.md)
- [Code Directory Notes](code/README.md)
- [Hunyuan3D CLI Integration](agent/Hunyuan3D_CLI_Integration.md)
- [Gradio UI MVP](agent/Gradio_UI_MVP.md)

## Hardware Target

- OS/runtime: WSL Ubuntu
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU
- VRAM: 8GB
- Python: 3.10
- PyTorch/CUDA stack: validated in the local WSL environment

## Development Notes

- The project proceeds through human-reviewed checkpoints.
- Before major changes, the last stable state should be committed.
- When a remote repository is configured, stable commits should be pushed to GitHub.
- Local virtual environments, model weights, cache files, logs, secrets, and third-party checkouts are intentionally excluded from Git.

## Roadmap

- [x] Validate WSL, Python, CUDA, PyTorch, xformers, TRELLIS import, and ControlNet import.
- [x] Revise the project route based on 8GB VRAM constraints.
- [x] Initialize Git and push the first stable planning baseline.
- [x] Evaluate Stable Fast 3D on a shoe image and verify GLB export.
- [x] Validate ControlNet sketch-to-render adaptation.
- [x] Build the CLI end-to-end MVP.
- [x] Add non-destructive mesh reporting for paper/UI metrics.
- [x] Complete Hunyuan3D pre-installation candidate evaluation.
- [x] Install and smoke-test Hunyuan3D-2mini shape-only inference.
- [x] Visually review Hunyuan3D-2mini output and promote it as the preferred shape backend.
- [x] Attempt Hunyuan3D-2mv shape-only inference and record local blockers.
- [x] Integrate Hunyuan3D-2mini into the CLI MVP as the default backend.
- [x] Build the first Gradio UI MVP around the CLI pipeline.
- [ ] Add optional geometry-changing mesh cleanup/post-processing.
- [ ] Prepare paper evaluation materials.

## Current Next Step

Review Phase 7A Gradio UI, then decide whether to add mesh cleanup controls or prepare paper evaluation runs.
