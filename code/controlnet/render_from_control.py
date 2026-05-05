from __future__ import annotations

import argparse
from pathlib import Path

import torch
from diffusers import ControlNetModel, StableDiffusionControlNetPipeline
from PIL import Image


DEFAULT_PROMPT = (
    "clean side view footwear concept render, single pair of shoes, white background, "
    "industrial design sketch converted to product rendering, clear sole, upper, heel, toe box"
)

DEFAULT_NEGATIVE_PROMPT = (
    "person, foot, leg, text, watermark, logo, blurry, low quality, deformed shoe, "
    "extra objects, messy background"
)


def load_control_image(path: Path, size: int) -> Image.Image:
    image = Image.open(path).convert("RGB")
    return image.resize((size, size), Image.Resampling.LANCZOS)


def build_pipeline(
    base_model: str,
    controlnet_model: str,
    device: str,
    enable_xformers: bool,
) -> StableDiffusionControlNetPipeline:
    controlnet = ControlNetModel.from_pretrained(
        controlnet_model,
        torch_dtype=torch.float16,
    )
    pipe = StableDiffusionControlNetPipeline.from_pretrained(
        base_model,
        controlnet=controlnet,
        torch_dtype=torch.float16,
        safety_checker=None,
        requires_safety_checker=False,
    )
    pipe.enable_attention_slicing()
    if enable_xformers:
        try:
            pipe.enable_xformers_memory_efficient_attention()
        except Exception as exc:
            print(f"xformers unavailable: {exc}")
    pipe.to(device)
    return pipe


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a designer shoe sketch/control map with Stable Diffusion ControlNet."
    )
    parser.add_argument("control_image", type=Path, help="Control image path.")
    parser.add_argument("--output", type=Path, required=True, help="Output image path.")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--negative-prompt", default=DEFAULT_NEGATIVE_PROMPT)
    parser.add_argument("--base-model", default="runwayml/stable-diffusion-v1-5")
    parser.add_argument("--controlnet-model", default="lllyasviel/control_v11p_sd15_canny")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--steps", type=int, default=12)
    parser.add_argument("--guidance-scale", type=float, default=7.0)
    parser.add_argument("--control-scale", type=float, default=0.85)
    parser.add_argument("--seed", type=int, default=114)
    parser.add_argument("--no-xformers", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    control_image = load_control_image(args.control_image, args.size)
    generator = torch.Generator(device=args.device).manual_seed(args.seed)
    pipe = build_pipeline(
        base_model=args.base_model,
        controlnet_model=args.controlnet_model,
        device=args.device,
        enable_xformers=not args.no_xformers,
    )

    result = pipe(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        image=control_image,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance_scale,
        controlnet_conditioning_scale=args.control_scale,
        generator=generator,
    ).images[0]
    result.save(args.output)
    print(f"output: {args.output}")


if __name__ == "__main__":
    main()
