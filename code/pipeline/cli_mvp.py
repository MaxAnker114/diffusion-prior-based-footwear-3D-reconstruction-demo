from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
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
        help="Which SF3D path to run.",
    )
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--controlnet-steps", type=int, default=12)
    parser.add_argument("--controlnet-seed", type=int, default=114)
    parser.add_argument("--control-scale", type=float, default=0.9)
    parser.add_argument("--texture-resolution", type=int, default=512)
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
        command_results["controlnet"] = asdict(result)

        print("step: sf3d from controlnet render")
        sf3d_output = sf3d_dir / "controlnet_render"
        result = run_sf3d(
            input_image=rendered_image,
            output_dir=sf3d_output,
            sf3d_repo=args.sf3d_repo.resolve(),
            conda_profile=args.conda_profile,
            conda_env=args.sf3d_env,
            texture_resolution=args.texture_resolution,
        )
        command_results["sf3d_controlnet"] = asdict(result)
        mesh_reports["controlnet_render"] = build_mesh_report(
            sf3d_output / "0" / "mesh.glb",
            project_root=PROJECT_ROOT,
        )

    if args.mode in {"direct", "both"}:
        print("step: sf3d direct from normalized sketch")
        sf3d_output = sf3d_dir / "direct_sketch"
        result = run_sf3d(
            input_image=preprocess_outputs["normalized"],
            output_dir=sf3d_output,
            sf3d_repo=args.sf3d_repo.resolve(),
            conda_profile=args.conda_profile,
            conda_env=args.sf3d_env,
            texture_resolution=args.texture_resolution,
        )
        command_results["sf3d_direct"] = asdict(result)
        mesh_reports["direct_sketch"] = build_mesh_report(
            sf3d_output / "0" / "mesh.glb",
            project_root=PROJECT_ROOT,
        )

    summary = {
        "run_id": args.run_id,
        "input": relpath(input_path),
        "mode": args.mode,
        "preprocess_outputs": {
            name: relpath(path) for name, path in preprocess_outputs.items()
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
