---
title: "[design] overview_arm: mount the chosen USB camera (waiting for the camera pick)"
labels: design, waiting
part: overview_arm
who: Any strong AI
---
> **Waiting:** do not start until the research task "pick the overview USB camera" is done and the camera is chosen. Then the integrator refreshes this prompt with the real numbers.

# Task: Overview arm

**Suggested model:** Fable or the strongest model you have. **Part file:** `parts/overview/overview_arm.py`. **Spec version:** 3. **Status:** redesign.

You are designing one 3D printed part of ARGUS T18, a low-cost automated microscope slide scanner (METU EE493 capstone). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera. Parts are CadQuery Python, modelled in assembled position. Many people work on different parts at the same time, so each part has a contract: a box it must stay inside and holes it must keep where other parts meet it.

## Goal
Redesign the overview arm for the USB camera picked in the research task: board holes, lens position over the slide park position, cable exit. Keep the two M3x60 holes through the column.

## Inputs (measurements or listing data)
- none given; use the listing values already in the code and say which numbers you assumed

## Contract
- Envelope (x0, x1, y0, y1, z0, z1): [25, 92, -20, 128, 176, 198]. Stay inside it.
- Moves with: nothing (fixed to the base). Prints upside down (top face down).
- Interface holes you must keep exactly (other parts depend on them):
- **column_to_overview**: 2 M3x60 screws go through the column and the overview arm. Axis x, centres (104, 188), (120, 188), starts at x = 25, goes +x at least 6 mm, clearance. Mates with: column. In code: `pat('column_to_overview')`.
- **overview_camera_mount**: overview camera board screws (placeholder until the USB camera is picked). Axis z, centres (64.5, -6.25), (64.5, 6.25), (85.5, -6.25), (85.5, 6.25), starts at z = 186, goes +z at least 4 mm, bore, diameter 2 mm. Mates with: a bought part. In code: `pat('overview_camera_mount')`.
- Parts whose space is next to yours:
  - Column (`column`, envelope [-36, 36, 65, 141, -1, 202])
  - Column top cap (`column_top_cap`, envelope [-31, 31, 64, 137, 194, 212])
  - Focus carriage (`focus_carriage`, envelope [-31, 31, 61, 83, 144, 190])
  - Lens clamp (`lens_clamp`, envelope [-30, 30, -36, 62, 145, 205])
- Bought parts in or next to your space (assembled, stage at home):
  - LM8UU (Z): box [10.5, 25.5, 68.5, 83.5, 159, 183]
  - Overview camera (USB, tbd): box [62.5, 87.5, -12, 12, 177, 186] (placeholder: the Pi has one camera port (HQ), so the overview camera will be a USB module; the arm gets redesigned when we pick it)
  - Overview LED 5 mm: box [72.1, 77.9, 15.1, 20.9, 184, 197] (lights the slide from above for the overview photo)

## Rules
1. Change only `parts/overview/overview_arm.py`. Keep `META` and `build()`.
2. Take numbers from `P[...]` and `pat(...)`. Never type in a number another part depends on.
3. If the goal needs a bigger envelope, a moved interface or a new parameter, do not change shared files: finish what you can and write a **change request** (what, why, the new numbers) at the end of your answer.
4. Print-friendly: no supports in the chosen orientation (overhangs steeper than 45 degrees from vertical need a chamfer), walls at least 1.2 mm, fits a 220 x 220 x 250 mm bed.
5. Code comments: short, lowercase, no punctuation.

## Parameters this part uses now
- `overview` = {'x': 75.0, 'y': 0.0, 'z_lens': 177.0, 'hfov': 66.0, 'vfov': 41.0, 'min_focus': 100.0}

## Current code
`parts/overview/overview_arm.py`
```python
# overview arm: bolts through the column, carries the overview camera above the slide park position
from argus.geo import *
from argus.spec import P, pat

META = dict(name='Overview arm', group='F', layer=6, sub='Overview camera', step=10, color='overview', orient='zmax',
            note='Bolts through the column; carries the overview camera 113 mm above the slide and a 5 mm white LED for '
                 'reflected light.', hw={'M3x60 screw': 2, 'M3 nut': 2, 'M2x6 screw': 4})


def build():
    oc = P['overview']
    arm = fuse(box(25, 31, 98, 126, 180, 196), box(25, 82, 106, 118, 188, 196), box(68, 82, -14, 118, 188, 196),
               box(62, 88, -16, 22, 186, 196))
    return cut(arm, *[cyl(1.7, (24.9, y, z), (31.1, y, z)) for y, z in pat('column_to_overview')],
               cyl(5, (oc['x'], 0, 185.9), (oc['x'], 0, 196.1)), cyl(2.6, (oc['x'], 18, 185.9), (oc['x'], 18, 196.1)),
               *[cyl(1.0, (x, y, 185.9), (x, y, 192)) for x, y in pat('overview_camera_mount')])
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
- If you can run code: `pip install -r requirements.txt`, then `python tools/check.py overview_arm` (seconds) and `python tools/check.py` (whole machine, about a minute). All must pass.
- If you cannot run code: deliver the file anyway; the checks run automatically on the pull request.

## Deliver
1. The full new `parts/overview/overview_arm.py`.
2. Three lines: what changed, which numbers are measured vs assumed, what you are unsure about.
3. A change request, only if rule 3 applied.

Repo: https://github.com/mmucteba/argus (read everything else in CONTEXT.md if you have access).
