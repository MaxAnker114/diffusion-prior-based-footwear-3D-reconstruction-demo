# Thesis Writing Plan

Date: 2026-05-06

## Writing Principle

The thesis will be written step by step. Each major step must be reviewed by the user before moving to the next one.

Current project direction:

- Task: reconstruct a 3D footwear model from single-view or three-view designer sketches.
- Main backend: Hunyuan3D-2mini / Hunyuan3D-2 family candidate.
- Baseline: SF3D.
- Adaptation route: ControlNet sketch-domain conditioning and future fine-tuning.
- Evaluation focus: visual quality, mesh usability, geometry bounds, face count, thickness/internal-structure risk, and demo reproducibility.

## Step 1: Thesis Skeleton And Metadata

Goal:

- Convert the USTC template from sample content into project-specific thesis structure.
- Set undergraduate template mode.
- Prepare metadata from the midterm PDF.

Files:

- `paper/ustcthesis/main.tex`
- `paper/ustcthesis/ustcsetup.tex`
- `paper/ustcthesis/chapters/`
- `paper/ustcthesis/bib/references.bib`

Output:

- Project chapter skeleton.
- Correct title, author, department, major, supervisor, and bibliography wiring.

Review gate:

- User reviews the metadata and chapter structure.

## Step 2: Chapter 1 Introduction

Goal:

- Explain research background, project motivation, problem definition, and thesis contributions.

Key points:

- Footwear design needs fast 3D visualization from sketches.
- Traditional 3D modeling has high manual cost.
- Diffusion-prior and image-to-3D models make rapid reconstruction feasible.
- This project focuses on a practical demo pipeline under local hardware limits.

Expected sections:

- Research background and significance.
- Problem definition.
- Main work and contributions.
- Thesis organization.

Review gate:

- User confirms whether the research framing matches the graduation project.

## Step 3: Chapter 2 Related Work

Goal:

- Build a literature-based technical context.

Expected sections:

- Single-image 3D reconstruction.
- Diffusion-prior 3D generation.
- Multi-view generation and feed-forward 3D reconstruction.
- Sketch-conditioned generation and ControlNet.
- Footwear/sketch input scenario and remaining challenges.

Reference source:

- `paper/ustcthesis/bib/references.bib`
- `paper/references/README.md`

Review gate:

- User reviews whether cited methods and comparison logic are reasonable.

## Step 4: Chapter 3 Method

Goal:

- Describe the proposed pipeline and why the final route changed from TRELLIS/SF3D baseline to Hunyuan3D-centered generation.

Expected sections:

- Overall pipeline.
- Input preprocessing for single-view / three-view sketches.
- Hunyuan3D generation route.
- SF3D baseline route.
- ControlNet sketch-domain adaptation design.
- Mesh post-processing and report metrics.

Review gate:

- User checks whether the method description matches the actual implementation and project route.

## Step 5: Chapter 4 System Design And Implementation

Goal:

- Explain the implemented CLI and Gradio demo.

Expected sections:

- System architecture.
- Environment and dependency design.
- Inference backend abstraction.
- Mesh report module.
- Evaluation sample management.
- Gradio interface.

Project sources:

- `code/`
- `System_Architecture.md`
- `Dev_Plan.md`
- `paper/evaluation_samples/`

Review gate:

- User verifies that the system description matches the real demo behavior.

## Step 6: Chapter 5 Experiments And Analysis

Goal:

- Present reproducible evaluation results and limitations.

Expected sections:

- Experimental setup.
- Test input design: designer sketch / product-like single-view and three-view cases.
- SF3D baseline results.
- Hunyuan3D-2mini results.
- Mesh metrics and post-processing report.
- Failure cases: internal structure, thickness ambiguity, sketch-domain mismatch.
- Qualitative comparison and analysis.

Evidence source:

- `paper/evaluation_samples/`
- generated GLB screenshots and mesh reports.

Review gate:

- User confirms whether the experimental claims match observed outputs.

## Step 7: Chapter 6 Conclusion And Future Work

Goal:

- Summarize completed work and honestly discuss limitations.

Expected sections:

- Work summary.
- Main findings.
- Current limitations.
- Future work: dataset construction, Hunyuan3D fine-tuning, ControlNet sketch adaptation, multi-view consistency, internal-structure constraints.

Review gate:

- User confirms final project positioning and limitations.

## Step 8: Abstract, Keywords, Acknowledgements

Goal:

- Write the Chinese abstract, English abstract, keywords, and acknowledgements after the main chapters are stable.

Reason:

- Abstract should reflect the final implementation and experiment conclusions, so it should be written near the end.

Review gate:

- User reviews language, tone, and school-format requirements.

## Step 9: Formatting And Compilation

Goal:

- Compile the thesis and fix LaTeX, bibliography, figure, table, and layout issues.

Prerequisite:

- Install a local TeX distribution or use an online LaTeX environment.

Checks:

- `xelatex` / `latexmk` availability.
- Bibliography renders correctly.
- Figures fit pages.
- No sample template content remains.
- No generated LaTeX artifacts are staged by git.

Review gate:

- User reviews compiled PDF.

## Step 10: Final Polish

Goal:

- Improve academic style, consistency, citations, figure captions, table captions, and conclusion wording.

Checks:

- Terminology consistency.
- Contribution statements are not overstated.
- Limitations are clear and defensible.
- The thesis matches the actual demo and code.

Review gate:

- User performs final approval before final archive or submission version.

