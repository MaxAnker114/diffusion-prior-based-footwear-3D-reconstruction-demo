from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import torch
from PIL import Image


CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from postprocess.mesh_report import build_mesh_report  # noqa: E402


def now_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path.resolve())


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Hunyuan3D shape-only inference and export a GLB."
    )
    parser.add_argument("input", type=Path, help="Input shoe image or sketch-derived render.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "code" / "outputs" / "hunyuan3d_runs",
    )
    parser.add_argument("--run-id", default=now_run_id())
    parser.add_argument("--model-path", default="tencent/Hunyuan3D-2mini")
    parser.add_argument("--subfolder", default="hunyuan3d-dit-v2-mini")
    parser.add_argument("--variant", default="fp16")
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--octree-resolution", type=int, default=256)
    parser.add_argument("--num-chunks", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=12345)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input.resolve()
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the planned local Hunyuan3D smoke test.")

    from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline

    run_dir = (args.output_root / args.run_id).resolve()
    mesh_path = run_dir / "mesh.glb"
    reports_dir = run_dir / "reports"
    run_dir.mkdir(parents=True, exist_ok=True)

    image = Image.open(input_path).convert("RGBA")
    torch.cuda.reset_peak_memory_stats()

    load_started = time.perf_counter()
    pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
        args.model_path,
        subfolder=args.subfolder,
        variant=args.variant,
    )
    load_seconds = time.perf_counter() - load_started

    infer_started = time.perf_counter()
    mesh = pipeline(
        image=image,
        num_inference_steps=args.steps,
        octree_resolution=args.octree_resolution,
        num_chunks=args.num_chunks,
        generator=torch.manual_seed(args.seed),
        output_type="trimesh",
    )[0]
    infer_seconds = time.perf_counter() - infer_started
    mesh.export(mesh_path)

    peak_memory_mb = torch.cuda.max_memory_allocated() / 1024 / 1024
    mesh_report = build_mesh_report(mesh_path, project_root=PROJECT_ROOT)

    summary = {
        "run_id": args.run_id,
        "backend": "hunyuan3d_shape",
        "input": relpath(input_path),
        "output_mesh": relpath(mesh_path),
        "model_path": args.model_path,
        "subfolder": args.subfolder,
        "variant": args.variant,
        "steps": args.steps,
        "octree_resolution": args.octree_resolution,
        "num_chunks": args.num_chunks,
        "seed": args.seed,
        "load_seconds": round(load_seconds, 3),
        "infer_seconds": round(infer_seconds, 3),
        "peak_memory_mb": round(peak_memory_mb, 3),
        "mesh_report": mesh_report,
    }
    write_json(reports_dir / "summary.json", summary)
    write_json(reports_dir / "mesh_report.json", {"hunyuan3d_shape": mesh_report})

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
