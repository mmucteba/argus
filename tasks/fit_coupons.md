---
title: "[test-print] fit coupons: check holes and bores before the big parts"
labels: test-print
part: test_prints/fit_coupons.py
who: Any strong AI
---
# Task: fit coupons

**Suggested model:** any strong AI. **File:** `test_prints/fit_coupons.py` (new). Read `docs/geo_api.md` for the helpers.

ARGUS T18 is a low-cost microscope slide scanner (METU EE493). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera; an Arduino Uno runs GRBL 1.1 for the motors; a Raspberry Pi 3B+ runs the scan and streams tiles to a laptop, which stitches them and runs a tumour classifier. The software is built as small modules with fixed interfaces and fakes for the hardware, so everything is tested before the boards exist.

## Goal
One small, fast print that tells us how our printer makes holes. Then the hole sizes in `spec/params.yaml` (`insert_d`, `m3_clear_d`, rod bores 8.1, LM8UU saddle 15.1, 608 seat 22.15) can be set from facts before printing 500 g of parts.

## What to put on it
One plate, at most 100 x 60 mm and 6 to 10 mm thick:
- **Rod bores:** 8.0 / 8.1 / 8.2 mm, through holes, for an 8 mm rod
- **LM8UU saddles:** 15.0 / 15.1 / 15.2 mm, half-pipe pockets like on the X carriage (open on top, 24 mm long)
- **608 seats:** 22.0 / 22.15 / 22.3 mm, 7 mm deep
- **M3 heat-set insert holes:** 3.8 / 4.0 / 4.2 mm, 6 mm deep
- **M3 clearance holes:** 3.2 / 3.4 / 3.6 mm
- **M2.5 tap holes:** 2.0 / 2.2 / 2.4 mm
- A label next to every feature (engraved numbers 0.6 mm deep), so nobody needs a caliper to know which is which.

## Rules
1. `META = dict(name='Fit coupons', orient='zmin', note='...')` and `build()` returning one solid at the origin.
2. Prints flat with no supports, walls at least 1.5 mm between features.
3. Code comments short, lowercase, no punctuation.
4. `python tools/check.py fit_coupons` must pass.

## Deliver
The file, as a pull request or to your teammate. After it is printed, write on this issue which size fits each real part best. That becomes a change request for the spec.
