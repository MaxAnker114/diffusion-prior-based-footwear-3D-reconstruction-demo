# Code

此目录用于放置后续项目代码、推理脚本、UI 入口、实验工具和本地运行配置。

计划中的主要模块：

- `preprocess/`：鞋履图像裁剪、背景处理、Canny/Scribble 控制图生成。
- `controlnet/`：草图到鞋履渲染图的 2D 适配。
- `reconstruction/`：SF3D baseline 与 Hunyuan3D 候选后端。
- `postprocess/`：GLB/OBJ mesh 清理、平滑、减面。
- `ui/`：Gradio demo。

`code/third_party/` 用于本地第三方源码或实验依赖，默认不提交到 Git。

## CLI MVP

Run from WSL with the `trellis310` environment active:

```bash
source /home/anker/miniforge3/etc/profile.d/conda.sh
conda activate trellis310
cd /mnt/d/Final_Project
python code/pipeline/cli_mvp.py \
  code/test_assets/patent_sketches/usd247201s_sport_shoe/views/right_side_fig4_clean.png \
  --run-id phase4_cli_smoke_patent_side \
  --mode both \
  --controlnet-steps 8 \
  --texture-resolution 512
```

Modes:

- `direct`: normalized sketch -> SF3D.
- `controlnet`: sketch -> ControlNet render -> SF3D.
- `both`: run both paths and compare reports.

Runtime outputs are written under `code/outputs/pipeline_runs/<run_id>/` and are ignored by Git.
