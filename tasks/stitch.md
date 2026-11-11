---
title: "[software] stitch: register and blend tiles"
labels: software
part: software/stitch
who: Any strong AI
---
# Task: stitcher

**Suggested model:** a strong AI (keep Fable for 3D parts). **Folder:** `software/stitch/`. No hardware.

ARGUS T18 is a low-cost microscope slide scanner (METU EE493). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera; an Arduino Uno runs GRBL 1.1 for the motors; a Raspberry Pi 3B+ runs the scan and streams tiles to a laptop, which stitches them and runs a tumour classifier. The software is built as small modules with fixed interfaces and fakes for the hardware, so everything is tested before the boards exist.

## Goal
Turn a grid of overlapping tiles plus rough stage positions into one seamless mosaic, and report how good the registration was. This runs on the laptop.

## Interface
```python
from software.stitch import register, solve, blend
pairs = register(tiles, nominal_px, overlap_px)   # tiles: dict (row, col) -> HxWx3 uint8; nominal_px: dict (row, col) -> (x, y) top-left in px
pos, report = solve(pairs, nominal_px, sigma_px=20)   # refined top-left positions + residuals
mosaic = blend(tiles, pos)                          # HxWx3 uint8, linear feathering in the overlaps
```
## Method
1. **Pairwise registration:** for each east and south neighbour, phase correlation on the green channel of the overlap strips with a Hann window. Check the top 3 peaks with normalised cross-correlation and keep the best.
2. **Accept or reject:** accept a pair if NCC > 0.5 and the shift is within 4 x sigma_px of the nominal one. Otherwise use the nominal shift with a low weight.
3. **Global solve:** weighted least squares for all tile positions together, with tile (0, 0) fixed. Drop the worst outliers and solve again.
4. **Blend:** linear feathering in the overlaps, plus a per-tile gain so the brightness matches.
5. **Report:** per-pair shift, NCC, residual; overall RMS residual and run time.

## Tests (build tiles inside the tests from a random smooth texture, or use software/fake_camera if merged)
- **48 tiles (6 x 8, 25 % overlap, 2028 x 1520 px, scaled down 4x for speed) with random position errors of ±20 px:** recovered positions within 1 px of the truth
- **The same with 3 blank tiles:** they fall back to nominal positions without wrecking the others
- **Mosaic vs the source image:** mean absolute difference below 3 grey levels away from the borders

## Rules
1. Everything goes in `software/stitch/`: `__init__.py`, the code, `interface.md` (the interface below in your words), `tests/test_*.py`. Do not edit other folders.
2. Plain Python 3.13 with numpy, scipy and Pillow only (already in requirements.txt); no new libraries, no downloads, no hardware.
3. Read machine numbers from `from argus.spec import P` (spec/params.yaml), never copy them.
4. `python -m pytest software/stitch -q` must pass in under 60 s. The same tests run automatically on the pull request.
5. Code comments short, lowercase, no punctuation. Small functions, type hints, no global state.

## Deliver
The files above, as a pull request (template in the repo) or as files your teammate uploads. Three lines at the end: what works, what is assumed, what is missing.
