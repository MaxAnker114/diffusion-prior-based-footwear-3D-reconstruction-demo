from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


def load_rgb(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    background.alpha_composite(image)
    return background.convert("RGB")


def square_pad(image: Image.Image, fill: int = 255) -> Image.Image:
    width, height = image.size
    side = max(width, height)
    canvas = Image.new("RGB", (side, side), (fill, fill, fill))
    offset = ((side - width) // 2, (side - height) // 2)
    canvas.paste(image, offset)
    return canvas


def resize_image(image: Image.Image, size: int) -> Image.Image:
    return image.resize((size, size), Image.Resampling.LANCZOS)


def make_binary_line(gray: np.ndarray, threshold: int) -> np.ndarray:
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return binary


def make_canny(gray: np.ndarray, low: int, high: int) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, low, high)
    return edges


def preprocess_sketch(
    input_path: Path,
    output_dir: Path,
    size: int,
    threshold: int,
    canny_low: int,
    canny_high: int,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem

    rgb = resize_image(square_pad(load_rgb(input_path)), size)
    gray_image = ImageOps.grayscale(rgb)
    gray = np.array(gray_image)

    binary = make_binary_line(gray, threshold)
    canny = make_canny(gray, canny_low, canny_high)

    # ControlNet scribble models usually expect bright strokes on a dark canvas.
    scribble = 255 - binary

    outputs = {
        "normalized": output_dir / f"{stem}_normalized.png",
        "gray": output_dir / f"{stem}_gray.png",
        "binary": output_dir / f"{stem}_binary.png",
        "canny": output_dir / f"{stem}_canny_control.png",
        "scribble": output_dir / f"{stem}_scribble_control.png",
    }

    rgb.save(outputs["normalized"])
    gray_image.save(outputs["gray"])
    Image.fromarray(binary).save(outputs["binary"])
    Image.fromarray(canny).save(outputs["canny"])
    Image.fromarray(scribble).save(outputs["scribble"])

    return outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize designer shoe sketches and generate ControlNet control maps."
    )
    parser.add_argument("input", type=Path, help="Input sketch image path.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("code/outputs/sketch_preprocess"),
        help="Directory for generated preprocessing outputs.",
    )
    parser.add_argument("--size", type=int, default=512, help="Square output size.")
    parser.add_argument(
        "--threshold",
        type=int,
        default=235,
        help="Binary threshold for line extraction.",
    )
    parser.add_argument("--canny-low", type=int, default=80, help="Canny low threshold.")
    parser.add_argument("--canny-high", type=int, default=180, help="Canny high threshold.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = preprocess_sketch(
        input_path=args.input,
        output_dir=args.output_dir,
        size=args.size,
        threshold=args.threshold,
        canny_low=args.canny_low,
        canny_high=args.canny_high,
    )
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
