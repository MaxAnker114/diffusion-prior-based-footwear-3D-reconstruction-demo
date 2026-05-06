# Thesis LaTeX Preparation

Date: 2026-05-06

## Template Location

The school LaTeX template has been placed at:

- `paper/ustcthesis/`

Recognized files:

- `main.tex`
- `ustcsetup.tex`
- `ustcthesis.cls`
- `Makefile`
- `latexmkrc`
- `chapters/`
- `bib/ustc.bib`
- `figures/`
- `ustcthesis-doc.pdf`

## Template Type

The template is `ustcthesis`, the University of Science and Technology of China thesis template.

The current sample `main.tex` uses:

```tex
\documentclass[degree=doctor]{ustcthesis}
```

For this project, the expected final setting should be:

```tex
\documentclass[degree=bachelor]{ustcthesis}
```

The template comments show these class options:

- `degree = doctor | master | bachelor`
- `degree-type = academic | professional | engineering`
- `language = chinese | english`
- `fontset = windows | mac | ubuntu | fandol`
- `review = true | false`

## Bachelor Fields Needed

For an undergraduate thesis, `ustcsetup.tex` should eventually provide:

- Chinese title
- English title
- Author name
- English author name
- Major / specialty
- English major / specialty
- Supervisor
- English supervisor
- Department
- Student ID
- Completion date if the default date should not be used

The current template still contains sample personal information and should not be treated as project content.

## Build Method

Template README recommends:

```bash
latexmk -xelatex main.tex
```

or:

```bash
make
```

The provided `latexmkrc` uses XeLaTeX and BibTeX-compatible compilation.

## Current Local Build Environment

Checked on 2026-05-06:

- Windows PowerShell: `latexmk`, `xelatex`, and `bibtex` were not found in PATH.
- WSL Ubuntu: `latexmk`, `xelatex`, `bibtex`, `kpsewhich`, and `tlmgr` were not found in PATH.
- WSL has `make`, but Makefile compilation still requires TeX tools.

Conclusion:

- We can draft and edit LaTeX source now.
- PDF compilation requires installing a TeX distribution first.

Recommended options:

1. Install TeX Live in WSL.
2. Install MiKTeX on Windows and ensure `latexmk`/`xelatex` are in PATH.
3. Use Overleaf or another online LaTeX environment temporarily.

For local reproducibility with this project, WSL TeX Live is the cleanest route.

## Git Hygiene

Added LaTeX build artifacts to `.gitignore` so future compilation does not accidentally stage files such as:

- `.aux`
- `.log`
- `.xdv`
- `.toc`
- `.bbl`
- `.fdb_latexmk`
- `.synctex.gz`

The template directory is currently untracked. Before substantial thesis writing, the recommended next stable commit should include:

- template source files that we will edit;
- thesis figures copied or referenced from `paper/evaluation_samples/`;
- `.gitignore` LaTeX artifact rules.

Generated build outputs should generally remain untracked unless a final PDF needs to be archived.

## Recommended Thesis Project Layout

Use the template as the thesis working directory:

```text
paper/ustcthesis/
|-- main.tex
|-- ustcsetup.tex
|-- chapters/
|   |-- abstract.tex
|   |-- intro.tex
|   |-- related_work.tex
|   |-- method.tex
|   |-- implementation.tex
|   |-- experiments.tex
|   |-- conclusion.tex
|-- bib/
|   |-- references.bib
|-- figures/
|   |-- evaluation/
```

The existing template chapter examples should be replaced gradually with project-specific chapters rather than kept as final content.

## Proposed Thesis Title

Chinese:

```text
融合三视图特征的鞋履3D模型重建研究
```

English:

```text
Research on 3D Shoe Model Reconstruction by Fusing Multi-View Features
```

These titles come from `paper/毕业论文中期.pdf`.

## Metadata Extracted From Midterm PDF

Extracted from `paper/毕业论文中期.pdf`:

- Student ID: `PB22111607`
- Author: `安凯尔·艾尼瓦尔`
- Department: `计算机科学与技术系`
- Major: `01101计算机科学与技术`
- Supervisor: `石震波`
- Supervisor title: `特任副研究员`
- Supervisor unit: `215计算机科学与技术学院`
- Chinese title: `融合三视图特征的鞋履3D模型重建研究`
- English title: `Research on 3D Shoe Model Reconstruction by Fusing Multi-View Features`
- Topic type: `理论类`

Still useful to confirm before final metadata writing:

- official English spelling of the author's name;
- official English spelling of the supervisor's name;
- whether the school requires an English abstract;
- whether there is a required word count or page count.

## Reference Baseline

Created a compact literature baseline at:

- `paper/references/README.md`
- `paper/references/papers/`
- `paper/ustcthesis/bib/references.bib`

The local PDF set only uses arXiv/open-access sources. It covers:

- diffusion-prior 3D generation;
- single-image and multi-view 3D reconstruction;
- feed-forward 3D baselines;
- SF3D and Hunyuan3D-2 project candidates;
- ControlNet/sketch-conditioning;
- classic mesh-reconstruction baselines.

## Next Step

After the user confirms the build environment choice and approves the current pre-thesis baseline, create the real thesis chapter skeleton in `paper/ustcthesis/chapters/` and start drafting:

1. Abstract
2. Introduction
3. Related Work
4. Method
5. System Design and Implementation
6. Experiments and Analysis
7. Conclusion
