from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


REPORT_VERSION = "0.2.0"


@dataclass(frozen=True)
class WarningRule:
    code: str
    severity: str
    message: str


def _safe_relpath(path: Path, root: Path | None) -> str:
    resolved = path.resolve()
    if root is None:
        return str(resolved)
    try:
        return str(resolved.relative_to(root.resolve()))
    except ValueError:
        return str(resolved)


def _round_float(value: Any, digits: int = 6) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(numeric):
        return None
    return round(numeric, digits)


def _round_list(values: Any, digits: int = 6) -> list[float] | None:
    if values is None:
        return None
    array = np.asarray(values, dtype=float)
    if array.size == 0 or not np.all(np.isfinite(array)):
        return None
    return [round(float(item), digits) for item in array.reshape(-1).tolist()]


def _bounds_dict(bounds: Any) -> dict[str, Any] | None:
    array = np.asarray(bounds, dtype=float)
    if array.shape != (2, 3) or not np.all(np.isfinite(array)):
        return None

    dimensions = array[1] - array[0]
    sorted_dims = np.sort(dimensions)
    max_dim = float(sorted_dims[-1]) if sorted_dims.size else 0.0
    min_dim = float(sorted_dims[0]) if sorted_dims.size else 0.0
    mid_dim = float(sorted_dims[1]) if sorted_dims.size >= 2 else 0.0

    return {
        "min": _round_list(array[0]),
        "max": _round_list(array[1]),
        "dimensions": _round_list(dimensions),
        "sorted_dimensions": _round_list(sorted_dims),
        "longest_dimension": _round_float(max_dim),
        "middle_dimension": _round_float(mid_dim),
        "smallest_dimension": _round_float(min_dim),
        "smallest_to_longest_ratio": _round_float(min_dim / max_dim)
        if max_dim > 0
        else None,
        "middle_to_longest_ratio": _round_float(mid_dim / max_dim)
        if max_dim > 0
        else None,
    }


def _mesh_components(mesh: trimesh.Trimesh) -> dict[str, Any]:
    try:
        parts = mesh.split(only_watertight=False)
    except Exception:
        parts = []

    face_counts = sorted((int(len(getattr(part, "faces", []))) for part in parts), reverse=True)
    return {
        "component_count": len(parts),
        "largest_component_faces": face_counts[0] if face_counts else 0,
        "component_face_counts_top5": face_counts[:5],
    }


def _geometry_report(name: str, mesh: trimesh.Trimesh) -> dict[str, Any]:
    vertices = int(len(getattr(mesh, "vertices", [])))
    faces = int(len(getattr(mesh, "faces", [])))
    bounds = _bounds_dict(getattr(mesh, "bounds", None))
    components = _mesh_components(mesh) if faces > 0 else {
        "component_count": 0,
        "largest_component_faces": 0,
        "component_face_counts_top5": [],
    }
    is_watertight = bool(getattr(mesh, "is_watertight", False))

    return {
        "name": name,
        "vertices": vertices,
        "faces": faces,
        "bounds": bounds,
        "surface_area": _round_float(getattr(mesh, "area", None)),
        "is_watertight": is_watertight,
        "volume_if_watertight": _round_float(getattr(mesh, "volume", None))
        if is_watertight
        else None,
        "euler_number": int(getattr(mesh, "euler_number", 0)) if faces > 0 else None,
        **components,
    }


def _iter_meshes(loaded: Any) -> list[tuple[str, trimesh.Trimesh]]:
    if isinstance(loaded, trimesh.Scene):
        meshes: list[tuple[str, trimesh.Trimesh]] = []
        for name, geometry in loaded.geometry.items():
            if isinstance(geometry, trimesh.Trimesh):
                meshes.append((str(name), geometry))
        return meshes
    if isinstance(loaded, trimesh.Trimesh):
        return [("mesh", loaded)]
    return []


def _aggregate_bounds(meshes: list[tuple[str, trimesh.Trimesh]]) -> dict[str, Any] | None:
    valid_bounds = []
    for _, mesh in meshes:
        bounds = np.asarray(getattr(mesh, "bounds", None), dtype=float)
        if bounds.shape == (2, 3) and np.all(np.isfinite(bounds)):
            valid_bounds.append(bounds)

    if not valid_bounds:
        return None

    stacked = np.stack(valid_bounds)
    combined = np.array([stacked[:, 0, :].min(axis=0), stacked[:, 1, :].max(axis=0)])
    return _bounds_dict(combined)


