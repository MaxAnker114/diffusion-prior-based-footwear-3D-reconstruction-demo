from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

import gradio as gr


CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
CLI_PATH = CODE_DIR / "pipeline" / "cli_mvp.py"
OUTPUT_ROOT = CODE_DIR / "outputs" / "pipeline_runs"
UPLOAD_ROOT = CODE_DIR / "outputs" / "ui_uploads"
CONDA_PROFILE = Path("/home/anker/miniforge3/etc/profile.d/conda.sh")
CLI_ENV = "trellis310"

DEFAULT_PROMPT = (
    "clean side view sneaker product concept render, white background, low top sport shoe, "
    "visible sole, laces, heel counter, toe box, design sketch converted to product rendering"
)


def _run_id() -> str:
    return datetime.now().strftime("ui_%Y%m%d_%H%M%S")


def _copy_input(input_path: str | Path, run_id: str) -> Path:
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(source)

    suffix = source.suffix.lower() or ".png"
    target_dir = UPLOAD_ROOT / run_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"input{suffix}"
    shutil.copy2(source, target)
    return target.resolve()


def _rel_to_abs(path_value: str | None) -> str | None:
    if not path_value:
        return None
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return str(path.resolve()) if path.exists() else None


def _first_existing(values: list[str | None]) -> str | None:
    for value in values:
        resolved = _rel_to_abs(value)
        if resolved:
            return resolved
    return None


