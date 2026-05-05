# System Architecture

## Project Summary

Project name: diffusion-prior-based footwear 3D reconstruction demo.

Core goal: build a local research demo that reconstructs a shoe 3D model from a single-view or three-view designer shoe sketch. The first deliverable must run on the current RTX 4060 Laptop GPU with 8GB VRAM, export a usable GLB/OBJ mesh, and provide an inspectable UI for the graduation project.

The formal project input is a designer sketch, not a general product photo. Product photos may still be used as baseline smoke-test inputs for validating image-to-3D backends, but they do not represent the final task setting.

The project route is updated from a TRELLIS-dominant pipeline to:

1. **ControlNet sketch-domain adaptation**: convert single-view or three-view designer shoe sketches into more model-friendly rendered shoe images.
2. **Hunyuan3D-2mini / Hunyuan3D-2mv shape generation**: preferred reconstruction direction after Phase 5B visual review.
3. **Stable Fast 3D (SF3D) baseline**: stable comparison/fallback backend for single-image-to-GLB generation.

TRELLIS is no longer the primary runtime path because local testing showed that the official `microsoft/TRELLIS-image-large` pipeline can load and produce Gaussian output on 8GB VRAM, but mesh extraction runs out of memory.

## Verified Local Constraints

- Main runtime environment: WSL Ubuntu.
- Python environment: `trellis310`, Python 3.10.
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU, 8GB VRAM.
- PyTorch stack verified: `torch 2.4.0+cu118`, `torchvision 0.19.0+cu118`.
- `xformers==0.0.27.post2` import and CUDA attention smoke test passed.
- `StableDiffusionControlNetPipeline` minimal import passed.
- TRELLIS import passed, but TRELLIS mesh generation is not reliable on this GPU.
- SF3D baseline has generated readable GLB output from an official sample and a public shoe image within the 8GB VRAM limit.

## User Review Findings

- Future tests should use single-view or three-view designer shoe sketches as the primary input type.
- The SF3D product-image baseline is visually acceptable for exterior shoe shape, but it does not reliably reconstruct reasonable internal shoe structure.
- The Hunyuan3D-2mini shape-only output was manually reviewed and judged clearly better than the earlier SF3D output for the footwear case.
- Internal shoe structure is a core technical difficulty because it involves invisible geometry completion from limited visual evidence.
- The paper and demo should present internal structure as a limitation/research challenge, not as a solved capability of the MVP.

## Key References

- Stable Fast 3D official repo: https://github.com/Stability-AI/stable-fast-3d
- Hunyuan3D-2 official repo: https://github.com/Tencent-Hunyuan/Hunyuan3D-2
- Hunyuan3D-2.1 official repo: https://github.com/tencent-hunyuan/hunyuan3d-2.1
- Diffusers ControlNet API: https://huggingface.co/docs/diffusers/api/pipelines/controlnet
- Gradio Model3D API: https://www.gradio.app/docs/gradio/model3d
- TRELLIS official repo, retained as experimental reference: https://github.com/microsoft/TRELLIS

## System Overview

### 1. Web UI Layer

Recommended first implementation: Gradio Blocks.

Inputs:

- Single-view designer shoe sketch.
- Optional three-view input: front, side, top or outsole view.
- Prompt and negative prompt fields for ControlNet rendering.
- Backend selector: `sf3d`, `hunyuan3d_candidate`, `trellis_experimental`.

Outputs:

- Preprocessed control image.
- Generated or normalized shoe render.
- Final 3D model preview via `gradio.Model3D`.
- Export files: GLB as the default, OBJ as optional.

### 2. Sketch and View Preprocessing Layer

Responsibilities:

- Normalize uploaded shoe sketches to consistent background, crop, aspect ratio, and resolution.
- Convert designer sketches to Canny or scribble control maps.
- For three-view input, keep each view independently inspectable and prepare a fused prompt/context package for downstream models.

This layer is important because the graduation topic focuses on single-view and multi-view shoe reconstruction. Even if the first baseline model is single-image-to-3D, the UI and data structure should already preserve the three-view path.

### 3. ControlNet Adaptation Layer

Primary purpose: reduce the domain gap between hand-drawn shoe sketches and image-to-3D models trained mostly on rendered or natural images.

Recommended modes:

- Canny ControlNet for clean product edges.
- Scribble ControlNet for rough hand-drawn sketches.
- Optional depth/normal ControlNet only after the baseline is stable.

Output:

- A clean shoe render suitable for SF3D or Hunyuan3D input.
- The original sketch remains available for comparison and evaluation.

### 4. 3D Reconstruction Layer

#### Preferred Shape Backend: Hunyuan3D-2mini / Hunyuan3D-2mv

Role:

- Convert ControlNet-rendered shoe images, and later multi-view shoe references, into shape meshes.
- Use Hunyuan3D-2mini as the current preferred local shape-generation backend.
- Evaluate Hunyuan3D-2mv for the thesis-aligned three-view branch.

Reasoning:

- Hunyuan3D-2mini passed local shape-only inference on the RTX 4060 Laptop GPU with about `4436 MB` peak CUDA memory.
- Human visual review judged the Hunyuan3D-2mini GLB clearly better than the earlier SF3D result for the footwear case.
- Hunyuan3D-2mv is conceptually better aligned with the single-view/three-view designer sketch project goal.

Risks:

- Texture generation remains disabled until shape generation and multi-view feasibility are stable.
- Hunyuan3D-2mv may still exceed the practical 8GB VRAM budget depending on settings.
- Hunyuan3D-2.1 remains a cloud/fine-tuning research candidate rather than a local MVP backend.

