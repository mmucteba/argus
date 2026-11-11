---
title: "[software] image_tools: focus score, flat-field, exposure check"
labels: software
part: software/image_tools
who: Any strong AI
---
# Task: image tools

**Suggested model:** any AI. **Folder:** `software/image_tools/`. No hardware.

ARGUS T18 is a low-cost microscope slide scanner (METU EE493). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera; an Arduino Uno runs GRBL 1.1 for the motors; a Raspberry Pi 3B+ runs the scan and streams tiles to a laptop, which stitches them and runs a tumour classifier. The software is built as small modules with fixed interfaces and fakes for the hardware, so everything is tested before the boards exist.

## Goal
The small image functions the scan loop needs on every tile.

## Interface
```python
from software.image_tools import sharpness, flat_field, exposure_check, make_flat
s = sharpness(img)                    # variance of the Laplacian of the green channel, float
corr = flat_field(img, flat, dark)    # (I - D) / (F - D) * mean(F - D), clipped to uint8
flat = make_flat(frames)              # mean of N frames (float32) for F or D
ok, info = exposure_check(img)        # info = dict(mean=..., clipped_high=fraction, clipped_low=fraction); ok when mean in 60..200 and clipped < 0.5 %
```
Pure numpy and scipy; work on uint8 RGB arrays of size 1520 x 2028 in under 50 ms each on a laptop.

## Tests
- sharpness drops monotonically as a test image is blurred more (sigma 0, 1, 2, 4)
- flat_field of a vignetted image (built in the test) is flat within 2 %
- exposure_check flags a dark, a bright and a clipped image and passes a normal one
- the timing test runs on a full-size random image

## Rules
1. Everything goes in `software/image_tools/`: `__init__.py`, the code, `interface.md` (the interface below in your words), `tests/test_*.py`. Do not edit other folders.
2. Plain Python 3.13 with numpy, scipy and Pillow only (already in requirements.txt); no new libraries, no downloads, no hardware.
3. Read machine numbers from `from argus.spec import P` (spec/params.yaml), never copy them.
4. `python -m pytest software/image_tools -q` must pass in under 30 s. The same tests run automatically on the pull request.
5. Code comments short, lowercase, no punctuation. Small functions, type hints, no global state.

## Deliver
The files above, as a pull request (template in the repo) or as files your teammate uploads. Three lines at the end: what works, what is assumed, what is missing.
