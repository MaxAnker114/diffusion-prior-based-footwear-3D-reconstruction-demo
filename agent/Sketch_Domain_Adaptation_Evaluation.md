# Sketch-Domain Adaptation Evaluation

Date: 2026-05-05

## Goal

Validate the first task-aligned path from a public shoe line-art sketch to:

1. normalized sketch preprocessing,
2. Canny/Scribble control maps,
3. ControlNet rendered shoe image,
4. SF3D GLB export comparison.

This is the first Phase 3A validation. It is not yet a full designer three-view workflow.

## Test Asset

Input sketch:

- File: `code/test_assets/sketches/openclipart_shoes_lineart.png`
- Source page: https://openclipart.org/detail/215041/shoes-lineart
- Download URL: https://openclipart.org/image/2000px/215041
- License: Public domain / CC0, according to Openclipart's public-domain publishing model.

Limitations:

- The image is a public shoe line-art illustration rather than a professional designer three-view sketch.
- It contains a pair of shoes instead of one isolated side-view shoe.
- It is still useful as an early sketch-domain preprocessing and ControlNet smoke test.

## Preprocessing

Script:

- `code/preprocess/sketch_preprocess.py`

Command:

```bash
python code/preprocess/sketch_preprocess.py \
  code/test_assets/sketches/openclipart_shoes_lineart.png \
  --output-dir code/outputs/sketch_preprocess/openclipart_shoes_lineart \
  --size 512
```

Generated outputs:

- normalized sketch
- grayscale sketch
- binary sketch
- Canny control map
- Scribble-style control map

Result:

- Preprocessing completed successfully in `trellis310`.
- Canny and Scribble control maps were generated at 512x512.

## ControlNet Readiness

Environment:

- Conda environment: `trellis310`
- `torch 2.4.0+cu118`
- `diffusers 0.31.0`
- `transformers 4.46.3`
- CUDA available: yes

Access checks:

- `lllyasviel/control_v11p_sd15_canny` config access: passed.
- `runwayml/stable-diffusion-v1-5` config access: passed.

## ControlNet Render Test

Script:

- `code/controlnet/render_from_control.py`

Command:

```bash
python code/controlnet/render_from_control.py \
  code/outputs/sketch_preprocess/openclipart_shoes_lineart/openclipart_shoes_lineart_canny_control.png \
  --output code/outputs/controlnet_render/openclipart_shoes_lineart/canny_render_seed114.png \
  --steps 12 \
  --size 512 \
  --seed 114
```

Result:

- ControlNet pipeline downloaded and loaded successfully.
- 12-step inference completed successfully.
- Output image: `code/outputs/controlnet_render/openclipart_shoes_lineart/canny_render_seed114.png`
- Runtime including first model download: about `194.12` seconds.
- The render preserved the overall shoe pair silhouette, shoe openings, laces, sole, and dotted upper texture.

## SF3D Comparison

Two inputs were tested:

1. Raw normalized sketch directly into SF3D.
2. ControlNet-rendered image into SF3D.

### Raw Sketch -> SF3D

Result:

- GLB export succeeded.
- SF3D reported peak GPU memory: `6171.86572265625 MB`.
- Output GLB: `code/outputs/sf3d_from_sketch_raw/0/mesh.glb`
- Mesh validation:
  - Loaded as `Scene`
  - Geometry count: `1`
  - Vertices: `12245`
  - Faces: `20760`
  - Bounds: `[[-0.48978233337402344, -0.4154082238674164, -0.048157453536987305], [0.47740796208381653, 0.41569316387176514, 0.04605585336685181]]`

Observation:

- The Z thickness range is very small, suggesting raw line-art input tends to produce a flatter reconstruction.

### ControlNet Render -> SF3D

Result:

- GLB export succeeded.
- SF3D reported peak GPU memory: `6172.0283203125 MB`.
- Output GLB: `code/outputs/sf3d_from_controlnet_render/0/mesh.glb`
- Mesh validation:
  - Loaded as `Scene`
  - Geometry count: `1`
  - Vertices: `16476`
  - Faces: `26460`
  - Bounds: `[[-0.4907611608505249, -0.35692620277404785, -0.24842870235443115], [0.48021361231803894, 0.42490828037261963, 0.2086470127105713]]`

Observation:

- The ControlNet-rendered input produced a fuller geometry range than the raw sketch input.
- This supports keeping ControlNet adaptation in the pipeline before SF3D.

## Phase 3A Status

Passed as an early technical validation:

