# Dev Plan

## Step Policy

This project will proceed one checkpoint at a time. After each phase, I will stop and wait for your review before moving on.

The route is updated from a TRELLIS-dominant system to:

1. **ControlNet sketch-domain adaptation** to bridge designer sketch inputs and image-to-3D model expectations.
2. **Hunyuan3D-2mini / Hunyuan3D-2mv** as the preferred shape-generation direction after Phase 5B visual review.
3. **SF3D baseline** as a stable comparison/fallback backend.

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

Status: in progress. Phase 3A technical validation passed on public shoe line art; Phase 3B single-view patent-sketch validation passed technically.

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

Phase 3B Results:

- Expired sport-shoe patent drawing `USD247201S` collected from Google Patents.
- Manual crop utility added for reproducible patent view extraction.
- Single-view right-side patent sketch was preprocessed into Canny/Scribble controls.
- Top-plan and bottom-plan views were also preprocessed for future multi-view experiments.
- ControlNet render from right-side patent sketch succeeded.
- Raw patent sketch -> SF3D and ControlNet patent render -> SF3D both exported readable GLB files.
- ControlNet-rendered patent input again gave a somewhat fuller mesh than raw line input.
- Limitation: patent-page crops are imperfect and not yet equivalent to clean designer three-view sketches.

Success criteria:

- Output render keeps the shoe silhouette and key features.
- Pipeline can run without breaking the SF3D environment.
- We have a clear prompt/control strategy for shoes.
- We can decide whether ControlNet improves SF3D input quality compared with raw sketches.

Human Checkpoint:

- Stop after sketch-to-render validation and ask for your review. Phase 3A is now ready for review before deeper tuning or three-view work.

## Phase 4 - End-to-End MVP Pipeline

Status: in progress. Phase 4A CLI skeleton passed on the patent side-view sketch. Phase 4B mesh reporting layer passed a direct smoke test.

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

Phase 4A Results:

- CLI orchestrator implemented at `code/pipeline/cli_mvp.py`.
- Supports `direct`, `controlnet`, and `both` modes.
- End-to-end smoke test passed with `right_side_fig4_clean.png`.
- The CLI generated preprocessing outputs, a ControlNet render, two SF3D GLBs, and JSON reports.
- `controlnet_render` and `direct_sketch` GLB outputs both passed `trimesh` validation.

Phase 4B Results:

- Mesh reporting was moved into `code/postprocess/mesh_report.py`.
- The CLI now writes a paper/UI-friendly mesh report for each generated GLB.
- The report includes:
  - GLB existence, file size, scene type, geometry count, vertices, and faces.
  - Aggregate bounds, dimensions, and smallest-to-longest dimension ratio as a thickness proxy.
  - Surface area, watertight status, reliable volume only when all geometry is watertight, and connected-component counts.
  - Structured warnings for thin geometry, many fragments, non-watertight meshes, and the unresolved internal-structure risk.
  - `display_summary` rows designed for later Gradio tables.
- A direct CLI smoke test passed with run id `phase4b_report_smoke_direct`.

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

- Stop after CLI MVP/reporting work and ask for your review before UI work or destructive mesh cleanup. Phase 4B is ready for review.

## Phase 5 - Hunyuan3D Candidate Evaluation

Status: in progress. Phase 5A pre-installation candidate evaluation completed. Phase 5B Hunyuan3D-2mini shape-only smoke test passed.

Goal:

- Decide whether Hunyuan3D should become the fine-tuning/research branch of the project.

Candidate order:

1. `Hunyuan3D-2mini` for low VRAM local shape generation.
2. `Hunyuan3D-2mv` for three-view/multi-view alignment with the thesis topic.
3. `Hunyuan3D-2.1` for fine-tuning potential, if hardware or cloud resources permit.

Phase 5A Results:

- Official Hunyuan3D sources were reviewed before installing anything.
- Hunyuan3D-2mini is the safest first local test target because it is the 0.6B shape model.
- Hunyuan3D-2mv is the best conceptual match for the project's three-view shoe-sketch route, but should be tested only after a basic Hunyuan environment works.
- Hunyuan3D-2.1 is not a good local MVP backend on the current 8GB GPU because its official memory guidance is above the local VRAM budget, but it remains a strong cloud/fine-tuning research candidate.
- Full local 3D fine-tuning is not realistic on this machine; ControlNet remains the practical local adaptation/fine-tuning path.
- Evaluation report: `agent/Hunyuan3D_Candidate_Evaluation.md`.

Phase 5B Results:

- Created isolated WSL conda environment `hunyuan3d`.
- Installed PyTorch CUDA `2.4.0+cu118`, Hunyuan3D-2 dependencies, and editable `hy3dgen`.
- Added runner `code/reconstruction/run_hunyuan3d_shape.py`.
- Ran Hunyuan3D-2mini shape-only inference on the ControlNet-rendered patent shoe image.
- Texture generation was intentionally disabled.
- Output GLB was generated successfully.
- Peak CUDA memory: `4436.453 MB`.
- Inference time after model loading: `30.967 s`.
- Mesh validation: valid GLB, 1 geometry, 117700 vertices, 235396 faces, watertight, 1 connected component.
- Human visual review: the generated Hunyuan3D-2mini GLB is clearly better than the earlier SF3D output for the footwear case.
- Route implication: Hunyuan3D-2mini is promoted to the current preferred shape-generation backend; SF3D is retained as a stable baseline/fallback.
- Evaluation report: `agent/Hunyuan3D_2mini_Smoke_Test.md`.

Tasks:

- Install Hunyuan3D in a separate environment to avoid breaking SF3D.
- Run low-VRAM inference on one shoe image.
- If possible, test multi-view input with `Hunyuan3D-2mv`.
- Inspect whether training/fine-tuning scripts can be reduced to a small shoe-domain experiment.
- Decide local-only vs cloud-assisted fine-tuning.

Tests:

- Import Hunyuan3D modules: passed with non-blocking `pymeshlab` plugin warnings.
- Shape-only inference smoke test: passed with Hunyuan3D-2mini.
- Optional texture generation test only if VRAM allows.
- Record VRAM and runtime.

Next test proposal:

- Run Hunyuan3D-2mv shape-only inference after review.
- Keep texture generation disabled.
- Run generated mesh through `code/postprocess/mesh_report.py`.

Success criteria:

- We can clearly classify Hunyuan3D as one of:
  - local inference backend,
  - cloud fine-tuning candidate,
  - paper-only comparison/future-work model.

Human Checkpoint:

- Stop after Hunyuan3D feasibility report and ask for your review. Phase 5B visual review is completed; Phase 5C Hunyuan3D-2mv testing is next.

## Phase 6 - Mesh Post-processing

Goal:

- Improve generated mesh usability without destroying shoe design details.

Tasks:

- Load generated GLB/OBJ with `trimesh` or `open3d`.
- Generate non-destructive mesh diagnostics for paper and UI display.
- Apply conservative smoothing.
- Add optional decimation or mesh cleanup.
- Preserve original and processed outputs for comparison.
- Export final GLB as the UI default.
- Add basic inspection/reporting for internal mesh artifacts where feasible.

Current status:

- Non-destructive mesh diagnostics are implemented in Phase 4B.
- Geometry-changing cleanup, smoothing, and decimation remain pending and require visual comparison before they become default behavior.

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

After Phase 5B visual review, the recommended next step is:

**Phase 5C: Hunyuan3D-2mv shape-only multi-view candidate testing.**