#### Stable Baseline: SF3D

Role:

- Preserve a stable single-image-to-GLB comparison backend.
- Keep a fallback route if Hunyuan3D multi-view testing becomes unstable.

Reasoning:

- SF3D already generated readable GLB outputs locally within the 8GB VRAM limit.
- SF3D remains useful for baseline tables and pipeline regression checks.

Risks:

- SF3D can produce plausible exterior shape from shoe images, but internal shoe structure may be geometrically unreasonable because single-view image-to-3D cannot observe hidden regions.
- It is no longer the preferred shape backend after Phase 5B visual review.

Current Phase 5A decision:

- Test Hunyuan3D-2mini first as the low-parameter local shape-only candidate.
- Test Hunyuan3D-2mv second because it best matches the three-view shoe-sketch direction.
- Keep Hunyuan3D-2.1 as a cloud/fine-tuning research candidate rather than the next local install target.
- Do not enable Hunyuan texture generation until shape-only inference is stable on the current GPU.

Current Phase 5B result:

- Hunyuan3D-2mini shape-only inference is locally feasible on the RTX 4060 Laptop GPU.
- The first smoke test used about `4436 MB` peak CUDA memory and exported a valid watertight GLB.
- Human visual review judged the Hunyuan3D-2mini output clearly better than the earlier SF3D output.
- Hunyuan3D-2mini is now the current preferred shape-generation backend.
- Hunyuan3D-2mv is the next logical candidate for the multi-view branch, but Phase 5C did not validate it locally yet.

Current Phase 5C result:

- Hunyuan3D-2mv standard failed before inference/mesh export on the current local machine.
- Hunyuan3D-2mv turbo could not be tested because the large model download did not complete in the current session.
- Hunyuan3D-2mv remains a pending or cloud-assisted research path, not a blocker for the MVP.

#### Experimental Backend: TRELLIS

Role:

- Keep as a comparison model or high-VRAM optional backend.
- Do not block the MVP on TRELLIS mesh export.

Verified local result:

- Import and low-step Gaussian generation passed.
- Mesh extraction failed with CUDA out-of-memory on 8GB VRAM.

### 5. Geometry Post-processing Layer

Tools:

- `trimesh`
- `open3d`
- Optional mesh repair/remesh tools if required by SF3D/Hunyuan3D outputs.

Responsibilities:

- Load generated GLB/OBJ.
- Generate a non-destructive mesh report for paper evidence and later UI display.
- Record geometry count, vertices, faces, bounds, dimensions, thickness proxy, surface area, watertight status, volume availability, and connected components.
- Emit structured warnings for thin geometry, many fragments, non-watertight outputs, and internal-structure uncertainty.
- Apply conservative smoothing, decimation, and mesh cleanup.
- Preserve shoe silhouette and important design details.
- Export GLB for UI preview and OBJ for optional downstream inspection.
- Detect and report obvious mesh issues such as empty geometry, broken exports, or extreme internal artifacts when possible.

Current implementation:

- `code/postprocess/mesh_report.py` implements the non-destructive reporting portion.
- The report does not modify mesh geometry.
- The report can indicate suspicious proxy signals, but it cannot automatically prove whether shoe interiors are anatomically or structurally correct.
- Geometry-changing smoothing/cleanup remains an optional later step and should be compared against the original GLB before becoming a default.

Non-goal for MVP:

- Full CAD/NURBS parameterization. This is too risky for the current schedule and hardware. It can be described as future work in the paper.

## Data Flow

### Single-view MVP Flow

1. User uploads one designer shoe sketch.
2. Preprocessing normalizes crop, background, and control map.
3. ControlNet optionally generates a clean shoe render.
4. Hunyuan3D-2mini generates the preferred shape GLB; SF3D remains available as baseline/fallback.
5. Post-processing cleans and smooths the mesh.
6. UI displays the render and 3D model.

### Three-view Research Flow

1. User uploads three shoe views.
2. Each view is preprocessed and converted into a control map.
3. ControlNet generates consistent rendered views or normalized references.
4. Hunyuan3D-2mv is evaluated for multi-view shape generation.
5. If Hunyuan3D-2mv is not feasible locally, three-view support remains a data/evaluation module while Hunyuan3D-2mini uses the best ControlNet-rendered side/profile view as the preferred local backend.

## Evaluation Plan

Metrics and qualitative checks:

- Mesh loads successfully in the browser.
- GLB/OBJ export integrity.
- Shoe silhouette consistency with input sketch/view.
- Visual plausibility of upper, sole, heel, toe box, and outsole shape.
- Explicit review of internal shoe geometry and hidden-region artifacts.
- If ground-truth meshes become available: Chamfer Distance and normal consistency.
- Runtime and peak VRAM per backend.

## Non-Functional Requirements

- Local-first inference by default.
- WSL as the main ML runtime.
- Clear progress states and error messages.
- Backend failure must not crash the UI; errors should be shown to the user.
- Every major phase requires human review before continuing.

## Current Open Decisions

- Whether to retry Hunyuan3D-2mv locally after completing the turbo checkpoint download, or move it to cloud-assisted evaluation.
- Whether the first UI supports three-view upload immediately or starts with single-view and adds three-view in the next phase.
- How much shoe-specific dataset preparation is expected for the graduation deliverable.
- How to define an acceptable internal-structure quality threshold for the MVP.
