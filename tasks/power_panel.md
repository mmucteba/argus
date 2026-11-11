---
title: "[design] power_panel: one place for jack, switch, fuse, buck and level shifter"
labels: design, fable
part: power_panel
who: Fable (hard geometry)
---
# Task: Power panel

**Suggested model:** Fable or the strongest model you have. **Part file:** `parts/electronics/power_panel.py`. **Spec version:** 3. **Status:** new.

You are designing one 3D printed part of ARGUS T18, a low-cost automated microscope slide scanner (METU EE493 capstone). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera. Parts are CadQuery Python, modelled in assembled position. Many people work on different parts at the same time, so each part has a contract: a box it must stay inside and holes it must keep where other parts meet it.

## Goal
Design a new printed part that holds the whole power side of the scanner at the back left of the base, so the wiring page can be built neatly: DC jack, rocker switch, inline fuse, LM2596 buck, the 74HCT125 on a small perfboard, and three Wago connectors. Jack and switch reachable from the back edge of the base (y = 153). Screwed to the plywood with wood screws (return the base holes from build()).

## Inputs (measurements or listing data)
- DC jack: Robotistan "DC güç fişi 2.1 mm dişi, vidalı klemens", a female barrel jack with a screw terminal block, roughly 30 x 15 x 15 mm (assumed). Hold it in a clip or pocket so the plug goes in from the back edge.
- KCD1 rocker switch: needs a 19 x 13 mm rectangular cut-out in a wall 1.5 to 2 mm thick (standard KCD1 snap-in).
- Inline fuse holder 5 x 20 mm: a cable part about 50 x 12 mm; a zip-tie anchor is enough.
- LM2596 buck module: about 43 x 21 x 14 mm, 2 mounting holes about 3 mm (positions assumed: diagonal corners); keep its trim screw reachable.
- 74HCT125 on a perfboard about 30 x 20 mm (assumed), 2 holes or a slot to slide into.
- 3 x Wago 221-413: about 20 x 19 x 13 mm each (assumed); a row of pockets or zip-tie anchors.
- Wire routes: 12 V goes to the CNC shield on the Uno tray at the front left (x -132..12, y -114..-58); 5 V goes to the LED card (centre), the LED ring (up the column) and the endstops.
- The X motor sits just in front of your space (x -131..-91, y 49..91, z 3..45); keep at least 3 mm away.
- Keep the panel under 45 mm tall and the switch easy to hit as an emergency stop.

## Contract
- Envelope (x0, x1, y0, y1, z0, z1): [-135, -40, 96, 152, 0, 45]. Stay inside it.
- Moves with: nothing (fixed to the base). Prints as assembled (bottom face down).
- Interface holes you must keep exactly (other parts depend on them):
- none listed
- Parts whose space is next to yours:
  - X end block L (`x_end_block_l`, envelope [-92, -70, -56, 94, -1, 48])
- Bought parts in or next to your space (assembled, stage at home):
  - Base plate: box [-137, 163, -117, 153, -18, 0] (18 mm plywood (or 6 mm aluminium, then tap M4 instead of wood screws). The flat, heavy reference that every other part bolts to. Printing it is possible but it would be less flat and lighter, so buy it.)

## Rules
1. Change only `parts/electronics/power_panel.py`. Keep `META` and `build()`.
2. Take numbers from `P[...]` and `pat(...)`. Never type in a number another part depends on.
3. If the goal needs a bigger envelope, a moved interface or a new parameter, do not change shared files: finish what you can and write a **change request** (what, why, the new numbers) at the end of your answer.
4. Print-friendly: no supports in the chosen orientation (overhangs steeper than 45 degrees from vertical need a chamfer), walls at least 1.2 mm, fits a 220 x 220 x 250 mm bed.
5. Code comments: short, lowercase, no punctuation.

## Parameters this part uses now
- none

## Current code
`parts/electronics/power_panel.py`
```python
# power panel: dc jack, switch, fuse, buck and the level shifter in one place at the back left
# placeholder plate until the design task is done
from argus.geo import *

META = dict(name='Power panel', group='F', layer=0, sub='Electronics', step=11, color='frame', orient='zmin',
            note='Placeholder. Will hold the DC jack, KCD1 switch, inline fuse, LM2596 buck, 74HCT125 board and the Wago '
                 'connectors, with the jack and switch facing the back edge.',
            hw={'Wood screw 4x16': 4})


def build():
    plate = box(-130, -45, 100, 150, 0, 3)
    base = [(-125, 105), (-125, 145), (-50, 105), (-50, 145)]
    return cut(plate, *[wood_hole(x, y, 3, 0) for x, y in base]), [(x, y, 'Power panel') for x, y in base]
```

