---
title: "[design] led_tower: fit the real LED card and heatsink"
labels: design, fable
part: led_tower
who: Fable (hard geometry)
---
# Task: LED tower

**Suggested model:** Fable or the strongest model you have. **Part file:** `parts/light/led_tower.py`. **Spec version:** 3. **Status:** needs-measurement.

You are designing one 3D printed part of ARGUS T18, a low-cost automated microscope slide scanner (METU EE493 capstone). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera. Parts are CadQuery Python, modelled in assembled position. Many people work on different parts at the same time, so each part has a contract: a box it must stay inside and holes it must keep where other parts meet it.

## Goal
Redesign the LED tower for the parts we actually bought: the Robotistan LED card (23 x 30 mm, driver on board) and the 20 x 15 x 10 mm heatsink. The light must still come up the optical axis through the diffuser, the tower must stay out of the X carriage path, and the card must be easy to take out. Also update the two placeholder shapes in parts/light/bought.py ('Heatsink' and '3 W LED on star PCB', you may rename the second to '3 W LED card') so they match the real parts.

## Inputs (measurements or listing data)
- LED card, Robotistan "Sürücülü 3W Power LED Kartı": PCB about 23 x 30 mm (listing), about 1.6 mm thick (assumed), LED in the middle of the card (assumed), 3-pin header VCC / GND / SIG on one short edge (assumed). Mounting hole positions unknown: hold the card in a pocket or under clips, no screws through the card.
- Heatsink, robotus "Aluminum heatsink 20x10x15": 20 x 15 x 10 mm block (listing), stuck under the card with thermal tape, the card is bigger than the heatsink.
- The LED card header needs about 10 mm free for Dupont plugs, and the wires leave through a side slot.
- Diffuser stays: 28 mm disc on the ledge at z 22, top at z 25 (interface diffuser_seat).
- Everything above z 25 belongs to the stage; the X carriage saddles pass at |y| >= 32.5 mm.
- All sizes are from the listings: say in your note which ones you assumed, we measure when the parts arrive.

## Contract
- Envelope (x0, x1, y0, y1, z0, z1): [-30, 30, -30, 30, 0, 25]. Stay inside it.
- Moves with: nothing (fixed to the base). Prints as assembled (bottom face down).
- Interface holes you must keep exactly (other parts depend on them):
- **diffuser_seat**: the 28 mm diffuser disc sits on the LED tower ledge at z 22, top at 25. Axis z, centres (0, 0), starts at z = 22, goes +z at least 3 mm, bore, diameter 28.4 mm. Mates with: a bought part. In code: `pat('diffuser_seat')`.
- Parts whose space is next to yours:
  - X carriage (`x_carriage`, envelope [-51, 51, -57, 84, 11, 35])
- Bought parts in or next to your space (assembled, stage at home):
  - Base plate: box [-137, 163, -117, 153, -18, 0] (18 mm plywood (or 6 mm aluminium, then tap M4 instead of wood screws). The flat, heavy reference that every other part bolts to. Printing it is possible but it would be less flat and lighter, so buy it.)
  - Heatsink: box [-10, 10, -10, 10, 3, 11] (20 x 20 mm aluminium, LED star screwed on with 2 M3x8 and thermal paste)
  - 3 W LED on star PCB: box [-10, 10, -10, 10, 11, 15] (placeholder shape: the real part is the 23 x 30 mm Robotistan LED card with its own driver, 5 V, on/off from GRBL CoolEn (A3))
  - Opal diffuser: box [-13.9, 13.9, -13.9, 13.9, 22, 25] (28 mm disc of 3 mm opal acrylic; sets how evenly the slide is lit)

## Rules
1. Change only `parts/light/led_tower.py` and `parts/light/bought.py`. Keep `META` and `build()`.
2. Take numbers from `P[...]` and `pat(...)`. Never type in a number another part depends on.
3. If the goal needs a bigger envelope, a moved interface or a new parameter, do not change shared files: finish what you can and write a **change request** (what, why, the new numbers) at the end of your answer.
4. Print-friendly: no supports in the chosen orientation (overhangs steeper than 45 degrees from vertical need a chamfer), walls at least 1.2 mm, fits a 220 x 220 x 250 mm bed.
5. Code comments: short, lowercase, no punctuation.

## Parameters this part uses now
- `diffuser_top` = 25

## Current code
`parts/light/led_tower.py`
```python
# led tower: holds heatsink, led card and diffuser on the optical axis
from argus.geo import *
from argus.spec import P, IF

META = dict(name='LED tower', group='F', layer=1, sub='Light source', step=2, color='frame', orient='zmin',
            note='Holds heatsink, LED and diffuser on the optical axis. Wire exits through the side slot. Print in white PLA.',
            hw={'Wood screw 4x16': 3})


def build():
    zt = P['diffuser_top']
    seat = IF['diffuser_seat']
    zs, rs = seat['holes']['led_tower']['plane'], seat['d'] / 2
    t = fuse(cyl(16.5, (0, 0, 0), (0, 0, zt)), cyl(25, (0, 0, 0), (0, 0, 3)))
    t = cut(t, cyl(14.6, (0, 0, 3), (0, 0, 18.4)), cone(14.6, 13, (0, 0, 18.39), (0, 0, 20.01)), cyl(13, (0, 0, 20), (0, 0, zs + 0.1)),
            cyl(rs, (0, 0, zs), (0, 0, zt + 0.1)), box(10, 18, -3, 3, 3, 9))
    base = [(21 * math.cos(math.radians(a)), 21 * math.sin(math.radians(a))) for a in (90, 210, 330)]
    for x, y in base:
        t = t.cut(wood_hole(x, y, 3, 0))
    return t, [(x, y, 'LED tower') for x, y in base]
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
- If you can run code: `pip install -r requirements.txt`, then `python tools/check.py led_tower` (seconds) and `python tools/check.py` (whole machine, about a minute). All must pass.
- If you cannot run code: deliver the file anyway; the checks run automatically on the pull request.

## Deliver
1. The full new `parts/light/led_tower.py` and `parts/light/bought.py`.
2. Three lines: what changed, which numbers are measured vs assumed, what you are unsure about.
3. A change request, only if rule 3 applied.

Repo: https://github.com/mmucteba/argus (read everything else in CONTEXT.md if you have access).
