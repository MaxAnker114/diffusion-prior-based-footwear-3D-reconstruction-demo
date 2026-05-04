# Code

此目录用于放置后续项目代码、推理脚本、UI 入口、实验工具和本地运行配置。

计划中的主要模块：

- `preprocess/`：鞋履图像裁剪、背景处理、Canny/Scribble 控制图生成。
- `controlnet/`：草图到鞋履渲染图的 2D 适配。
- `reconstruction/`：SF3D baseline 与 Hunyuan3D 候选后端。
- `postprocess/`：GLB/OBJ mesh 清理、平滑、减面。
- `ui/`：Gradio demo。

`code/third_party/` 用于本地第三方源码或实验依赖，默认不提交到 Git。