def _select_report(summary: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    preferred_order = [
        "hunyuan3d_controlnet_render",
        "hunyuan3d_direct_sketch",
        "sf3d_controlnet_render",
        "sf3d_direct_sketch",
    ]
    reports = summary.get("mesh_reports") or {}
    for key in preferred_order:
        report = reports.get(key)
        if report:
            return key, report
    if reports:
        key = next(iter(reports))
        return key, reports[key]
    return None, {}


def _table_rows(items: list[dict[str, Any]]) -> list[list[str]]:
    return [[str(item.get("label", "")), str(item.get("value", ""))] for item in items]


def _warning_rows(items: list[dict[str, Any]]) -> list[list[str]]:
    return [
        [
            str(item.get("severity", "")),
            str(item.get("code", "")),
            str(item.get("message", "")),
        ]
        for item in items
    ]


def _command_status(summary: dict[str, Any]) -> str:
    lines = [
        f"run_id: {summary.get('run_id')}",
        f"mode: {summary.get('mode')}",
        f"backend: {summary.get('backend')}",
    ]
    commands = summary.get("commands") or {}
    for name, command in commands.items():
        elapsed = float(command.get("elapsed_seconds", 0.0))
        lines.append(f"{name}: exit {command.get('returncode')} / {elapsed:.1f}s")
    return "\n".join(lines)


def _run_cli(
    input_image: str,
    mode: str,
    backend: str,
    prompt: str,
    controlnet_steps: int,
    control_scale: float,
    hunyuan_steps: int,
    hunyuan_octree_resolution: int,
    hunyuan_seed: int,
) -> dict[str, Any]:
    run_id = _run_id()
    copied_input = _copy_input(input_image, run_id)
    command = (
        f"source {shlex.quote(str(CONDA_PROFILE))} && "
        f"conda activate {shlex.quote(CLI_ENV)} && "
        f"cd {shlex.quote(str(PROJECT_ROOT))} && "
        f"python {shlex.quote(str(CLI_PATH))} "
        f"{shlex.quote(str(copied_input))} "
        f"--output-root {shlex.quote(str(OUTPUT_ROOT))} "
        f"--run-id {shlex.quote(run_id)} "
        f"--mode {shlex.quote(mode)} "
        f"--backend {shlex.quote(backend)} "
        f"--prompt {shlex.quote(prompt)} "
        f"--controlnet-steps {int(controlnet_steps)} "
        f"--control-scale {float(control_scale)} "
        f"--hunyuan-steps {int(hunyuan_steps)} "
        f"--hunyuan-octree-resolution {int(hunyuan_octree_resolution)} "
        f"--hunyuan-seed {int(hunyuan_seed)}"
    )

    completed = subprocess.run(
        ["bash", "-lc", command],
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
        timeout=3600,
    )
    if completed.returncode != 0:
        raise gr.Error(
            "Pipeline failed.\n\n"
            f"STDOUT tail:\n{completed.stdout[-3000:]}\n\n"
            f"STDERR tail:\n{completed.stderr[-3000:]}"
        )

    summary_path = OUTPUT_ROOT / run_id / "reports" / "summary.json"
    if not summary_path.exists():
        raise gr.Error(f"Pipeline finished but summary was not found: {summary_path}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["_summary_path"] = str(summary_path.resolve())
    summary["_copied_input"] = str(copied_input)
    return summary


def run_demo(
    input_image: str | None,
    mode: str,
    backend: str,
    prompt: str,
    controlnet_steps: int,
    control_scale: float,
    hunyuan_steps: int,
    hunyuan_octree_resolution: int,
    hunyuan_seed: int,
) -> tuple[Any, ...]:
    if not input_image:
        raise gr.Error("Please upload a single-view shoe sketch or rendered shoe image.")

    summary = _run_cli(
        input_image=input_image,
        mode=mode,
        backend=backend,
        prompt=prompt,
        controlnet_steps=controlnet_steps,
        control_scale=control_scale,
        hunyuan_steps=hunyuan_steps,
        hunyuan_octree_resolution=hunyuan_octree_resolution,
        hunyuan_seed=hunyuan_seed,
    )

    preprocess = summary.get("preprocess_outputs") or {}
    report_key, report = _select_report(summary)
    mesh_path = _rel_to_abs(report.get("path")) if report else None
    warnings = report.get("warnings", []) if report else []

    render_path = _first_existing(
        [
            (summary.get("reconstruction_inputs") or {}).get("controlnet_render"),
            None,
        ]
    )

    status = _command_status(summary)
    if report_key:
        status += f"\nselected_report: {report_key}"

    return (
        _rel_to_abs(summary.get("_copied_input")),
        _rel_to_abs(preprocess.get("normalized")),
        _rel_to_abs(preprocess.get("canny")),
        render_path,
        mesh_path,
        _table_rows(report.get("display_summary", [])) if report else [],
        _warning_rows(warnings),
        status,
        mesh_path,
        summary.get("_summary_path"),
    )


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="Footwear 3D Reconstruction") as demo:
        gr.Markdown("# Footwear 3D Reconstruction")

        with gr.Row(equal_height=False):
            with gr.Column(scale=4, min_width=340):
                input_image = gr.Image(
                    label="Input sketch / render",
                    type="filepath",
                    sources=["upload"],
                    height=320,
                )
                with gr.Row():
                    mode = gr.Radio(
                        ["direct", "controlnet", "both"],
                        value="direct",
                        label="Input path",
                    )
                    backend = gr.Radio(
                        ["hunyuan3d", "sf3d", "both"],
                        value="hunyuan3d",
                        label="3D backend",
                    )
                prompt = gr.Textbox(
                    value=DEFAULT_PROMPT,
                    label="ControlNet prompt",
                    lines=3,
                )
                with gr.Row():
                    controlnet_steps = gr.Slider(
                        4,
                        30,
                        value=8,
                        step=1,
                        label="ControlNet steps",
                    )
                    control_scale = gr.Slider(
                        0.2,
                        1.4,
                        value=0.9,
                        step=0.05,
                        label="Control scale",
                    )
                with gr.Row():
                    hunyuan_steps = gr.Slider(
                        5,
                        50,
                        value=30,
                        step=1,
                        label="Hunyuan steps",
                    )
                    hunyuan_octree_resolution = gr.Dropdown(
                        [128, 192, 256],
                        value=256,
                        label="Octree resolution",
                    )
                    hunyuan_seed = gr.Number(
                        value=12345,
                        precision=0,
                        label="Seed",
                    )
                run_button = gr.Button("Run", variant="primary", elem_id="run-button")

            with gr.Column(scale=5, min_width=480):
                model = gr.Model3D(label="Generated mesh", height=420)
                with gr.Row():
                    mesh_file = gr.File(label="GLB")
                    summary_file = gr.File(label="Summary JSON")
                status = gr.Textbox(label="Run status", lines=8, interactive=False)

        with gr.Row():
            copied_input = gr.Image(label="Copied input", type="filepath", height=220)
            normalized = gr.Image(label="Normalized", type="filepath", height=220)
            canny = gr.Image(label="Canny", type="filepath", height=220)
            render = gr.Image(label="ControlNet render", type="filepath", height=220)

        with gr.Row():
            metrics = gr.Dataframe(
                headers=["Metric", "Value"],
                datatype=["str", "str"],
                label="Mesh metrics",
                interactive=False,
                wrap=True,
            )
            warnings = gr.Dataframe(
                headers=["Severity", "Code", "Message"],
                datatype=["str", "str", "str"],
                label="Warnings",
                interactive=False,
                wrap=True,
            )

        run_button.click(
            fn=run_demo,
            inputs=[
                input_image,
                mode,
                backend,
                prompt,
                controlnet_steps,
                control_scale,
                hunyuan_steps,
                hunyuan_octree_resolution,
                hunyuan_seed,
            ],
            outputs=[
                copied_input,
                normalized,
                canny,
                render,
                model,
                metrics,
                warnings,
                status,
                mesh_file,
                summary_file,
            ],
            show_progress="full",
            concurrency_limit=1,
        )

    return demo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the Gradio UI MVP.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--share", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    demo = build_demo()
    demo.queue(default_concurrency_limit=1)
    demo.launch(server_name=args.host, server_port=args.port, share=args.share)


if __name__ == "__main__":
    main()
