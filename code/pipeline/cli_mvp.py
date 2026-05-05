from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from postprocess.mesh_report import build_mesh_report  # noqa: E402
from preprocess.sketch_preprocess import preprocess_sketch  # noqa: E402


DEFAULT_PROMPT = (
    "clean side view sneaker product concept render, white background, low top sport shoe, "
    "visible sole, laces, heel counter, toe box, design sketch converted to product rendering"
)


@dataclass
class CommandResult:
    command: list[str] | str
    returncode: int
    elapsed_seconds: float
    stdout: str
    stderr: str


def summarize_command_result(
    result: CommandResult,
    stdout_tail_chars: int = 4000,
    stderr_tail_chars: int = 4000,
) -> dict:
    stdout_truncated = len(result.stdout) > stdout_tail_chars
    stderr_truncated = len(result.stderr) > stderr_tail_chars
    return {
        "command": result.command,
        "returncode": result.returncode,
        "elapsed_seconds": result.elapsed_seconds,
        "stdout_tail": result.stdout[-stdout_tail_chars:],
        "stderr_tail": result.stderr[-stderr_tail_chars:],
        "stdout_truncated": stdout_truncated,
        "stderr_truncated": stderr_truncated,
    }


def ensure_wsl_runtime() -> None:
    if os.name != "posix":
        raise RuntimeError("This CLI MVP is intended to run inside WSL/Linux.")


def now_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path.resolve())


def run_command(command: list[str] | str, cwd: Path | None = None) -> CommandResult:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        shell=isinstance(command, str),
    )
    elapsed = time.perf_counter() - started
    result = CommandResult(
        command=command,
        returncode=completed.returncode,
        elapsed_seconds=elapsed,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {completed.returncode}: {command}\n"
            f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return result


def render_with_controlnet(
    control_image: Path,
    output_image: Path,
    prompt: str,
    steps: int,
    seed: int,
    control_scale: float,
) -> CommandResult:
    command = [
        sys.executable,
        str(CODE_DIR / "controlnet" / "render_from_control.py"),
        str(control_image),
        "--output",
        str(output_image),
        "--prompt",
        prompt,
        "--steps",
        str(steps),
        "--seed",
        str(seed),
        "--control-scale",
        str(control_scale),
        "--size",
        "512",
    ]
    return run_command(command, cwd=PROJECT_ROOT)


def run_sf3d(
    input_image: Path,
    output_dir: Path,
    sf3d_repo: Path,
    conda_profile: Path,
    conda_env: str,
    texture_resolution: int,
) -> CommandResult:
    command = (
        f"source {shlex.quote(str(conda_profile))} && "
        f"conda activate {shlex.quote(conda_env)} && "
        f"cd {shlex.quote(str(sf3d_repo))} && "
        f"python run.py {shlex.quote(str(input_image.resolve()))} "
        f"--output-dir {shlex.quote(str(output_dir.resolve()))} "
        f"--texture-resolution {texture_resolution} "
        f"--remesh_option none "
        f"--batch_size 1"
    )
    return run_command(["bash", "-lc", command], cwd=PROJECT_ROOT)


def run_hunyuan3d_shape(
    input_image: Path,
    output_dir: Path,
    conda_profile: Path,
    conda_env: str,
    model_path: str,
    subfolder: str,
    variant: str,
    steps: int,
    octree_resolution: int,
    num_chunks: int,
    seed: int,
) -> CommandResult:
    command = (
        f"source {shlex.quote(str(conda_profile))} && "
        f"conda activate {shlex.quote(conda_env)} && "
        "export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True && "
        "export HF_HUB_OFFLINE=1 && "
        f"cd {shlex.quote(str(PROJECT_ROOT))} && "
        f"python {shlex.quote(str(CODE_DIR / 'reconstruction' / 'run_hunyuan3d_shape.py'))} "
        f"{shlex.quote(str(input_image.resolve()))} "
        f"--output-root {shlex.quote(str(output_dir.resolve()))} "
        "--run-id result "
        f"--model-path {shlex.quote(model_path)} "
        f"--subfolder {shlex.quote(subfolder)} "
        f"--variant {shlex.quote(variant)} "
        f"--steps {steps} "
        f"--octree-resolution {octree_resolution} "
        f"--num-chunks {num_chunks} "
        f"--seed {seed}"
    )
    return run_command(["bash", "-lc", command], cwd=PROJECT_ROOT)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the MVP footwear sketch-to-3D CLI pipeline."
    )
    parser.add_argument("input", type=Path, help="Single-view designer shoe sketch.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "code" / "outputs" / "pipeline_runs",
    )
    parser.add_argument("--run-id", default=now_run_id())
    parser.add_argument(
        "--mode",
        choices=["direct", "controlnet", "both"],
        default="controlnet",
        help="Which input path to reconstruct.",
    )
    parser.add_argument(
        "--backend",
        choices=["hunyuan3d", "sf3d", "both"],
        default="hunyuan3d",
        help="Which 3D backend to run.",
    )
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--controlnet-steps", type=int, default=12)
    parser.add_argument("--controlnet-seed", type=int, default=114)
    parser.add_argument("--control-scale", type=float, default=0.9)
    parser.add_argument("--texture-resolution", type=int, default=512)
    parser.add_argument("--hunyuan-env", default="hunyuan3d")
    parser.add_argument("--hunyuan-model-path", default="tencent/Hunyuan3D-2mini")
    parser.add_argument("--hunyuan-subfolder", default="hunyuan3d-dit-v2-mini")
    parser.add_argument("--hunyuan-variant", default="fp16")
    parser.add_argument("--hunyuan-steps", type=int, default=30)
    parser.add_argument("--hunyuan-octree-resolution", type=int, default=256)
    parser.add_argument("--hunyuan-num-chunks", type=int, default=20000)
    parser.add_argument("--hunyuan-seed", type=int, default=12345)
    parser.add_argument(
        "--sf3d-repo",
        type=Path,
        default=PROJECT_ROOT / "code" / "third_party" / "stable-fast-3d",
    )
    parser.add_argument(
        "--conda-profile",
        type=Path,
        default=Path("/home/anker/miniforge3/etc/profile.d/conda.sh"),
    )
    parser.add_argument("--sf3d-env", default="sf3d")
    return parser.parse_args()


