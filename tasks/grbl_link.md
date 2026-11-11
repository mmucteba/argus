---
title: "[software] grbl_link: talk to GRBL over serial"
labels: software
part: software/grbl_link
who: Any strong AI
---
# Task: GRBL link

**Suggested model:** any strong AI. **Folder:** `software/grbl_link/`. No hardware.

ARGUS T18 is a low-cost microscope slide scanner (METU EE493). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera; an Arduino Uno runs GRBL 1.1 for the motors; a Raspberry Pi 3B+ runs the scan and streams tiles to a laptop, which stitches them and runs a tumour classifier. The software is built as small modules with fixed interfaces and fakes for the hardware, so everything is tested before the boards exist.

## Goal
The Pi side of the motor control: one class that sends G-code to the Uno and knows when the stage has really stopped. It works with a real pyserial port or with any object that has `write(bytes)` and `readline() -> bytes`. A separate task builds `software/fake_grbl`; if it is not merged yet, test against a small stub inside your tests.

## Interface
```python
from software.grbl_link import GrblLink, GrblError
g = GrblLink(port)                 # port: object with write(bytes) and readline() -> bytes
g.reset()                          # ctrl-x, wait for the banner
g.unlock()                         # $X
g.home(timeout=60)                 # $H, waits until Idle
g.move_to(x=None, y=None, z=None, feed=900)   # absolute G90 G1; only the given axes
g.wait_idle(timeout=3.0)           # sends G4 P0.01, waits for its ok, then polls ? until Idle
g.status() -> dict(state='Idle', x=..., y=..., z=...)
g.light(True)                      # M8 / M9
```
GRBL 1.1 facts to rely on:
- Every line gets `ok` or `error:N`.
- `?` is answered right away with `<State|MPos:x,y,z|...>` and no `ok`.
- `ALARM:N` can arrive at any time.
- `ok` for `G4` means the planner is empty, so "move finished" = `G4 P0.01` ok + state Idle.
- Use the simple send-and-wait-for-ok protocol, one line at a time (keep it simple, no character counting).

## Behaviour
- `GrblError` with the code and a readable message for `error:N` and `ALARM:N`.
- Every wait has a timeout, and a timeout raises.
- Log every line sent and received at debug level.

## Tests
- protocol with a scripted stub: ok, error:N, ALARM in the middle of a wait, status parsing with and without the `WCO` and `FS` fields
- `wait_idle` timing out raises
- with `software.fake_grbl` merged: home, move, wait_idle, light against it (skip the test if the module is missing)

## Rules
1. Everything goes in `software/grbl_link/`: `__init__.py`, the code, `interface.md` (the interface below in your words), `tests/test_*.py`. Do not edit other folders.
2. Plain Python 3.13 with numpy, scipy and Pillow only (already in requirements.txt); no new libraries, no downloads, no hardware.
3. Read machine numbers from `from argus.spec import P` (spec/params.yaml), never copy them.
4. `python -m pytest software/grbl_link -q` must pass in under 30 s. The same tests run automatically on the pull request.
5. Code comments short, lowercase, no punctuation. Small functions, type hints, no global state.

## Deliver
The files above, as a pull request (template in the repo) or as files your teammate uploads. Three lines at the end: what works, what is assumed, what is missing.
