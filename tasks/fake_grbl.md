---
title: "[software] fake_grbl: a fake GRBL 1.1 to test against"
labels: software
part: software/fake_grbl
who: Any strong AI
---
# Task: fake GRBL

**Suggested model:** any strong AI. **Folder:** `software/fake_grbl/`. No hardware.

ARGUS T18 is a low-cost microscope slide scanner (METU EE493). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera; an Arduino Uno runs GRBL 1.1 for the motors; a Raspberry Pi 3B+ runs the scan and streams tiles to a laptop, which stitches them and runs a tumour classifier. The software is built as small modules with fixed interfaces and fakes for the hardware, so everything is tested before the boards exist.

## Goal
A pretend Arduino running GRBL 1.1, good enough that the real serial code (`grbl_link`) and the scan loop can be tested on a laptop. It must speak the same text protocol as GRBL over a serial port.

## Interface
```python
from software.fake_grbl import FakeGrbl
g = FakeGrbl(clock=None)     # clock: callable returning seconds; default time.monotonic; tests pass a fake clock
g.write(b'G90 G1 X10 Y5 F900\n')
line = g.readline()          # bytes ending in b'\r\n', b'' when nothing is waiting
```
Behave like GRBL 1.1:
- After reset (`g.write(b'\x18')`) send `Grbl 1.1h ['$' for help]`, then the `ALARM` state until `$H` (homing) or `$X` (unlock).
- Each line gets `ok` or `error:N` (unsupported: `error:20`). `?` is real time: no `ok`, it answers `<Idle|MPos:x,y,z|FS:0,0>` or `<Run|...>`, `<Home|...>`, `<Alarm|...>`. Three decimals in the positions.
- **Motion:** G90 / G91, G0 / G1 with X Y Z F (mm/min), `$J=G91 X1 F300` jogs, and `G4 P0.01` waits. Moves take real (or fake-clock) time with trapezoid profiles using `P['vmax']` and `P['accel']` for X and Y, and 10 mm/min for Z.
- **Planner:** queue up to 15 moves; `ok` comes back when a line is queued, not when the move ends (like GRBL).
- **Homing:** `$H` homes X and Y only (our GRBL is built that way). Machine X and Y become the travel minimum (`P['x_travel'][0]`, `P['y_travel'][0]`); Z keeps its value.
- **Limits:** like our real setup (soft limits off, endstops at X- and Y- only): a move that goes below the travel minimum in X or Y hits the switch, gives `ALARM:1` and stops. Moves past the maximum are not caught by GRBL; the Pi software must keep them in range.
- **Light:** `M8` / `M9` switch the LED; expose it as `g.led_on` and as `A:F` in the status.
- **Test hooks:** `g.inject_alarm(code)` to test error paths, and `g.log` (list of received lines).

## Tests
- reset banner, alarm after reset, `$X` unlocks
- a 10 mm X move at F1200 reports Run then Idle and takes the time the trapezoid says (fake clock)
- `ok` arrives before the move finishes
- G91 relative moves add up; `$J` jogs
- homing sets the position to the travel minimum
- a move below the X or Y minimum gives ALARM:1, and the state stays Alarm until `$X`
- M8 / M9 change `led_on`

## Rules
1. Everything goes in `software/fake_grbl/`: `__init__.py`, the code, `interface.md` (the interface below in your words), `tests/test_*.py`. Do not edit other folders.
2. Plain Python 3.13 with numpy, scipy and Pillow only (already in requirements.txt); no new libraries, no downloads, no hardware.
3. Read machine numbers from `from argus.spec import P` (spec/params.yaml), never copy them.
4. `python -m pytest software/fake_grbl -q` must pass in under 30 s. The same tests run automatically on the pull request.
5. Code comments short, lowercase, no punctuation. Small functions, type hints, no global state.

## Deliver
The files above, as a pull request (template in the repo) or as files your teammate uploads. Three lines at the end: what works, what is assumed, what is missing.
