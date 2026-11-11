---
title: "[design] x_endstop_pedestal: fit the real optical endstop"
labels: design
part: x_endstop_pedestal
who: Any strong AI
---
# Task: X endstop pedestal

**Suggested model:** Fable or the strongest model you have. **Part file:** `parts/x_axis/x_endstop_pedestal.py`. **Spec version:** 3. **Status:** needs-measurement.

You are designing one 3D printed part of ARGUS T18, a low-cost automated microscope slide scanner (METU EE493 capstone). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera. Parts are CadQuery Python, modelled in assembled position. Many people work on different parts at the same time, so each part has a contract: a box it must stay inside and holes it must keep where other parts meet it.

## Goal
Make the X endstop pedestal fit the optical endstop board we bought even though its hole spacing is not confirmed: give the board slotted holes (about 17 to 21 mm spacing) or another way to fix it, keep the fork straddling the vane on the X carriage, and keep the board easy to take off.

## Inputs (measurements or listing data)
- Robolink "Optik limit switch - endstop" (red board, TCST2103 type fork): about 32 x 10 x 21 mm overall (listing); hole spacing 19 mm assumed; 3-pin cable on one end (VCC, GND, OUT).
- The vane on the X carriage is 1.5 mm thick at y = x_endstop[1] (-19.5), from z 15.5 to 28.5, and passes through the fork at the X- end of travel.
- The current model puts the board on top of the pedestal at z 10 with the fork gap at z 14.4 to 22.4: keep the fork centred on the vane.
- Keep the two M3 heat-set insert positions in interface x_endstop_sensor open (a slot through them is fine).

## Contract
- Envelope (x0, x1, y0, y1, z0, z1): [-75, -51, -48, 8, 0, 12]. Stay inside it.
- Moves with: nothing (fixed to the base). Prints as assembled (bottom face down).
- Interface holes you must keep exactly (other parts depend on them):
- **x_endstop_sensor**: optical endstop board screws onto the X endstop pedestal (19 mm spacing assumed, check the real board). Axis z, centres (-63, -29), (-63, -10), starts at z = 10, goes -z at least 5 mm, insert. Mates with: a bought part. In code: `pat('x_endstop_sensor')`.
- Parts whose space is next to yours:
  - X carriage (`x_carriage`, envelope [-51, 51, -57, 84, 11, 35])
  - X end block L (`x_end_block_l`, envelope [-92, -70, -56, 94, -1, 48])
- Bought parts in or next to your space (assembled, stage at home):
  - Base plate: box [-137, 163, -117, 153, -18, 0] (18 mm plywood (or 6 mm aluminium, then tap M4 instead of wood screws). The flat, heavy reference that every other part bolts to. Printing it is possible but it would be less flat and lighter, so buy it.)
  - X endstop sensor: box [-68.25, -57.75, -36, -3, 10, 22.4] (optical fork (TCST2103 type); triggers at the X- end of travel for homing)

## Rules
1. Change only `parts/x_axis/x_endstop_pedestal.py`. Keep `META` and `build()`.
2. Take numbers from `P[...]` and `pat(...)`. Never type in a number another part depends on.
3. If the goal needs a bigger envelope, a moved interface or a new parameter, do not change shared files: finish what you can and write a **change request** (what, why, the new numbers) at the end of your answer.
4. Print-friendly: no supports in the chosen orientation (overhangs steeper than 45 degrees from vertical need a chamfer), walls at least 1.2 mm, fits a 220 x 220 x 250 mm bed.
5. Code comments: short, lowercase, no punctuation.

## Parameters this part uses now
- `x_endstop` = [-63, -19.5]
- `xblk_l` = -77
- `xblk_r` = 122

## Current code
`parts/x_axis/x_endstop_pedestal.py`
```python
# x endstop pedestal: optical fork board lies on top, vane on the x carriage passes through the fork
from argus.geo import *
from argus.spec import pat
from parts.x_axis.layout import EX, EY

META = dict(name='X endstop pedestal', group='F', layer=2, sub='X drive', step=4, color='frame', orient='zmin',
            note='Sensor board lies on top, long side along Y. Hole spacing 19 mm assumed; check your board and slot the holes '
                 'if needed.', hw={'Wood screw 4x16': 2, 'M3 heat-set insert': 2, 'M3x8 screw': 2})


def build():
    ped = box(EX - 8, EX + 8, EY - 26, EY + 26, 0, 10)
    base = [(EX, EY - 22), (EX, EY + 22)]
    ped = cut(ped, *[wood_hole(x, y, 10, 0) for x, y in base],
              *[ins((x, y, 10), '-z') for x, y in pat('x_endstop_sensor')])
    return ped, [(x, y, 'X endstop') for x, y in base]
```

`parts/x_axis/layout.py` (shared by the module, read only)
```python
# shared numbers for the x axis module, all from the spec
from argus.spec import P, pat

(Y_ROD_A, XZ), (Y_ROD_B, _) = pat('x_rods')      # rod centres (y, z)
SY, SZ = pat('x_screw')[0]                       # lead screw centre (y, z)
L, R = P['xblk_l'], P['xblk_r']                  # inner faces of the end blocks
EX, EY = P['x_endstop']                          # endstop sensor centre
ROD_X = (L - 10, R + 10)                         # rod ends
CPL = (L - 14 + 12, L - 14 + 37)                 # coupling span
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
- If you can run code: `pip install -r requirements.txt`, then `python tools/check.py x_endstop_pedestal` (seconds) and `python tools/check.py` (whole machine, about a minute). All must pass.
- If you cannot run code: deliver the file anyway; the checks run automatically on the pull request.

## Deliver
1. The full new `parts/x_axis/x_endstop_pedestal.py`.
2. Three lines: what changed, which numbers are measured vs assumed, what you are unsure about.
3. A change request, only if rule 3 applied.

Repo: https://github.com/mmucteba/argus (read everything else in CONTEXT.md if you have access).
