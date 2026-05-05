#!/usr/bin/env bash
set -euo pipefail

source /home/anker/miniforge3/etc/profile.d/conda.sh
conda activate hunyuan3d

cd /mnt/d/Final_Project
export GRADIO_ANALYTICS_ENABLED=False

python code/ui/app.py --host "${GRADIO_HOST:-0.0.0.0}" --port "${GRADIO_PORT:-7860}"