def _build_warnings(
    file_exists: bool,
    aggregate: dict[str, Any],
    geometries: list[dict[str, Any]],
) -> list[dict[str, str]]:
    warnings: list[WarningRule] = []

    if not file_exists:
        warnings.append(
            WarningRule("missing_file", "error", "The mesh file does not exist.")
        )

    total_vertices = int(aggregate.get("total_vertices", 0))
    total_faces = int(aggregate.get("total_faces", 0))
    if total_vertices == 0 or total_faces == 0:
        warnings.append(
            WarningRule("empty_mesh", "error", "The mesh has no usable vertices or faces.")
        )

    bounds = aggregate.get("bounds")
    smallest_ratio = bounds.get("smallest_to_longest_ratio") if bounds else None
    if smallest_ratio is not None and smallest_ratio < 0.08:
        warnings.append(
            WarningRule(
                "very_flat_geometry",
                "warning",
                "The smallest bounding-box dimension is very low compared with the longest dimension; this often indicates a flat or collapsed reconstruction.",
            )
        )
    elif smallest_ratio is not None and smallest_ratio < 0.16:
        warnings.append(
            WarningRule(
                "thin_geometry",
                "info",
                "The mesh is thin relative to its length; review shoe width/thickness and hidden-side reconstruction manually.",
            )
        )

    total_components = int(aggregate.get("component_count", 0))
    if total_components > max(6, len(geometries) * 4):
        warnings.append(
            WarningRule(
                "many_components",
                "warning",
                "The mesh is split into many connected components; small floating fragments may need cleanup.",
            )
        )

    non_watertight = [
        item["name"] for item in geometries if item.get("faces", 0) > 0 and not item.get("is_watertight")
    ]
    if non_watertight:
        warnings.append(
            WarningRule(
                "non_watertight_mesh",
                "info",
                "At least one geometry is non-watertight, so volume is not a reliable metric.",
            )
        )

    warnings.append(
        WarningRule(
            "internal_structure_not_validated",
            "research_risk",
            "Automatic mesh metrics cannot verify shoe interior plausibility from a single exterior sketch; inspect internal geometry separately and document hidden-structure uncertainty.",
        )
    )

    return [warning.__dict__ for warning in warnings]


def build_mesh_report(glb_path: Path, project_root: Path | None = None) -> dict[str, Any]:
    glb_path = glb_path.resolve()
    file_exists = glb_path.exists()
    report: dict[str, Any] = {
        "report_version": REPORT_VERSION,
        "path": _safe_relpath(glb_path, project_root),
        "exists": file_exists,
        "size_bytes": glb_path.stat().st_size if file_exists else 0,
    }

    if not file_exists:
        aggregate = {
            "total_vertices": 0,
            "total_faces": 0,
            "geometry_count": 0,
            "component_count": 0,
            "bounds": None,
        }
        report.update(
            {
                "type": None,
                "is_valid": False,
                "geometries": [],
                "aggregate": aggregate,
                "display_summary": _display_summary(aggregate),
                "warnings": _build_warnings(False, aggregate, []),
            }
        )
        return report

    loaded = trimesh.load(glb_path)
    meshes = _iter_meshes(loaded)
    geometries = [_geometry_report(name, mesh) for name, mesh in meshes]
    aggregate = {
        "geometry_count": len(geometries),
        "total_vertices": int(sum(item["vertices"] for item in geometries)),
        "total_faces": int(sum(item["faces"] for item in geometries)),
        "component_count": int(sum(item.get("component_count", 0) for item in geometries)),
        "bounds": _aggregate_bounds(meshes),
        "surface_area_total": _round_float(
            sum(item.get("surface_area") or 0.0 for item in geometries)
        ),
        "all_watertight": bool(geometries)
        and all(bool(item.get("is_watertight")) for item in geometries),
    }
    aggregate["volume_total_if_all_watertight"] = _round_float(
        sum(item.get("volume_if_watertight") or 0.0 for item in geometries)
    ) if aggregate["all_watertight"] else None

    report.update(
        {
            "type": type(loaded).__name__,
            "is_valid": aggregate["total_vertices"] > 0 and aggregate["total_faces"] > 0,
            "geometries": geometries,
            "aggregate": aggregate,
            "display_summary": _display_summary(aggregate),
            "warnings": _build_warnings(True, aggregate, geometries),
        }
    )
    return report


def _display_summary(aggregate: dict[str, Any]) -> list[dict[str, str]]:
    bounds = aggregate.get("bounds") or {}
    return [
        {"label": "Geometry count", "value": str(aggregate.get("geometry_count", 0))},
        {"label": "Vertices", "value": str(aggregate.get("total_vertices", 0))},
        {"label": "Faces", "value": str(aggregate.get("total_faces", 0))},
        {"label": "Connected components", "value": str(aggregate.get("component_count", 0))},
        {
            "label": "Bounds dimensions",
            "value": str(bounds.get("dimensions")) if bounds else "n/a",
        },
        {
            "label": "Thickness proxy ratio",
            "value": str(bounds.get("smallest_to_longest_ratio")) if bounds else "n/a",
        },
        {
            "label": "Surface area",
            "value": str(aggregate.get("surface_area_total")),
        },
        {
            "label": "Volume",
            "value": str(aggregate.get("volume_total_if_all_watertight"))
            if aggregate.get("volume_total_if_all_watertight") is not None
            else "n/a",
        },
    ]


def write_mesh_report(glb_path: Path, output_path: Path, project_root: Path | None = None) -> dict[str, Any]:
    report = build_mesh_report(glb_path=glb_path, project_root=project_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a paper/UI-friendly GLB mesh report.")
    parser.add_argument("input", type=Path, help="Path to a GLB/mesh file.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    parser.add_argument("--project-root", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_mesh_report(glb_path=args.input, project_root=args.project_root)
    payload = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
