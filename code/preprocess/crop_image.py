from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def parse_box(value: str) -> tuple[int, int, int, int]:
    parts = [int(part.strip()) for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("box must be left,top,right,bottom")
    left, top, right, bottom = parts
    if right <= left or bottom <= top:
        raise argparse.ArgumentTypeError("box must satisfy right > left and bottom > top")
    return left, top, right, bottom


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crop and optionally rotate an image.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--box", type=parse_box, required=True, help="left,top,right,bottom")
    parser.add_argument(
        "--rotate",
        type=float,
        default=0.0,
        help="Degrees counter-clockwise. Use negative values for clockwise rotation.",
    )
    parser.add_argument("--expand", action="store_true", help="Expand canvas after rotation.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(args.input).convert("RGB")
    cropped = image.crop(args.box)
    if args.rotate:
        cropped = cropped.rotate(args.rotate, expand=args.expand, fillcolor=(255, 255, 255))
    cropped.save(args.output)
    print(f"output: {args.output}")


if __name__ == "__main__":
    main()