def main() -> None:
    ensure_wsl_runtime()
    args = parse_args()
    input_path = args.input.resolve()
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    run_dir = (args.output_root / args.run_id).resolve()
    preprocess_dir = run_dir / "preprocess"
    render_dir = run_dir / "controlnet"
    sf3d_dir = run_dir / "sf3d"
    hunyuan_dir = run_dir / "hunyuan3d"
    reports_dir = run_dir / "reports"

    print(f"run_dir: {run_dir}")
    print("step: preprocess")
    preprocess_outputs = preprocess_sketch(
        input_path=input_path,
        output_dir=preprocess_dir,
        size=512,
        threshold=235,
        canny_low=80,
        canny_high=180,
    )

    command_results: dict[str, dict] = {}
    mesh_reports: dict[str, dict] = {}

    reconstruction_inputs: dict[str, Path] = {}

    if args.mode in {"controlnet", "both"}:
        print("step: controlnet render")
        rendered_image = render_dir / "render.png"
        result = render_with_controlnet(
            control_image=preprocess_outputs["canny"],
            output_image=rendered_image,
            prompt=args.prompt,
            steps=args.controlnet_steps,
            seed=args.controlnet_seed,
            control_scale=args.control_scale,
        )
        command_results["controlnet"] = summarize_command_result(result)
        reconstruction_inputs["controlnet_render"] = rendered_image

    if args.mode in {"direct", "both"}:
        reconstruction_inputs["direct_sketch"] = preprocess_outputs["normalized"]

    for input_name, reconstruction_input in reconstruction_inputs.items():
        if args.backend in {"hunyuan3d", "both"}:
            print(f"step: hunyuan3d from {input_name}")
            hunyuan_output = hunyuan_dir / input_name
            result = run_hunyuan3d_shape(
                input_image=reconstruction_input,
                output_dir=hunyuan_output,
                conda_profile=args.conda_profile,
                conda_env=args.hunyuan_env,
                model_path=args.hunyuan_model_path,
                subfolder=args.hunyuan_subfolder,
                variant=args.hunyuan_variant,
                steps=args.hunyuan_steps,
                octree_resolution=args.hunyuan_octree_resolution,
                num_chunks=args.hunyuan_num_chunks,
                seed=args.hunyuan_seed,
            )
            command_results[f"hunyuan3d_{input_name}"] = summarize_command_result(result)
            mesh_reports[f"hunyuan3d_{input_name}"] = build_mesh_report(
                hunyuan_output / "result" / "mesh.glb",
                project_root=PROJECT_ROOT,
            )

        if args.backend in {"sf3d", "both"}:
            print(f"step: sf3d from {input_name}")
            sf3d_output = sf3d_dir / input_name
            result = run_sf3d(
                input_image=reconstruction_input,
                output_dir=sf3d_output,
                sf3d_repo=args.sf3d_repo.resolve(),
                conda_profile=args.conda_profile,
                conda_env=args.sf3d_env,
                texture_resolution=args.texture_resolution,
            )
            command_results[f"sf3d_{input_name}"] = summarize_command_result(result)
            mesh_reports[f"sf3d_{input_name}"] = build_mesh_report(
                sf3d_output / "0" / "mesh.glb",
                project_root=PROJECT_ROOT,
            )

    summary = {
        "run_id": args.run_id,
        "input": relpath(input_path),
        "mode": args.mode,
        "backend": args.backend,
        "preprocess_outputs": {
            name: relpath(path) for name, path in preprocess_outputs.items()
        },
        "reconstruction_inputs": {
            name: relpath(path) for name, path in reconstruction_inputs.items()
        },
        "mesh_reports": mesh_reports,
        "commands": command_results,
    }
    write_json(reports_dir / "summary.json", summary)
    write_json(reports_dir / "mesh_report.json", mesh_reports)

    print(f"summary: {reports_dir / 'summary.json'}")
    print(f"mesh_report: {reports_dir / 'mesh_report.json'}")


if __name__ == "__main__":
    main()
