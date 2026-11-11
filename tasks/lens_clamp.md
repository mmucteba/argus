---
title: "[design] lens_clamp: fit the real zoom lens (waiting for the lens)"
labels: design, fable, waiting
part: lens_clamp
who: Fable (hard geometry)
---
> **Waiting:** do not start until the zoom lens arrives and someone measures the barrel diameter, where the zoom ring sits and the lens front height at best focus. Then the integrator refreshes this prompt with the real numbers.

# Task: Lens clamp

**Suggested model:** Fable or the strongest model you have. **Part file:** `parts/optics/lens_clamp.py`. **Spec version:** 3. **Status:** needs-measurement.

You are designing one 3D printed part of ARGUS T18, a low-cost automated microscope slide scanner (METU EE493 capstone). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera. Parts are CadQuery Python, modelled in assembled position. Many people work on different parts at the same time, so each part has a contract: a box it must stay inside and holes it must keep where other parts meet it.

## Goal
Lens arrives: measure barrel diameter, where the zoom ring sits and the height at best focus.

## Inputs (measurements or listing data)
- none given; use the listing values already in the code and say which numbers you assumed

## Contract
- Envelope (x0, x1, y0, y1, z0, z1): [-30, 30, -36, 62, 145, 205]. Stay inside it.
- Moves with: the focus carriage. Prints as assembled (bottom face down).
- Interface holes you must keep exactly (other parts depend on them):
- **focus_to_lens_clamp**: 2 M3 screws hold the lens clamp on the front of the focus carriage. Axis y, centres (0, 160), (0, 182), starts at y = 62, goes -y at least 8 mm, clearance. Mates with: focus_carriage. In code: `pat('focus_to_lens_clamp')`.
- Parts whose space is next to yours:
  - Column top cap (`column_top_cap`, envelope [-31, 31, 64, 137, 194, 212])
  - Focus carriage (`focus_carriage`, envelope [-31, 31, 61, 83, 144, 190])
  - Ring light holder (`ring_light_holder`, envelope [-46, 46, -46, 46, 100, 146])
  - Overview arm (`overview_arm`, envelope [25, 92, -20, 128, 176, 198])
- Bought parts in or next to your space (assembled, stage at home):
  - Zoom lens 0.12-1.8x: box [-19.5, 19.5, -19.5, 19.5, 123.17, 235.17] (Waveshare 100X industrial microscope lens, C-mount, 39 x 112 mm. Zoom set to 1.8x; working distance about 55 mm there (listing says 55-285 mm over the zoom range), measure on arrival. NA is not published.)

## Rules
1. Change only `parts/optics/lens_clamp.py`. Keep `META` and `build()`.
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
`parts/optics/lens_clamp.py`
```python
# lens clamp: split collar for the zoom lens barrel, screwed to the focus carriage
from argus.geo import *
from argus.spec import pat
from parts.optics.layout import LR

META = dict(name='Lens clamp', group='Z', layer=5, sub='Optics', step=9, color='zstage', orient='zmin',
            note='Split collar for the 39 mm lens barrel, two M3 bolts close the slit. Screw it to the focus carriage first '
                 'through the bore, then slide the lens in. The lens can slide about 10 mm either way to set the height.',
            hw={'M3x16 screw': 4, 'M3 nut': 2})


def build():
    c0, c1 = 148.0, 192.0
    rb = LR + 0.2
    tc = fuse(tube(24.5, rb, (0, 0, c0), (0, 0, c1)), box(-10, 10, 22, 62, c0, c1), box(-7, 7, -31, -22.5, c0, c1))
    return cut(tc, box(-0.75, 0.75, -31.1, -18, c0 - 0.1, c1 + 0.1),
               *[cyl(1.7, (-7.1, -26.75, z), (7.1, -26.75, z)) for z in (156, 184)],
               *[hexprism(5.7, 2.6, (-7.01, -26.75, z), 'x') for z in (156, 184)],
               *[cyl(1.7, (x, 18, z), (x, 62.1, z)).fuse(cyl(3.2, (x, 18, z), (x, 52, z))) for x, z in pat('focus_to_lens_clamp')])
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
- If you can run code: `pip install -r requirements.txt`, then `python tools/check.py lens_clamp` (seconds) and `python tools/check.py` (whole machine, about a minute). All must pass.
- If you cannot run code: deliver the file anyway; the checks run automatically on the pull request.

## Deliver
1. The full new `parts/optics/lens_clamp.py`.
2. Three lines: what changed, which numbers are measured vs assumed, what you are unsure about.
3. A change request, only if rule 3 applied.

Repo: https://github.com/mmucteba/argus (read everything else in CONTEXT.md if you have access).
