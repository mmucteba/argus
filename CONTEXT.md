# ARGUS T18: context for AI agents

Read this first. It tells you what the project is, how the repo is built, and the rules that let many people and AIs work on it at the same time.

## The project

ARGUS T18 is a low-cost automated pathology slide scanner, the METU EE493 capstone of team T18.
- **Mechanics:** a two-axis stage moves a 75 x 25 mm glass slide under a fixed Waveshare zoom lens (0.12-1.8x, used at 1.8x) and a Raspberry Pi HQ camera.
- **Light:** a 3 W LED card lights glass slides from below. A 24-LED ring lights printed paper targets from above.
- **Control:** an Arduino Uno with a CNC Shield V3 runs GRBL 1.1 and drives two NEMA17 steppers (X, Y) and a 28BYJ-48 (focus). A Raspberry Pi 3B+ runs the scan, and a laptop stitches the tiles and runs the tumour classifier.
- **Budget:** 17,427 TL ($350).

The current state is **model v0.3, spec version 3**. Decisions and their reasons are in `DECISIONS.md`.

## Repo map

| Path | What | Who edits |
|---|---|---|
| `spec/params.yaml` | Every shared number (positions, sizes, optics, motion, print settings) | integrator |
| `spec/interfaces.yaml` | Where parts meet: hole patterns both sides read | integrator |
| `spec/contracts.yaml` | Per printed part: status, envelope (space it may use), spec version it was checked against | integrator |
| `spec/bom.yaml` | Every bought item, store, link, price, status | integrator |
| `spec/meta.yaml` | Layer names, build steps, colours | integrator |
| `argus/` | Shared library: spec loader, geometry helpers, bought part shapes, registry | integrator |
| `parts/<module>/<part>.py` | **One printed part per file.** This is where design tasks happen | the task owner |
| `parts/<module>/bought.py` | Shapes of the bought parts in that module | integrator, or a task that lists it |
| `parts/<module>/layout.py` | Numbers shared inside one module, all read from the spec | integrator |
| `checks/` | Per-part checks and whole-machine checks | integrator |
| `tools/check.py` | Runs the checks | |
| `tools/task.py` | Writes a self-contained prompt for one part | |
| `tools/build.py` | 3D viewer, STEP, STL print pack, drilling template into `build/` | |
| `tools/pages/` | Parts-and-budget page and wiring page | |
| `software/` | Scan software, not started yet (plan in software/README.md) | |
| `docs/geo_api.md` | Geometry helper reference | |

Modules: `base`, `light`, `x_axis`, `y_axis`, `slide`, `column`, `optics`, `overview`, `electronics`.

## How a part works

- Every printed part is one file with a `META` dict and a `build()` function. `build()` returns the CadQuery solid in its **assembled position**, or `(solid, base_holes)` for parts screwed to the plywood. See `docs/geo_api.md` for the helpers and an example.
- **Coordinates:** units are mm and z is up. The optical axis is x = 0, y = 0. The top of the plywood is z = 0. The focal plane is at z = 68.
- **Motion groups:** F is fixed, X moves with the X carriage, Y moves with the Y carriage (on top of X), Z moves with focus.
- **Numbers:** they come from `P['name']` (params.yaml) and `pat('interface')` (interfaces.yaml). Interfaces can write their numbers as formulas of params, so moving one parameter moves both sides of a joint.

## Rules

1. **Stay in your file.** A design task changes only its part file, plus any file the task lists.
2. **No private copies of shared numbers.** If another part depends on a value, read it from the spec.
3. **Stay inside your envelope and keep every interface hole.** The checks fail otherwise.
4. **Need a shared change? Write a change request.** That covers a bigger envelope, a moved hole, a new parameter or a different bought part. Do not edit `spec/`, `argus/` or another part. Finish what you can and describe the change (file, name, new value, why) at the end of your answer, or open an issue with the Change request template.
5. **Printable without supports.** Downward faces must be steeper than 45 degrees from horizontal (otherwise chamfer them). Walls must be at least 1.2 mm. The part must fit a 220 x 220 x 250 mm bed in its `orient`.
6. **Say what you guessed.** Every number that is not from a measurement or a datasheet must be named as assumed in your delivery note.
7. **Code comments:** short, lowercase, no punctuation.

## Check your work

```
pip install -r requirements.txt
python tools/check.py <part>      # one part, seconds
python tools/check.py             # every part + the whole machine, about a minute
```

**Part checks:**
- one valid solid
- inside the envelope
- every interface hole open and in the right place
- fits the bed
- no supports needed
- built for the current spec

**Whole-machine checks:**
- no collisions over 72 stage and focus poses
- no overlaps inside a moving group
- light path clear
- overview camera view clear
- rod sag
- motor torque margins
- column stiffness
- print time and filament
- scan time

The same checks run on every pull request and post a report. Red means fix it; the report says where and why.

## Deliver

**With repo access:** open a branch, change your file, run the part check, and open a pull request using the template. Say which numbers are measured and which are assumed.

**From a chat:** give back the full file plus that note. Your teammate uploads it.

## Status of the parts

`python tools/status.py` lists every printed part with its status:
- `ok`
- `needs-measurement`: waiting for the real part to be measured
- `redesign`
- `in-progress`

The open question for each part is listed with it. GitHub issues are the task list. An issue with an assignee is taken.
