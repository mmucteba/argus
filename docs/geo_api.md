# Geometry helpers (argus.geo)

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
