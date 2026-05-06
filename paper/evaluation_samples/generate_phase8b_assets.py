from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_ROOT = PROJECT_ROOT / "paper" / "evaluation_samples"
SCREENSHOT_ROOT = SAMPLE_ROOT / "screenshots"
MANIFEST_PATH = SAMPLE_ROOT / "phase8a_manifest.json"
METRICS_PATH = SAMPLE_ROOT / "phase8a_metrics.csv"

CANVAS_BG = (248, 249, 250)
PANEL_BG = (255, 255, 255)
INK = (34, 37, 41)
MUTED = (93, 101, 110)
GRID = (218, 223, 229)
ACCENT = (25, 102, 168)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT_TITLE = font(30, bold=True)
FONT_H2 = font(22, bold=True)
FONT_BODY = font(18)
FONT_SMALL = font(15)
FONT_TABLE = font(15)
FONT_TABLE_BOLD = font(15, bold=True)


def resolve(path_value: str | None) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    max_width: int,
    text_font: ImageFont.ImageFont,
    fill: tuple[int, int, int] = INK,
    line_gap: int = 4,
) -> int:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=text_font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    x, y = xy
    line_height = draw.textbbox((0, 0), "Ag", font=text_font)[3] + line_gap
    for line in lines:
        draw.text((x, y), line, font=text_font, fill=fill)
        y += line_height
    return y


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str | None = None) -> None:
    draw.rounded_rectangle(box, radius=8, fill=PANEL_BG, outline=GRID, width=1)
    if title:
        draw.text((box[0] + 18, box[1] + 14), title, font=FONT_H2, fill=INK)


def load_image(path: Path | None, size: tuple[int, int]) -> Image.Image:
    image = Image.new("RGB", size, PANEL_BG)
    if path and path.exists():
        source = Image.open(path).convert("RGB")
        source = ImageOps.contain(source, (size[0] - 24, size[1] - 62), method=Image.Resampling.LANCZOS)
        x = (size[0] - source.width) // 2
        y = 46 + (size[1] - 62 - source.height) // 2
        image.paste(source, (x, y))
    return image


def image_panel(path: Path | None, title: str, size: tuple[int, int] = (440, 320)) -> Image.Image:
    output = load_image(path, size)
    draw = ImageDraw.Draw(output)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=8, outline=GRID, width=1)
    draw.text((18, 14), title, font=FONT_H2, fill=INK)
    return output


def scene_to_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(path, force="scene")
    if isinstance(loaded, trimesh.Scene):
        meshes = []
        for geometry in loaded.geometry.values():
            if isinstance(geometry, trimesh.Trimesh) and len(geometry.faces) > 0:
                meshes.append(geometry)
        if not meshes:
            raise ValueError(f"No usable mesh geometry found in {path}")
        return trimesh.util.concatenate(meshes)
    if isinstance(loaded, trimesh.Trimesh):
        return loaded
    raise TypeError(f"Unsupported mesh type for {path}: {type(loaded)!r}")


def rotation_matrix(yaw: float, pitch: float, roll: float = 0.0) -> np.ndarray:
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cr, sr = math.cos(roll), math.sin(roll)
    rz = np.array([[cr, -sr, 0.0], [sr, cr, 0.0], [0.0, 0.0, 1.0]])
    ry = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]])
    rx = np.array([[1.0, 0.0, 0.0], [0.0, cp, -sp], [0.0, sp, cp]])
    return rz @ rx @ ry


def render_mesh_preview(
    mesh_path: Path,
    size: tuple[int, int] = (560, 420),
    yaw: float = math.radians(35),
    pitch: float = math.radians(-20),
) -> Image.Image:
    mesh = scene_to_mesh(mesh_path)
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > 70000:
        step = max(1, int(math.ceil(len(faces) / 70000)))
        faces = faces[::step]

    center = (vertices.min(axis=0) + vertices.max(axis=0)) / 2.0
    vertices = vertices - center
    rot = rotation_matrix(yaw=yaw, pitch=pitch)
    rv = vertices @ rot.T

    xy = rv[:, :2]
    span = xy.max(axis=0) - xy.min(axis=0)
    scale = min((size[0] - 70) / max(span[0], 1e-6), (size[1] - 70) / max(span[1], 1e-6))
    screen = xy * scale
    screen[:, 0] += size[0] / 2.0
    screen[:, 1] = size[1] / 2.0 - screen[:, 1]

    face_vertices = rv[faces]
    depths = face_vertices[:, :, 2].mean(axis=1)
    normals = np.cross(face_vertices[:, 1] - face_vertices[:, 0], face_vertices[:, 2] - face_vertices[:, 0])
    normal_norm = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = np.divide(normals, np.maximum(normal_norm, 1e-9))
    light = np.array([0.25, -0.35, 0.9], dtype=np.float64)
    light = light / np.linalg.norm(light)
    shade = np.clip(normals @ light, 0.0, 1.0)

    image = Image.new("RGB", size, (246, 248, 250))
    draw = ImageDraw.Draw(image)
    order = np.argsort(depths)
    base = np.array([89, 143, 191], dtype=np.float64)
    for idx in order:
        pts = [(float(screen[v, 0]), float(screen[v, 1])) for v in faces[idx]]
        value = 0.42 + 0.58 * float(shade[idx])
        color = tuple(np.clip(base * value + 38, 0, 255).astype(int).tolist())
        draw.polygon(pts, fill=color)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=8, outline=GRID, width=1)
    return image


