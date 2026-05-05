# Dev Plan

## Step Policy

This project will proceed one checkpoint at a time. After each phase, I will stop and wait for your review before moving on.

The route is updated from a TRELLIS-dominant system to:

1. **SF3D baseline** for reliable local single-image-to-GLB delivery.
2. **Hunyuan3D fine-tune candidate** for research value and possible shoe-domain adaptation.
3. **ControlNet sketch-domain adaptation** to bridge designer sketch inputs and image-to-3D model expectations.

Primary input definition:

- The formal project input is a single-view or three-view designer shoe sketch.
- Product photos are only baseline smoke-test inputs for validating image-to-3D backends.
- Future tests should prioritize sketch inputs because they match the thesis target more closely.

## Phase 0 - Documentation and Route Review

Status: completed.

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

- Completed. The route was updated to SF3D + Hunyuan3D + ControlNet, with TRELLIS retained only as an experimental comparison backend.

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

Status: completed and passed for baseline feasibility.

Goal:

- Prove that Stable Fast 3D can generate a usable shoe GLB locally from a single image, before adapting the pipeline to designer sketches.

Tasks:

- Check access requirements for `stabilityai/stable-fast-3d`.
- Install SF3D into a clean WSL environment or a dedicated conda environment.
- Run SF3D on a simple sample image.
- Run SF3D on at least one shoe image.
- Export GLB and inspect it in a local viewer or Gradio `Model3D`.
- Record runtime, peak VRAM, and failure modes.

Tests:

- Import SF3D modules: passed.
- Single sample inference smoke test: passed.
- Shoe image inference smoke test: passed with `code/test_assets/worn_shoe_commons.png`.
- GLB file loads successfully with `trimesh`: passed.

Verified Results:

- Official SF3D sample generated a readable GLB.
- Public shoe image generated a readable GLB.
- Shoe test peak GPU memory reported by SF3D: `6172.10009765625 MB`.
- Shoe test mesh validation: 1 geometry, `18572` vertices, `28956` faces.
- Human visual review: exterior shoe form is basically acceptable as a baseline.
- Human visual review: internal shoe structure is not reasonable enough and should be treated as a core technical difficulty.

Success criteria:

- A generated GLB can be opened and previewed: passed at file/mesh validation level.
- Peak VRAM stays within the RTX 4060 8GB limit: passed.
- The output is good enough to serve as a baseline in the graduation demo: passed as a technical baseline; visual quality will continue to be reviewed with more shoe cases.

Human Checkpoint:

- Completed. SF3D is accepted as the default MVP 3D backend for exterior baseline generation.
- Important limitation: SF3D product-image success does not mean the final designer-sketch task is solved.
- Important limitation: internal shoe geometry remains an unresolved hidden-structure reconstruction problem.

## Phase 3 - Designer Sketch-Domain Adaptation

Status: in progress. Phase 3A technical validation passed on a public shoe line-art sketch.

Goal:

- Convert single-view or three-view designer shoe sketches into cleaner rendered shoe images that are easier for SF3D/Hunyuan3D to reconstruct.
- Establish the first real task-aligned test path for sketch input rather than product-photo input.

Tasks:

- Prepare or collect at least one single-view designer shoe sketch and, if available, one three-view sketch set.
- Decide first ControlNet mode: Canny or Scribble.
- Implement sketch preprocessing: crop, background cleanup, edge extraction, and resizing.
- Build a minimal ControlNet inference script.
- Test single-view sketch to rendered shoe image.
- Test three-view sketch normalization without forcing 3D generation yet.
- Compare direct sketch/SF3D behavior against ControlNet-rendered/SF3D behavior if technically possible.

Tests:

- `StableDiffusionControlNetPipeline` full initialization test.
- One local sketch-to-render inference.
- Compare original sketch, control map, and generated render.
- Record whether the rendered output preserves shoe silhouette, sole, upper, toe box, heel, and key design lines.

Phase 3A Results:

- Public shoe line-art test asset collected from Openclipart.
- Sketch preprocessing script implemented.
- Canny and Scribble control maps generated.
- ControlNet Canny render succeeded with `lllyasviel/control_v11p_sd15_canny` and `runwayml/stable-diffusion-v1-5`.
- Raw sketch -> SF3D and ControlNet render -> SF3D both exported readable GLB files.
- Initial evidence suggests ControlNet-rendered input gives SF3D a fuller geometry range than raw line art.

Success criteria:

- Output render keeps the shoe silhouette and key features.
- Pipeline can run without breaking the SF3D environment.
- We have a clear prompt/control strategy for shoes.
- We can decide whether ControlNet improves SF3D input quality compared with raw sketches.

Human Checkpoint:

- Stop after sketch-to-render validation and ask for your review. Phase 3A is now ready for review before deeper tuning or three-view work.

## Phase 4 - End-to-End MVP Pipeline

Goal:

- Connect designer-sketch preprocessing, optional ControlNet rendering, SF3D reconstruction, post-processing, and GLB preview.

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

- Single-view designer sketch end-to-end CLI smoke test.
- Shoe sketch sample end-to-end GLB generation.
- Verify intermediate image outputs are saved.
- Verify final GLB loads.
- Record exterior shape quality and internal-structure artifacts separately.

Success criteria:

- One command can convert an input designer shoe sketch into a GLB.
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
- Add basic inspection/reporting for internal mesh artifacts where feasible.

Tests:

- Compare before/after mesh visually.
- Verify final GLB still loads in browser.
- Ensure post-processing does not remove key shoe components.
- Note that post-processing may reduce artifacts but cannot fully solve unobserved internal geometry.

Human Checkpoint:

- Stop after post-processing comparison and ask for your review.

## Phase 7 - Gradio UI Integration

Goal:

- Build the project demo UI after the core pipeline is stable.

Tasks:

- Build a focused Gradio Blocks app.
- Inputs:
  - single-view designer sketch upload
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
- Separate exterior-shape evaluation from internal-structure evaluation.
- Summarize why full CAD/NURBS reconstruction is future work.
- Summarize why hidden internal shoe geometry is a limitation of single-view reconstruction.

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
| Internal shoe structure is unreasonable | Exterior may look acceptable while hidden geometry is implausible | Treat as hidden-geometry completion limitation; use three-view constraints where possible; document clearly in paper |
| Three-view fusion is too large for MVP | Schedule risk | Implement three-view upload/preprocessing first; use multi-view 3D only after baseline works |
| CAD/NURBS parameterization is too difficult | Thesis scope risk | Treat as future work; deliver mesh-based GLB/OBJ reconstruction |

## Current Next Step

After Phase 2 baseline validation, the recommended next step is:

**Phase 3: Designer Sketch-Domain Adaptation.**
