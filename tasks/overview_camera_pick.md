---
title: "[research] pick the overview USB camera"
labels: research
part: -
who: Any strong AI
---
# Task: pick the overview camera

**Suggested model:** any AI with web search. **Output:** a comment on this issue (no code).

ARGUS T18 is a low-cost microscope slide scanner (METU EE493). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera; an Arduino Uno runs GRBL 1.1 for the motors; a Raspberry Pi 3B+ runs the scan and streams tiles to a laptop, which stitches them and runs a tumour classifier. The software is built as small modules with fixed interfaces and fakes for the hardware, so everything is tested before the boards exist.

## Goal
Find the USB camera that takes one photo of the whole slide before the scan, so the user can pick the area to scan. The Pi's camera port is taken by the HQ camera, so it has to be USB (UVC, works on Raspberry Pi OS without drivers).

## Requirements
- Sees the whole 75 x 25 mm slide from about 110 mm away, so a horizontal field of at least about 45 degrees with margin (wider is fine, we crop).
- Focus at 100-120 mm: an M12 lens you can turn, or fixed focus that is sharp that close (many are not, check reviews).
- At least 1920 x 1080, better 5 MP. Small board with mounting holes, not a webcam in a plastic case.
- Sold in Turkey (Robotistan, Robotsepeti, Direnc, SAMM, Trendyol, Hepsiburada), ideally under 700 TL.

## Deliver
1. A table of 3 candidates: name, link, price, sensor and resolution, lens and field of view, focus type, board size and hole pattern (from the datasheet or a photo), cable length.
2. Your pick and why.
3. Anything still unknown.

The integrator then puts the pick in `spec/bom.yaml`, and the overview_arm design task stops waiting.
