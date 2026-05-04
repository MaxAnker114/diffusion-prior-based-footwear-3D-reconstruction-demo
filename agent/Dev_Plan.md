# Dev Plan

## Step Policy

This project will proceed one checkpoint at a time. After each phase, I will stop and wait for your review before moving on.

The route is updated from a TRELLIS-dominant system to:

1. **SF3D baseline** for reliable local single-image-to-GLB delivery.
2. **Hunyuan3D fine-tune candidate** for research value and possible shoe-domain adaptation.
3. **ControlNet sketch-domain adaptation** to bridge sketch inputs and image-to-3D model expectations.

## Phase 0 - Documentation and Route Review

Status: in progress.

Goals:

- Update `System_Architecture.md` and `Dev_Plan.md`.
- Replace the TRELLIS-first plan with the SF3D + Hunyuan3D + ControlNet route.
- Keep TRELLIS only as an experimental/high-VRAM comparison backend.

Tasks:

- Record local environment findings.
- Record model selection rationale.
- Record risks from the 8GB VRAM constraint.
- Define the next implementation phases.

Tests:

- Manual review of the two Markdown files.

Human Checkpoint:

- You review this updated plan before we install or implement the next model backend.

## Phase 1 - Environment Baseline

Status: completed and verified.

Verified:

- WSL Ubuntu is the main ML runtime.
- Python environment `trellis310` uses Python 3.10.
- PyTorch CUDA stack works on the RTX 4060 Laptop GPU.
- `xformers==0.0.27.post2` imports and CUDA attention smoke test passes.
- TRELLIS imports under WSL.
- `StableDiffusionControlNetPipeline` minimal import passes.

Known issue:

- TRELLIS mesh extraction is not feasible as the primary path on the current 8GB VRAM GPU.

Human Checkpoint:

- Completed earlier. We are now revising the project route based on the findings.

## Phase 2 - SF3D Baseline Evaluation

Goal:

- Prove that Stable Fast 3D can generate a usable shoe GLB locally from a single image.

Tasks:

- Check access requirements for `stabilityai/stable-fast-3d`.
- Install SF3D into a clean WSL environment or a dedicated conda environment.
- Run SF3D on a simple sample image.
- Run SF3D on at least one shoe image.
- Export GLB and inspect it in a local viewer or Gradio `Model3D`.
- Record runtime, peak VRAM, and failure modes.

Tests:

- Import SF3D modules.
- Single sample inference smoke test.
- Shoe image inference smoke test.
- GLB file loads successfully.

Success criteria:

- A generated GLB can be opened and previewed.
- Peak VRAM stays within the RTX 4060 8GB limit.
- The output is good enough to serve as a baseline in the graduation demo.

Human Checkpoint:

- Stop after SF3D evaluation and ask for your review before integrating it into the project UI.

## Phase 3 - ControlNet Sketch-Domain Adaptation

Goal:

- Convert shoe sketches or three-view drawings into cleaner rendered shoe images that are easier for SF3D/Hunyuan3D to reconstruct.

Tasks:

- Decide first ControlNet mode: Canny or Scribble.
- Implement sketch preprocessing: crop, background cleanup, edge extraction, and resizing.
- Build a minimal ControlNet inference script.
- Test single-view sketch to rendered shoe image.
- Test three-view sketch normalization without forcing 3D generation yet.

Tests:

- `StableDiffusionControlNetPipeline` full initialization test.
- One local sketch-to-render inference.
- Compare original sketch, control map, and generated render.

Success criteria:

- Output render keeps the shoe silhouette and key features.
- Pipeline can run without breaking the SF3D environment.
- We have a clear prompt/control strategy for shoes.

Human Checkpoint:

- Stop after sketch-to-render validation and ask for your review.

## Phase 4 - End-to-End MVP Pipeline

Goal:

- Connect preprocessing, optional ControlNet rendering, SF3D reconstruction, post-processing, and GLB preview.

Tasks:

- Create project modules for:
  - image preprocessing
  - ControlNet rendering
  - SF3D reconstruction
  - mesh post-processing
  - export and file management
- Use SF3D as the default 3D backend.
- Add fallback behavior when ControlNet or SF3D fails.
- Save intermediate outputs for paper screenshots and debugging.

Tests:

- Single-view end-to-end CLI smoke test.
- Shoe sample end-to-end GLB generation.
- Verify intermediate image outputs are saved.
- Verify final GLB loads.