- Public sketch/line-art input collected.
- Sketch preprocessing pipeline implemented.
- Canny and Scribble control maps generated.
- ControlNet Canny render succeeded.
- Raw sketch vs ControlNet-rendered SF3D comparison succeeded.

Remaining work:

- Replace or supplement the Openclipart asset with a true single-view designer shoe sketch.
- Collect or create a three-view sketch test set.
- Run a human visual review of the generated render and both GLB outputs.
- Tune prompts/control strength for shoe-design preservation.
- Decide whether Canny or Scribble should be the default first-mode for designer sketches.

## Phase 3B - Patent Sketch Multi-View Validation

Date: 2026-05-05

Goal:

- Move from generic public line art toward a more task-aligned shoe drawing source.
- Validate a single-view patent sketch and prepare multi-view patent drawings for future three-view experiments.

Source:

- Google Patents page: https://patents.google.com/patent/USD247201S/en
- Patent: `USD247201S`, "Sport shoe"
- Publication date: 1978-02-14
- Legal status on Google Patents: expired-lifetime

Saved assets:

- `code/test_assets/patent_sketches/usd247201s_sport_shoe/usd247201s_sheet.png`
- `code/test_assets/patent_sketches/usd247201s_sport_shoe/usd247201s_page_1.png`
- `code/test_assets/patent_sketches/usd247201s_sport_shoe/views/right_side_fig4_clean.png`
- `code/test_assets/patent_sketches/usd247201s_sport_shoe/views/top_plan_fig1.png`
- `code/test_assets/patent_sketches/usd247201s_sport_shoe/views/bottom_plan_fig2.png`

Utilities added:

- `code/preprocess/crop_image.py` for reproducible manual image crops and rotations.

Preprocessing:

- `right_side_fig4_clean.png`, `top_plan_fig1.png`, and `bottom_plan_fig2.png` were normalized to 512x512.
- Canny and Scribble control maps were generated for each.

ControlNet render test:

```bash
python code/controlnet/render_from_control.py \
  code/outputs/sketch_preprocess/usd247201s_sport_shoe/right_side_fig4_clean/right_side_fig4_clean_canny_control.png \
  --output code/outputs/controlnet_render/usd247201s_sport_shoe/right_side_canny_render_seed115.png \
  --prompt "clean side view sneaker product concept render, white background, low top sport shoe, visible sole, laces, heel counter, toe box, design sketch converted to product rendering" \
  --steps 14 \
  --size 512 \
  --seed 115 \
  --control-scale 0.9
```

Result:

- ControlNet render succeeded.
- Runtime after model cache warm-up: about `17.68` seconds.
- The render preserved the side silhouette, laces, side logo area, heel counter, and sole.
- The patent sketch crop is imperfect: the original page layout caused some upper/collar detail to be cropped.

SF3D comparison:

### Raw Patent Side Sketch -> SF3D

- GLB export succeeded.
- SF3D reported peak GPU memory: `6171.6015625 MB`.
- Output GLB: `code/outputs/sf3d_patent_raw_side/0/mesh.glb`
- Mesh validation:
  - Loaded as `Scene`
  - Geometry count: `1`
  - Vertices: `6843`
  - Faces: `11536`
  - Bounds: `[[-0.4755481481552124, -0.15905815362930298, -0.08591032028198242], [0.48676279187202454, 0.160394549369812, 0.06010115146636963]]`

### ControlNet Patent Render -> SF3D

- GLB export succeeded.
- SF3D reported peak GPU memory: `6171.67578125 MB`.
- Output GLB: `code/outputs/sf3d_patent_controlnet_side/0/mesh.glb`
- Mesh validation:
  - Loaded as `Scene`
  - Geometry count: `1`
  - Vertices: `8376`
  - Faces: `14124`
  - Bounds: `[[-0.4785670042037964, -0.18337196111679077, -0.11239010095596313], [0.4887984097003937, 0.18371117115020752, 0.09511154890060425]]`

Observation:

- ControlNet-rendered patent input again produced a somewhat fuller mesh than raw line input.
- The improvement is present but modest. The bigger issue is input quality: patent page crops need better cleanup or a cleaner designer sketch source.

Phase 3B status:

- Passed as a technical single-view patent-sketch validation.
- Multi-view source collection and preprocessing started.
- Not yet passed as a full three-view reconstruction workflow.

Recommended next action:

- Review the ControlNet render and both GLB outputs.
- Decide whether to continue with patent drawings or switch to manually prepared/curated designer sketches for Phase 3C.
