# Thesis Format And Compile Preparation Check

Date: 2026-05-06

## Scope

Checked the active USTC thesis entry:

- `paper/ustcthesis/main.tex`
- `paper/ustcthesis/ustcsetup.tex`
- chapters included by `main.tex`
- bibliography file `paper/ustcthesis/bib/references.bib`
- figures referenced by included chapters

## Current Compile Environment

Checked in WSL after installing TinyTeX, a lightweight TeX Live distribution:

- `xelatex`: XeTeX 3.141592653-2.6-0.999998 (TeX Live 2026)
- `latexmk`: Version 4.88
- `bibtex`: BibTeX 0.99e (TeX Live 2026)

Conclusion:

- The thesis source can be compiled locally in WSL.
- The current PDF build succeeds with `latexmk -xelatex`.

Installed template dependencies include:

- Chinese and CJK packages: `ctex`, `xecjk`, `zhnumber`, `fandol`
- USTC template helpers: `bigfoot`, `notoccite`, `algorithm2e`, `ifoddpage`, `relsize`
- Math fonts: `xits`, `stix2-otf`

TinyTeX path:

- `/home/anker/.TinyTeX/bin/x86_64-linux`

## Static Checks Passed

Included chapters:

- `chapters/abstract.tex`
- `chapters/chapter1_introduction.tex`
- `chapters/chapter2_related_work.tex`
- `chapters/chapter3_method.tex`
- `chapters/chapter4_system_design.tex`
- `chapters/chapter5_experiments.tex`
- `chapters/chapter6_conclusion.tex`
- `chapters/appendix.tex`
- `chapters/acknowledgements.tex`

All files referenced by `\include{...}` exist.

Bibliography:

- `\bibliography{bib/references}` resolves to `paper/ustcthesis/bib/references.bib`.
- All citation keys used in included chapters exist in `references.bib`.

Figures:

- `figures/related_work/related_work_map.png`
- `figures/related_work/sketch_domain_adaptation.png`
- `figures/method/method_pipeline.png`
- `figures/method/backend_comparison.png`
- `figures/system/system_architecture_tree.png`
- `figures/system/gradio_ui_screenshot.png`
- `figures/evaluation/phase8b_three_view_input_evidence.png`
- `figures/evaluation/phase8b_s1_sample_sheet.png`
- `figures/evaluation/phase8b_sf3d_baseline_results.png`
- `figures/evaluation/phase8b_hunyuan_results.png`
- `figures/evaluation/phase8b_comparison_grid.png`
- `figures/evaluation/phase8b_mesh_preview_strip.png`
- `figures/evaluation/phase8b_metrics_table.png`

All referenced figure files exist.

Placeholder check:

- No active included file contains `本节将`.
- No active included file contains `占位` or `placeholder`.
- No active included file contains sample template names such as `李泽平`.
- No active included file contains `XXX`.

Markdown-to-LaTeX cleanup:

- Markdown-style inline code backticks in active chapters were converted to LaTeX-safe `\texttt{...}` form.
- Underscores inside inline code/path snippets were escaped.

## Known Non-Blocking Items

The template directory still contains unused sample chapter files such as:

- `chapters/intro.tex`
- `chapters/math.tex`
- `chapters/citations.tex`
- `chapters/achievements.tex`

These files are not included by `main.tex`, so they should not affect compilation. They can be removed later if the project owner wants a cleaner thesis directory, but deletion should be reviewed first.

## Pending Human Confirmation

Metadata confirmed by project owner before compile:

- official English author name in `ustcsetup.tex`: `Anker Ainiwaer`
- official English supervisor name in `ustcsetup.tex`: `Zhenbo Shi`

## Compile Result

Build command:

```bash
cd /mnt/d/Final_Project/paper/ustcthesis
latexmk -C main.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

Output:

- `paper/ustcthesis/main.pdf`
- 51 pages after switching to the electronic one-sided PDF output, removing front-matter blank pages, revising the first chapter pagination, expanding Chapter 2 with formulas and related-work diagrams, expanding Chapter 3 with method diagrams and backend-route formulas, revising Chapters 4--6 with system/UI figures plus reordered experiment analysis, adding more Chapter 5 experiment-result figures, revising Figure 4.1, and completing Appendix A
- approximately 3.05 MB

Final log checks:

- No `Overfull` warnings remain.
- No undefined citation warnings remain.
- No undefined reference warnings remain.
- Bibliography is generated through BibTeX with `ustcthesis-bachelor.bst`.

Known non-blocking compile note:

- The log still shows attempted probing of `SimSun`, but the produced document uses Fandol CJK fonts and the PDF is generated successfully.

## Codex Preview Build

The Codex built-in PDF preview can render the Fandol/CID-font PDF incorrectly, even when Chrome, Edge, Acrobat, and PyMuPDF render it correctly.

For Codex preview, use the Windows-font build script:

```powershell
cd D:\Final_Project\paper\ustcthesis
.\build_windows_fonts_preview.ps1
```

If PowerShell blocks local script execution, use:

```powershell
cd D:\Final_Project
powershell -NoProfile -ExecutionPolicy Bypass -File .\paper\ustcthesis\build_windows_fonts_preview.ps1
```

Output:

- `paper/ustcthesis/main_windows_fonts_preview.pdf`

This script:

- creates a temporary Fontconfig file pointing WSL to `C:\Windows\Fonts`;
- compiles with `latexmk -xelatex`;
- uses Windows fonts such as `SimSun`, `SimHei`, `Times New Roman`, and `Arial`;
- keeps intermediate files under `paper/ustcthesis/.build/windows-fonts-preview`;
- writes the detailed build log to `paper/ustcthesis/.build/windows-fonts-preview/build.log`;
- does not overwrite `main.pdf`.

## Next Manual Checks

- visually inspect cover metadata and abstract pages;
- inspect bibliography rendering;
- inspect figure and table placement;
- verify no old template content appears in the PDF;
- decide whether to rename `main.pdf` for submission later.