## Geometry helpers (argus.geo)

Units are mm, z is up, the optical axis is x = 0, y = 0 and the top of the plywood base is z = 0. Points are `(x, y, z)` tuples. Every function returns a CadQuery solid. Parts are modelled in their **assembled position**, not on the print bed.

| Function | What it makes |
|---|---|
| `box(x0, x1, y0, y1, z0, z1)` | Block between the two corners |
| `cyl(r, p0, p1)` | Cylinder of radius r from point p0 to point p1 (any direction) |
| `tube(ro, ri, p0, p1)` | Hollow cylinder |
| `cone(r0, r1, p0, p1)` | Cone or frustum, radius r0 at p0 and r1 at p1 |
| `fuse(a, b, ...)` | Union |
| `cut(a, b, ...)` | a minus everything else |
| `hexprism(af, h, p, axis='z')` | Hex nut pocket, af = across flats, starting at p along +axis |
| `prism_yz(pts_yz, x0, x1)` | Polygon in the y-z plane extruded along x |
| `ins(p, axis='-z', depth=6)` | M3 heat-set insert hole (diameter `insert_d` from the spec); p is the opening on the surface, axis the drilling direction |
| `bolt_v(x, y, z_top, z_bot, cb_depth=0)` | Vertical M3 clearance hole, optional counterbore from the top |
| `wood_hole(x, y, z_top, z_bot, cb_to=None)` | Hole for a 4 mm wood screw into the base, optional counterbore down to cb_to |
| `saddle(center, axis, length, half_w, open_dir, plate_face=...)` | Half-pipe pocket for an LM8UU; returns (block to fuse, bore to cut) |
| `ziptie_slots(center, axis, open_dir, z0, z1)` | Slots for two zip ties around an LM8UU |
| `spur_gear(m, z, t)` | Involute spur gear at the origin, module m, z teeth, thickness t |

Bought part shapes and their cut-outs are in `argus.catalog`: `nema17`, `nema_holes`, `lm8uu`, `t8_nut`, `t8_mount_holes`, `endstop_board`.

Numbers come from `argus.spec`:
- `P['name']` for a parameter in `spec/params.yaml`
- `pat('interface_name')` for the hole centres of an interface in `spec/interfaces.yaml`, already computed from params

## A part file looks like this

```python
# lens clamp: split collar for the zoom lens barrel, screwed to the focus carriage
from argus.geo import *
from argus.spec import P, pat

META = dict(name='Lens clamp', group='Z', layer=5, sub='Optics', step=9, color='zstage', orient='zmin',
            note='What it does and how to print it, in one or two sentences.',
            hw={'M3x16 screw': 4, 'M3 nut': 2})


def build():
    body = tube(24.5, 19.7, (0, 0, 148), (0, 0, 192))
    holes = [cyl(1.7, (x, 18, z), (x, 62.1, z)) for x, z in pat('focus_to_lens_clamp')]
    return cut(body, *holes)          # or (shape, base_holes) for parts screwed to the plywood
```

`META` fields:
- `group`: F fixed, X moves with the X carriage, Y moves with the Y carriage, Z moves with focus
- `orient`: print orientation: zmin as assembled, zmax upside down, xmin/xmax/ymin/ymax on that side
- `hw`: screws and inserts the part uses
- `layer`, `sub`, `step`, `color`: for the viewer and the build guide; keep them as they are


## Check your work
- If you can run code: `pip install -r requirements.txt`, then `python tools/check.py power_panel` (seconds) and `python tools/check.py` (whole machine, about a minute). All must pass.
- If you cannot run code: deliver the file anyway; the checks run automatically on the pull request.

## Deliver
1. The full new `parts/electronics/power_panel.py`.
2. Three lines: what changed, which numbers are measured vs assumed, what you are unsure about.
3. A change request, only if rule 3 applied.

Repo: https://github.com/mmucteba/argus (read everything else in CONTEXT.md if you have access).