def mesh_panel(mesh_path: Path | None, title: str, size: tuple[int, int] = (560, 420)) -> Image.Image:
    image = Image.new("RGB", size, PANEL_BG)
    if mesh_path and mesh_path.exists():
        try:
            image = render_mesh_preview(mesh_path, size=size)
        except Exception as exc:
            draw = ImageDraw.Draw(image)
            draw_wrapped(draw, f"Mesh preview failed: {exc}", (18, 72), size[0] - 36, FONT_BODY, fill=(160, 45, 45))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, size[0], 52), fill=(255, 255, 255))
    draw.text((18, 14), title, font=FONT_H2, fill=INK)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=8, outline=GRID, width=1)
    return image


def read_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def read_metrics() -> list[dict[str, str]]:
    with METRICS_PATH.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def draw_table(rows: list[dict[str, str]], output_path: Path) -> None:
    columns = [
        ("sample_id", "ID", 70),
        ("backend", "Backend", 170),
        ("path_mode", "Path", 110),
        ("vertices", "Vertices", 110),
        ("faces", "Faces", 110),
        ("components", "Components", 130),
        ("thickness_proxy_ratio", "Thickness", 120),
        ("volume", "Volume", 120),
        ("elapsed_seconds", "Seconds", 105),
        ("peak_vram_mb", "VRAM MB", 120),
    ]
    width = sum(item[2] for item in columns) + 80
    row_h = 46
    height = 140 + row_h * (len(rows) + 1)
    image = Image.new("RGB", (width, height), CANVAS_BG)
    draw = ImageDraw.Draw(image)
    draw.text((40, 32), "Phase 8A Mesh Metric Summary", font=FONT_TITLE, fill=INK)
    draw.text((40, 74), "Frozen samples for thesis/demo comparison", font=FONT_BODY, fill=MUTED)

    x = 40
    y = 118
    draw.rectangle((x, y, width - 40, y + row_h), fill=(235, 240, 245), outline=GRID)
    cx = x
    for key, label, col_w in columns:
        draw.text((cx + 10, y + 13), label, font=FONT_TABLE_BOLD, fill=INK)
        cx += col_w
        draw.line((cx, y, cx, y + row_h * (len(rows) + 1)), fill=GRID)

    for row_idx, row in enumerate(rows):
        y0 = y + row_h * (row_idx + 1)
        fill = PANEL_BG if row_idx % 2 == 0 else (248, 250, 252)
        draw.rectangle((x, y0, width - 40, y0 + row_h), fill=fill, outline=GRID)
        cx = x
        for key, label, col_w in columns:
            value = row.get(key, "")
            draw.text((cx + 10, y0 + 13), value, font=FONT_TABLE, fill=INK)
            cx += col_w

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def sample_sheet(sample: dict[str, Any], metric: dict[str, str]) -> Image.Image:
    width, height = 1600, 1120
    image = Image.new("RGB", (width, height), CANVAS_BG)
    draw = ImageDraw.Draw(image)
    title = f"{sample['id']} - {sample['label']}"
    draw.text((42, 34), title, font=FONT_TITLE, fill=INK)
    draw.text((42, 78), f"Run: {sample['run_id']} | Backend: {sample['backend']} | Path: {sample['path_mode']}", font=FONT_BODY, fill=MUTED)

    cards = [
        image_panel(resolve(sample.get("input")), "Input"),
        image_panel(resolve(sample.get("normalized")), "Normalized") if sample.get("normalized") else image_panel(resolve(sample.get("input")), "Reconstruction Input"),
        image_panel(resolve(sample.get("canny")), "Canny") if sample.get("canny") else image_panel(None, "Canny / Control"),
    ]
    x = 42
    y = 130
    for card in cards:
        image.paste(card, (x, y))
        x += card.width + 24

    mesh = mesh_panel(resolve(sample.get("mesh")), "Generated Mesh Preview", size=(720, 520))
    image.paste(mesh, (42, 500))

    metrics_box = (800, 500, 1558, 1020)
    panel(draw, metrics_box, "Metrics")
    metric_lines = [
        ("Vertices", metric.get("vertices", "")),
        ("Faces", metric.get("faces", "")),
        ("Components", metric.get("components", "")),
        ("Bounds", metric.get("bounds_dimensions", "")),
        ("Thickness proxy", metric.get("thickness_proxy_ratio", "")),
        ("Watertight", metric.get("watertight", "")),
        ("Volume", metric.get("volume", "")),
        ("Runtime", f"{metric.get('elapsed_seconds', '')} s"),
        ("Peak VRAM", f"{metric.get('peak_vram_mb', '')} MB"),
        ("Warnings", metric.get("warnings", "")),
    ]
    yy = 560
    for label, value in metric_lines:
        draw.text((830, yy), f"{label}:", font=FONT_TABLE_BOLD, fill=INK)
        yy = draw_wrapped(draw, value, (1020, yy), 500, FONT_TABLE, fill=MUTED, line_gap=3)
        yy += 8

    return image


