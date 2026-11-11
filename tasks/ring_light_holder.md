---
title: "[design] ring_light_holder: fit the real zoom lens (waiting for the lens)"
labels: design, fable, waiting
part: ring_light_holder
who: Fable (hard geometry)
---
> **Waiting:** do not start until the lens is measured (front barrel diameter and working distance) and the lens clamp task is done. Then the integrator refreshes this prompt with the real numbers.

# Task: Ring light holder

**Suggested model:** Fable or the strongest model you have. **Part file:** `parts/optics/ring_light_holder.py`. **Spec version:** 3. **Status:** needs-measurement.

You are designing one 3D printed part of ARGUS T18, a low-cost automated microscope slide scanner (METU EE493 capstone). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera. Parts are CadQuery Python, modelled in assembled position. Many people work on different parts at the same time, so each part has a contract: a box it must stay inside and holes it must keep where other parts meet it.

## Goal
Follows the lens measurements (front barrel diameter, working distance).

## Inputs (measurements or listing data)
- none given; use the listing values already in the code and say which numbers you assumed

## Contract
- Envelope (x0, x1, y0, y1, z0, z1): [-46, 46, -46, 46, 100, 146]. Stay inside it.
- Moves with: the focus carriage. Prints as assembled (bottom face down).
- Interface holes you must keep exactly (other parts depend on them):
- none listed
- Parts whose space is next to yours:
  - Lens clamp (`lens_clamp`, envelope [-30, 30, -36, 62, 145, 205])
- Bought parts in or next to your space (assembled, stage at home):
  - Zoom lens 0.12-1.8x: box [-19.5, 19.5, -19.5, 19.5, 123.17, 235.17] (Waveshare 100X industrial microscope lens, C-mount, 39 x 112 mm. Zoom set to 1.8x; working distance about 55 mm there (listing says 55-285 mm over the zoom range), measure on arrival. NA is not published.)
  - Zoom lens front glass: box [-15, 15, -15, 15, 122.97, 123.17]
  - LED ring 24x WS2812: box [-43.25, 43.25, -43.25, 43.25, 106, 109.5] (86.5 / 71.5 mm, 24 LEDs, data from Pi GPIO10 through the 74HCT125, 5 V from the buck)

## Rules
1. Change only `parts/optics/ring_light_holder.py`. Keep `META` and `build()`.
2. Take numbers from `P[...]` and `pat(...)`. Never type in a number another part depends on.
3. If the goal needs a bigger envelope, a moved interface or a new parameter, do not change shared files: finish what you can and write a **change request** (what, why, the new numbers) at the end of your answer.
4. Print-friendly: no supports in the chosen orientation (overhangs steeper than 45 degrees from vertical need a chamfer), walls at least 1.2 mm, fits a 220 x 220 x 250 mm bed.
5. Code comments: short, lowercase, no punctuation.

## Parameters this part uses now
- `lens_r` = 19.5
- `ring_above_slide` = 38
- `z_cmount` = 231.17
- `z_focal` = 68
- `z_obj_tip` = 123.17

## Current code
`parts/optics/ring_light_holder.py`
```python
# ring light holder: push-fit sleeve on the lens front, cone carries the led ring
from argus.geo import *
from argus.spec import P
from parts.optics.layout import LF, LR, RING_Z, RING_TOP

META = dict(name='Ring light holder', group='Z', layer=5, sub='Optics', step=9, color='zstage', orient='zmin',
            note=f'Push-fit on the lens front; a 52 degree cone carries the 86.5 mm LED ring {RING_Z - P["z_focal"]:.0f} mm '
                 f'above the slide, so the light hits printed targets at about '
                 f'{math.degrees(math.atan(39.5 / (RING_Z - P["z_focal"]))):.0f} degrees and glare stays out of the lens. '
                 'Prints as assembled, no supports.')


def build():
    rb = LR + 0.2
    pt = RING_TOP + 2.5
    plate = tube(44.5, 34.0, (0, 0, RING_TOP), (0, 0, pt))
    shell = cut(cone(36.5, 22.3, (0, 0, pt - 0.01), (0, 0, pt + 18)), cone(34.5, 20.3, (0, 0, pt - 0.02), (0, 0, pt + 18.01)))
    zj = 126.0
    sleeve = cut(cyl(23.5, (0, 0, zj), (0, 0, LF + 20)), cone(23.4, rb, (0, 0, zj - 0.01), (0, 0, zj + 3.7)),
                 cyl(rb, (0, 0, zj + 3.69), (0, 0, LF + 20.1)))
    return fuse(plate, shell, sleeve).clean()
```

`parts/optics/layout.py` (shared by the module, read only)
```python
# shared numbers for the optics module, all from the spec
from argus.spec import P

LF = P['z_obj_tip']                              # lens front
ZC = P['z_cmount']                               # c mount flange
LR = P['lens_r']                                 # lens barrel radius
RING_Z = P['z_focal'] + P['ring_above_slide']    # led ring bottom
RING_TOP = RING_Z + 3.5
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
- If you can run code: `pip install -r requirements.txt`, then `python tools/check.py ring_light_holder` (seconds) and `python tools/check.py` (whole machine, about a minute). All must pass.
- If you cannot run code: deliver the file anyway; the checks run automatically on the pull request.

## Deliver
1. The full new `parts/optics/ring_light_holder.py`.
2. Three lines: what changed, which numbers are measured vs assumed, what you are unsure about.
3. A change request, only if rule 3 applied.

Repo: https://github.com/mmucteba/argus (read everything else in CONTEXT.md if you have access).
