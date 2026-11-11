---
title: "[software] scan_planner: tile grid and move order"
labels: software
part: software/scan_planner
who: Any strong AI
---
# Task: scan planner

**Suggested model:** any strong AI (no Fable needed). **Folder:** `software/scan_planner/`. No hardware needed.

ARGUS T18 is a low-cost microscope slide scanner (METU EE493). The stage moves the slide under a fixed camera; the camera sees one small field at a time, so a 15 x 15 mm area is captured as a grid of overlapping tiles that are stitched later. This module plans where the stage goes.

## Goal
Write a pure Python module that turns a scan request into an ordered list of stage moves, with tests. No hardware, no GRBL, no camera: just numbers in and numbers out.

## Interface
```python
from software.scan_planner import plan

moves = plan(roi_center=(x_mm, y_mm), roi_size=(w_mm, h_mm), fov=(fw_mm, fh_mm), overlap=0.25,
             x_travel=(-25.0, 70.0), y_travel=(-15.0, 15.0), backlash_mm=0.5)
# returns a list of dicts in the order the stage should go:
# {'kind': 'pre' or 'tile', 'x': mm, 'y': mm, 'row': int, 'col': int, 'index': int or None}
```
Defaults come from `spec/params.yaml`: read them with `from argus.spec import P`:
- field of view = `P['sensor_w'] / P['mag']` x `P['sensor_h'] / P['mag']` (3.49 x 2.62 mm now)
- overlap `P['overlap']` (0.25), roi `P['roi']` (15 mm), travel `P['x_travel']`, `P['y_travel']`

## Rules
1. Step between tile centres = field x (1 - overlap). Use the fewest rows and columns that cover the whole ROI, and centre the grid on the ROI.
2. Raster order, row by row. Every row is approached from the same side in X: before the first tile of each row, add a `pre` move to x_first - backlash_mm, then step only in +X along the row. This takes up the screw backlash the same way for every tile.
3. Never plan a move outside the travel limits; raise `ValueError` with a clear message if the ROI cannot be reached.
4. Tile `index` counts tiles only, from 0, in capture order; `row` and `col` give the grid position (row 0 at the smallest y, col 0 at the smallest x).
5. Plain Python, no new libraries. Code comments short, lowercase, no punctuation.

## Tests (software/scan_planner/tests/test_plan.py, pytest)
- 15 x 15 mm ROI with the current field gives 6 columns x 8 rows = 48 tiles
- neighbouring tile centres are exactly one step apart; the union of tiles covers the ROI with the requested overlap
- every row starts with a `pre` move at x_first - backlash, and X never decreases inside a row
- an ROI that sticks out of the travel raises ValueError
- 1 x 1 mm ROI gives one tile

## Deliver
`software/__init__.py` (empty), `software/scan_planner/__init__.py`, `software/scan_planner/interface.md` (the interface above, in your words), the tests. `pytest software/` must pass. Open a pull request with the template, or give the files to your teammate.
