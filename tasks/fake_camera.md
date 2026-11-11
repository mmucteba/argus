---
title: "[software] fake_camera: synthetic slide tiles"
labels: software
part: software/fake_camera
who: Any strong AI
---
# Task: fake camera

**Suggested model:** any strong AI. **Folder:** `software/fake_camera/`. No hardware, no downloads.

ARGUS T18 is a low-cost microscope slide scanner (METU EE493). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera; an Arduino Uno runs GRBL 1.1 for the motors; a Raspberry Pi 3B+ runs the scan and streams tiles to a laptop, which stitches them and runs a tumour classifier. The software is built as small modules with fixed interfaces and fakes for the hardware, so everything is tested before the boards exist.

## Goal
A pretend HQ camera looking at a pretend slide, so the scan loop, the stitcher and the AI can be tested without hardware. The same fake slide must give tiles that really overlap where the stage positions say they do.

## Interface
```python
from software.fake_camera import FakeSlide, FakeCamera
slide = FakeSlide(size_mm=(20, 20), um_per_px=None, seed=0)   # um_per_px default from the spec (below)
cam = FakeCamera(slide, noise=2.0, vignette=0.15, blur_px=1.0, pos_error_um=0.0, seed=0)
tile = cam.capture(x_mm, y_mm)    # uint8 array (1520, 2028, 3): the field centred at stage position x, y
truth = slide.region(x0_mm, y0_mm, x1_mm, y1_mm)   # ground-truth image of any region, for tests
```
Numbers from the spec:
- `um_per_px = P['px_native'] * P['binning'] / P['mag']` (1.72 um/px now)
- tile size 2028 x 1520
- field = `P['sensor_w'] / P['mag']` x `P['sensor_h'] / P['mag']`

## Behaviour
- **FakeSlide:** procedural, tissue-like texture: pink background with darker purple blobs, small dark dots like nuclei, a few white holes. Deterministic from the seed. Generate it lazily in blocks or at reduced memory: a 20 x 20 mm slide at 1.72 um/px is about 11,600 x 11,600 px, so keep it under about 500 MB or tile it.
- **FakeCamera:** cut the field, optionally shift it by a random position error (`pos_error_um`, normal), add vignetting (darker corners), Gaussian blur and noise. Image +x and +y follow stage +x and +y; document the convention in interface.md.

## Tests
- `capture` at the same position twice gives the same image with noise=0
- two captures 1 mm apart in x are the same pixels shifted by 1000 / um_per_px px (check with a correlation)
- the shape and dtype are right; vignetting darkens the corners
- `region` matches a capture with all effects off

## Rules
1. Everything goes in `software/fake_camera/`: `__init__.py`, the code, `interface.md` (the interface below in your words), `tests/test_*.py`. Do not edit other folders.
2. Plain Python 3.13 with numpy, scipy and Pillow only (already in requirements.txt); no new libraries, no downloads, no hardware.
3. Read machine numbers from `from argus.spec import P` (spec/params.yaml), never copy them.
4. `python -m pytest software/fake_camera -q` must pass in under 30 s. The same tests run automatically on the pull request.
5. Code comments short, lowercase, no punctuation. Small functions, type hints, no global state.

## Deliver
The files above, as a pull request (template in the repo) or as files your teammate uploads. Three lines at the end: what works, what is assumed, what is missing.
