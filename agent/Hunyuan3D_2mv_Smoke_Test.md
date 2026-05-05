# Hunyuan3D-2mv Smoke Test

Date: 2026-05-05

## Goal

Evaluate whether Hunyuan3D-2mv can become the local multi-view shape-generation backend for the project's three-view footwear sketch direction.

This phase is a technical feasibility check. The available patent drawing set is not a clean designer three-view input, so the test uses a pseudo-three-view set only to check local runtime feasibility.

## Input Set

Pseudo-three-view patent inputs:

- `left`: `code/test_assets/patent_sketches/usd247201s_sport_shoe/views/left_side_fig3_clean.png`
- `right`: `code/test_assets/patent_sketches/usd247201s_sport_shoe/views/right_side_fig4_clean.png`
- `back`: `code/test_assets/patent_sketches/usd247201s_sport_shoe/views/rear_fig5.png`

Important limitation:

- This is not a true front/left/back designer three-view set.
- It is suitable for runtime feasibility testing, but not for final visual-quality claims.

## Implementation Update

`code/reconstruction/run_hunyuan3d_shape.py` was extended to support both:

- single-view image input;
- multi-view dictionary input through `--front`, `--left`, `--back`, and `--right`.

The runner also supports:

- `--enable-flashvdm`
- `--mc-algo`

This keeps the Hunyuan3D runner reusable for both Hunyuan3D-2mini and Hunyuan3D-2mv.

## Attempt 1: Hunyuan3D-2mv Standard

Command:

```bash
source /home/anker/miniforge3/etc/profile.d/conda.sh
conda activate hunyuan3d
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /mnt/d/Final_Project
python code/reconstruction/run_hunyuan3d_shape.py \
  --run-id phase5c_hunyuan2mv_patent_pseudo3view \
  --model-path tencent/Hunyuan3D-2mv \
  --subfolder hunyuan3d-dit-v2-mv \
  --variant fp16 \
  --steps 30 \
  --octree-resolution 256 \
  --num-chunks 20000 \
  --seed 12345 \
  --left code/test_assets/patent_sketches/usd247201s_sport_shoe/views/left_side_fig3_clean.png \
  --right code/test_assets/patent_sketches/usd247201s_sport_shoe/views/right_side_fig4_clean.png \
  --back code/test_assets/patent_sketches/usd247201s_sport_shoe/views/rear_fig5.png
```

Result:

- Hunyuan3D-2mv standard weights downloaded successfully.
- Model loading began from the local Hugging Face cache.
- The command exited with code `1` before inference output or mesh export.
- No GLB or mesh report was generated.
- The subsequent WSL session became unhealthy and returned `Wsl/Service/E_UNEXPECTED`; it recovered after `wsl --shutdown`.

Interpretation:

- Hunyuan3D-2mv standard is not yet locally validated on the 8GB GPU.
- The failure happened before usable inference output, so it should not be treated as a model-quality result.
- The likely causes are local memory/VRAM pressure or a model-load/runtime incompatibility, not input quality.

## Attempt 2: Hunyuan3D-2mv Turbo + FlashVDM

Command:

```bash
source /home/anker/miniforge3/etc/profile.d/conda.sh
conda activate hunyuan3d
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /mnt/d/Final_Project
python code/reconstruction/run_hunyuan3d_shape.py \
  --run-id phase5c_hunyuan2mv_turbo_patent_pseudo3view \
  --model-path tencent/Hunyuan3D-2mv \
  --subfolder hunyuan3d-dit-v2-mv-turbo \
  --variant fp16 \
  --enable-flashvdm \
  --steps 5 \
  --octree-resolution 256 \
  --num-chunks 20000 \
  --seed 12345 \
  --left code/test_assets/patent_sketches/usd247201s_sport_shoe/views/left_side_fig3_clean.png \
  --right code/test_assets/patent_sketches/usd247201s_sport_shoe/views/right_side_fig4_clean.png \
  --back code/test_assets/patent_sketches/usd247201s_sport_shoe/views/rear_fig5.png
```

Result:

- Turbo config was cached.
- Turbo `model.fp16.safetensors` did not finish downloading.
- A direct `snapshot_download` retry ran for 30 minutes and timed out.
- Cache still contained incomplete Hugging Face blob files after the retry.
- No GLB or mesh report was generated.

Interpretation:

- The turbo path is not rejected technically, but it is blocked by incomplete model download in the current session.
- Since standard 2mv is already heavy and unstable locally, turbo remains the better route to retry later if download/network conditions improve.

## Attempt 3: Hunyuan3D-2mv Turbo Download via HF Mirror

The project owner found a Hugging Face mirror configuration guide recommending `hf-mirror.com`.

Temporary mirror configuration used:

```bash
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_DOWNLOAD_TIMEOUT=3600
export HF_HUB_ETAG_TIMEOUT=300
```

Retry command:

```python
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="tencent/Hunyuan3D-2mv",
    allow_patterns=[
        "hunyuan3d-dit-v2-mv-turbo/config.yaml",
        "hunyuan3d-dit-v2-mv-turbo/model.fp16.safetensors",
    ],
    resume_download=True,
    max_workers=2,
)
```

Result:

- The mirror method is appropriate for Hugging Face downloads and should be reused for future large model downloads.
- In this session, the 2mv turbo safetensors download still timed out after 30 minutes.
- `hunyuan3d-dit-v2-mv-turbo/config.yaml` is cached.
- `hunyuan3d-dit-v2-mv-turbo/model.fp16.safetensors` is still not fully cached.
- The Hugging Face cache still contains incomplete blob files.

Interpretation:

- The failure is now classified as a download/cache availability blocker, not evidence that Hunyuan3D-2mv-turbo cannot run locally.
- Hunyuan3D-2mv-turbo should be retried later with a fully downloaded checkpoint or a cloud machine with more reliable model download bandwidth.

## Environment Notes

- Hunyuan3D-2mini remains validated and preferred for local shape generation.
- Hunyuan3D-2mv is not yet validated locally.
- `pymeshlab` still emits non-blocking `libOpenGL.so.0` plugin warnings.

## Phase 5C Decision

Phase 5C status: not passed locally yet.

Reason:

- Standard Hunyuan3D-2mv failed before inference/mesh export.
- Turbo Hunyuan3D-2mv could not be tested because the model download did not complete, even after a temporary `HF_ENDPOINT=https://hf-mirror.com` mirror retry.

Project route impact:

- Keep Hunyuan3D-2mini as the preferred local shape backend.
- Keep Hunyuan3D-2mv as a thesis-aligned multi-view candidate, but classify it as pending/retry or cloud-assisted.
- Do not block the MVP on Hunyuan3D-2mv.
- Continue preserving the three-view input path in preprocessing/UI design so 2mv can be reintroduced when feasible.

Recommended next step:

- Proceed toward integrating the stable path into the MVP: ControlNet render -> Hunyuan3D-2mini -> mesh report -> Gradio preview.
- Retry Hunyuan3D-2mv later with a completed turbo checkpoint, a cloud GPU, or a cleaner true three-view shoe sketch set.
