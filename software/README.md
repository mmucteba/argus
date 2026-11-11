# Software plan (not started)

Same idea as the parts: small modules, a fixed format between them, tests for each, and **fakes** that stand in for the hardware. Everything can be written and tested before the boards arrive. When they arrive, the real driver replaces the fake behind the same interface, and nothing else changes.

## Modules

| Module | Runs on | In | Out | Tested with |
|---|---|---|---|---|
| `grbl_link` | Pi | G-code moves, `?` polls | ok / Idle / Alarm states, positions | `fake_grbl`: answers like GRBL 1.1, with configurable delays and alarms |
| `camera` | Pi | exposure, gain, white balance (locked) | frames + timestamps | `fake_camera`: tiles cut from a Camelyon16 slide with noise, vignetting and blur |
| `scan_planner` | Pi | ROI, field of view, overlap, backlash approach | ordered list of stage positions | pure functions, unit tests |
| `acquisition` | Pi | plan, grbl_link, camera | tile JPEG + JSON sidecar per tile, streamed to the laptop | fake_grbl + fake_camera end to end |
| `stitch` | laptop | tiles + sidecars | pyramidal mosaic, residual report | synthetic tiles with known offsets |
| `ai` | laptop | mosaic | tumour heatmap, region mask | PCam test split, printed Camelyon targets |
| `gui` | laptop | mosaic, heatmap | viewer | manual |

## Shared formats (to fix before coding)

**Tile sidecar:** a JSON file next to each `tile_<row>_<col>.jpg` with:
- `index`, `row`, `col`
- `x_mm`, `y_mm`, `z_mm`
- `t_move_end`, `t_frame_start`
- `exposure_us`, `gain`, `colour_gains`
- `sharpness`, `retries`

**Scan folder:**
- `scan.json`: plan, settings, spec version
- the tiles and their sidecars
- `calib/` with the flat-field, dark frame and pixel size

## Rules

- Each module lives in its own folder with `interface.md`, the code and `tests/`.
- No module imports another module's internals; only its interface.
- `pytest software/` must pass. It joins the automatic checks when the first module lands.
- The end-to-end test runs a full fake scan (fake_grbl + fake_camera), stitches it, and compares the result with the known image.