Success criteria:

- One command can convert an input shoe image/sketch into a GLB.
- Failure states are understandable and recoverable.

Human Checkpoint:

- Stop after CLI MVP and ask for your review before UI work.

## Phase 5 - Hunyuan3D Candidate Evaluation

Goal:

- Decide whether Hunyuan3D should become the fine-tuning/research branch of the project.

Candidate order:

1. `Hunyuan3D-2mini` for low VRAM local shape generation.
2. `Hunyuan3D-2mv` for three-view/multi-view alignment with the thesis topic.
3. `Hunyuan3D-2.1` for fine-tuning potential, if hardware or cloud resources permit.

Tasks:

- Install Hunyuan3D in a separate environment to avoid breaking SF3D.
- Run low-VRAM inference on one shoe image.
- If possible, test multi-view input with `Hunyuan3D-2mv`.
- Inspect whether training/fine-tuning scripts can be reduced to a small shoe-domain experiment.
- Decide local-only vs cloud-assisted fine-tuning.

Tests:

- Import Hunyuan3D modules.
- Shape-only inference smoke test.
- Optional texture generation test only if VRAM allows.
- Record VRAM and runtime.

Success criteria:

- We can clearly classify Hunyuan3D as one of:
  - local inference backend,
  - cloud fine-tuning candidate,
  - paper-only comparison/future-work model.

Human Checkpoint:

- Stop after Hunyuan3D feasibility report and ask for your review.

## Phase 6 - Mesh Post-processing

Goal:

- Improve generated mesh usability without destroying shoe design details.

Tasks:

- Load generated GLB/OBJ with `trimesh` or `open3d`.
- Apply conservative smoothing.
- Add optional decimation or mesh cleanup.
- Preserve original and processed outputs for comparison.
- Export final GLB as the UI default.

Tests:

- Compare before/after mesh visually.
- Verify final GLB still loads in browser.
- Ensure post-processing does not remove key shoe components.

Human Checkpoint:

- Stop after post-processing comparison and ask for your review.

## Phase 7 - Gradio UI Integration

Goal:

- Build the project demo UI after the core pipeline is stable.

Tasks:

- Build a focused Gradio Blocks app.
- Inputs:
  - single-view upload
  - optional three-view upload slots
  - prompt and backend settings
- Outputs:
  - control map
  - generated render
  - 3D model preview
  - export file links
- Add progress and readable error messages.
- Keep the UI academic, clear, and usable rather than purely decorative.

Tests:

- Local UI smoke test.
- Upload image, run pipeline, preview GLB.
- Verify UI does not crash on failed inference.

Human Checkpoint:

- Stop after UI integration and ask for final review.

## Phase 8 - Paper Support and Evaluation Materials

Goal:

- Produce evidence for the graduation paper and defense.

Tasks:

- Save input, control map, render, raw mesh, and processed mesh for each test case.
- Record runtime and peak VRAM.
- Prepare comparison table:
  - SF3D baseline
  - Hunyuan3D candidate result if feasible
  - TRELLIS experimental result if useful
- Summarize why full CAD/NURBS reconstruction is future work.

Tests:

- Confirm output artifacts are reproducible.
- Confirm screenshots and metrics match the written claims.

Human Checkpoint:

- Stop before final packaging and ask for your review.

## Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| SF3D gated model access | Baseline cannot run immediately | Request Hugging Face access early; keep TripoSR/SPAR3D as fallback candidates |
| Hunyuan3D-2.1 VRAM exceeds 8GB | Fine-tuning may be impossible locally | Evaluate 2mini/2mv first; move fine-tuning to cloud or limit fine-tuning to ControlNet |
| TRELLIS mesh OOM | Original architecture cannot deliver GLB locally | Demote TRELLIS to experimental comparison only |
| Sketch-to-render output changes shoe structure | 3D result may drift from input design | Keep control maps, use conservative prompts, compare against original sketch |
| Three-view fusion is too large for MVP | Schedule risk | Implement three-view upload/preprocessing first; use multi-view 3D only after baseline works |
| CAD/NURBS parameterization is too difficult | Thesis scope risk | Treat as future work; deliver mesh-based GLB/OBJ reconstruction |

## Current Next Step

After you review and approve this Step 7 documentation update, the recommended next step is:

**Step 8: Evaluate Stable Fast 3D baseline in WSL and verify one shoe image can produce a GLB within 8GB VRAM.**
