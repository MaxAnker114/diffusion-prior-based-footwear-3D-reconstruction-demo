# Hunyuan3D Candidate Evaluation

Date: 2026-05-05

## Goal

Evaluate whether Hunyuan3D should become the project's research/fine-tuning candidate after the current SF3D baseline and ControlNet sketch-domain adaptation path.

This is a pre-installation evaluation. No new Hunyuan3D environment was installed in this phase.

## Project Fit

The project target is single-view or three-view designer shoe sketch to 3D footwear mesh.

Hunyuan3D is relevant because:

- It is a recent open-source image-to-3D family from Tencent Hunyuan.
- It separates shape generation and texture generation, which is useful for our project because shape quality matters more than texture at the current stage.
- It includes a multi-view shape model, which aligns better with the thesis goal than SF3D's single-image baseline.
- Hunyuan3D-2.1 includes training code and a VAE encoder, making it academically stronger as a fine-tuning candidate.

## Sources Checked

Primary sources:

- Hunyuan3D-2 GitHub: https://github.com/Tencent-Hunyuan/Hunyuan3D-2
- Hunyuan3D-2.1 GitHub: https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1
- Hunyuan3D-2 Hugging Face model collection: https://huggingface.co/tencent/Hunyuan3D-2
- Hunyuan3D-2mini Hugging Face: https://huggingface.co/tencent/Hunyuan3D-2mini
- Hunyuan3D-2mv Hugging Face: https://huggingface.co/tencent/Hunyuan3D-2mv
- Hunyuan3D-2.1 Hugging Face: https://huggingface.co/tencent/Hunyuan3D-2.1
- Hunyuan3D 2.5 technical report: https://arxiv.org/abs/2506.16504

Firecrawl was also used for live search/scrape checks. Its local cache is ignored by Git through `.firecrawl/`.

## Candidate Matrix

| Candidate | Role | Hardware fit on 8GB VRAM | Project value | Recommendation |
| --- | --- | --- | --- | --- |
| Hunyuan3D-2mini | Low-parameter local shape smoke test | Best fit. It is the 0.6B shape model and should be the first local target. | Useful as a lightweight Hunyuan baseline against SF3D. | Install/test first. |
| Hunyuan3D-2mv | Multi-view shape candidate | Possible only with low-VRAM mode or reduced settings. Texture should be disabled initially. | Highest alignment with the three-view shoe-sketch thesis direction. | Test after 2mini imports and single-image shape generation work. |
| Hunyuan3D-2.0 full | General Hunyuan shape+texture baseline | Shape generation may fit around the 8GB limit if texture is disabled; full shape+texture does not fit comfortably. | Useful comparison, but less targeted than 2mini/2mv for our constraints. | Optional only after 2mini/2mv. |
| Hunyuan3D-2.1 | Fine-tuning/research candidate | Not suitable for local full pipeline on 8GB. Official memory guidance is above our GPU for shape alone, and much higher for texture. | Strongest academic candidate because training code and PBR/texture improvements are open. | Keep as paper/cloud fine-tuning candidate, not local MVP backend. |
| Hunyuan3D 2.5 | Latest technical direction | No stable local project route selected in this phase. | Useful as related work and "newer Hunyuan direction" in the paper. | Related work only for now. |

## VRAM Feasibility

The current local GPU is an RTX 4060 Laptop GPU with about 8GB VRAM.

### Hunyuan3D-2

Official Hunyuan3D-2 documentation states that:

- shape generation requires about 6GB VRAM;
- shape + texture generation requires about 16GB VRAM;
- a `--low_vram_mode` option exists and can reduce memory usage at the cost of slower generation.

Interpretation for this project:

- Shape-only inference is plausible on 8GB and worth testing.
- Texture generation should be disabled for the first smoke tests.
- If texture is needed for demo visuals later, SF3D can remain the default textured GLB route while Hunyuan3D is used for shape comparison.

### Hunyuan3D-2mini

Hunyuan3D-2mini is described by the official Hunyuan3D-2 release notes as a 0.6B shape model.

Interpretation:

- It is the safest first Hunyuan target for our laptop GPU.
- It may provide weaker geometry than the larger models, but the value of Phase 5B is to validate installation, inference, and mesh export without breaking the current SF3D pipeline.

### Hunyuan3D-2mv

Hunyuan3D-2mv is the official multi-view shape model released with the Hunyuan3D-2 family.

Interpretation:

- It is the best conceptual fit for designer three-view shoe sketches.
- It should be tested only after the basic Hunyuan environment works.
- The first 2mv test should use normalized rendered/processed views and disable texture.
- If local VRAM is still too tight, it should become a cloud or paper-only research branch.

### Hunyuan3D-2.1

Official Hunyuan3D-2.1 documentation gives much higher GPU memory guidance than Hunyuan3D-2:

- shape generation: about 10GB;
- texture generation: about 21GB;
- shape + texture: about 29GB.

Interpretation:

- Hunyuan3D-2.1 is not a good local MVP backend for the current 8GB card.
- It is still valuable academically because it includes training code and a more complete research release.
- For this project, 2.1 should be recorded as a fine-tuning/cloud candidate rather than a local dependency for the near-term demo.

## Fine-tuning Implications

Local full 3D fine-tuning is not realistic on the current machine.

Better staged strategy:

1. Keep ControlNet sketch-domain adaptation as the local fine-tuning/adaptation path.
2. Use SF3D as the reliable local GLB baseline.
3. Evaluate Hunyuan3D-2mini for local shape-only inference.
4. Evaluate Hunyuan3D-2mv if 2mini works, because multi-view input is thesis-aligned.
5. Treat Hunyuan3D-2.1 as a cloud fine-tuning candidate or paper future-work direction.

## Proposed Phase 5B

Install Hunyuan3D in a separate WSL conda environment, not inside `trellis310` or `sf3d`.

Proposed environment name:

- `hunyuan3d`

Initial smoke-test order:

1. Clone Hunyuan3D-2 into `code/third_party/Hunyuan3D-2`.
2. Install only the minimal dependencies needed for shape generation.
3. Run an import check.
4. Run Hunyuan3D-2mini shape-only inference on one existing shoe/sketch-derived render.
5. Export mesh and run `code/postprocess/mesh_report.py`.
6. If 2mini works, test Hunyuan3D-2mv with two or three available views or view-like rendered inputs.

Safety rules:

- Do not modify the existing `sf3d` and `trellis310` environments.
- Do not enable texture generation in the first test.
- Do not make Hunyuan3D the default backend until a successful GLB/OBJ smoke test is recorded.
- Preserve SF3D as the working MVP path.

## Decision

Phase 5A conclusion:

- Hunyuan3D remains worth evaluating.
- The next local target should be Hunyuan3D-2mini shape-only inference.
- Hunyuan3D-2mv is the most thesis-aligned candidate after the basic environment is validated.
- Hunyuan3D-2.1 should not be the next local install target on 8GB VRAM, but should remain the strongest fine-tuning/cloud research candidate.

Phase 5A status:

- Passed as a pre-installation candidate evaluation.
- Waiting for human review before Phase 5B installation and smoke testing.
