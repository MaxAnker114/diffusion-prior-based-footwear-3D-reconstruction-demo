# Diffusion-Prior-Based Footwear 3D Reconstruction Demo

本项目是一个面向毕业设计的鞋履 3D 重建研究 demo，目标是从鞋履单视图或三视图草图/图像生成可预览、可导出的 3D 模型。

当前技术路线已经从 TRELLIS 主导调整为：

1. **Stable Fast 3D (SF3D) baseline**：优先完成可在 RTX 4060 Laptop GPU 8GB VRAM 上运行的单图到 GLB 基线。
2. **Hunyuan3D fine-tune candidate**：作为更高质量生成与鞋履域适配的研究候选。
3. **ControlNet sketch-domain adaptation**：将鞋履草图、边缘图或三视图输入转化为更适合 3D 生成模型的渲染图。

TRELLIS 保留为实验性/高显存对比后端，不再作为当前 MVP 的主链路。

## Project Structure

```text
D:/Final_Project
├── agent/   # 架构、开发计划、评阅结论、agent 协作记录
├── code/    # 后续项目代码、脚本、本地实验入口
├── paper/   # 论文材料、中期报告、后续论文相关资产
└── README.md
```

## Current Documents

- `agent/System_Architecture.md`：系统架构与模型路线。
- `agent/Dev_Plan.md`：分阶段开发计划与人工审阅 checkpoint。
- `paper/毕业论文中期.pdf`：论文中期材料。

## Development Policy

- 复杂任务一步一步推进，每个关键阶段完成后先审阅再继续。
- 在关键性更改前，先确保当前稳定版本已经 commit。
- 配置了远程仓库后，稳定版本应 push 到 GitHub，方便追踪与回退。
- 不将 API Key、token、登录态、虚拟环境、模型权重、缓存、日志或大型第三方依赖提交到仓库。

## Next Step

等待 Step 7 文档审阅通过后，进入：

**Step 8: Evaluate Stable Fast 3D baseline in WSL and verify one shoe image can produce a GLB within 8GB VRAM.**