def comparison_grid(samples: list[dict[str, Any]], metrics: dict[str, dict[str, str]], output_path: Path) -> None:
    tile_w, tile_h = 760, 620
    image = Image.new("RGB", (1600, 1420), CANVAS_BG)
    draw = ImageDraw.Draw(image)
    draw.text((42, 34), "Phase 8B Evaluation Sample Overview", font=FONT_TITLE, fill=INK)
    draw.text((42, 78), "Input and mesh previews for the frozen paper/demo samples", font=FONT_BODY, fill=MUTED)
    positions = [(42, 130), (820, 130), (42, 770), (820, 770)]
    for sample, pos in zip(samples, positions):
        metric = metrics[sample["id"]]
        x, y = pos
        panel(draw, (x, y, x + tile_w, y + tile_h))
        draw.text((x + 22, y + 18), f"{sample['id']} - {sample['backend']}", font=FONT_H2, fill=INK)
        draw.text((x + 22, y + 50), sample["label"], font=FONT_SMALL, fill=MUTED)
        input_img = image_panel(resolve(sample.get("input")), "Input", size=(300, 230))
        mesh_img = mesh_panel(resolve(sample.get("mesh")), "Mesh", size=(390, 300))
        image.paste(input_img, (x + 22, y + 90))
        image.paste(mesh_img, (x + 342, y + 90))
        rows = [
            f"Vertices/Faces: {metric.get('vertices')} / {metric.get('faces')}",
            f"Components: {metric.get('components')}",
            f"Thickness: {metric.get('thickness_proxy_ratio')}",
            f"Volume: {metric.get('volume')}",
            f"Runtime: {metric.get('elapsed_seconds')} s",
            f"Peak VRAM: {metric.get('peak_vram_mb')} MB",
        ]
        yy = y + 420
        for row in rows:
            draw.text((x + 30, yy), row, font=FONT_BODY, fill=INK)
            yy += 32
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def main() -> None:
    SCREENSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    manifest = read_manifest()
    metrics_rows = read_metrics()
    metrics_by_id = {row["sample_id"]: row for row in metrics_rows}

    draw_table(metrics_rows, SCREENSHOT_ROOT / "phase8b_metrics_table.png")

    samples = manifest["samples"]
    for sample in samples:
        sheet = sample_sheet(sample, metrics_by_id[sample["id"]])
        sheet.save(SCREENSHOT_ROOT / f"phase8b_{sample['id'].lower()}_sample_sheet.png")
        mesh_path = resolve(sample.get("mesh"))
        if mesh_path:
            mesh_panel(mesh_path, f"{sample['id']} Mesh Preview", size=(1200, 860)).save(
                SCREENSHOT_ROOT / f"phase8b_{sample['id'].lower()}_mesh_preview.png"
            )

    comparison_grid(samples, metrics_by_id, SCREENSHOT_ROOT / "phase8b_comparison_grid.png")

    index = {
        "phase": "8B",
        "date": "2026-05-06",
        "outputs": sorted(str(path.relative_to(SAMPLE_ROOT)) for path in SCREENSHOT_ROOT.glob("*.png")),
    }
    (SCREENSHOT_ROOT / "phase8b_screenshot_index.json").write_text(
        json.dumps(index, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
