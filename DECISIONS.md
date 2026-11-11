# Decisions

Newest first. Each one says what we picked and why, so nobody re-opens it by accident. To change one, open a change request.

| ID | Date | Decision | Why | Revisit when |
|---|---|---|---|---|
| D-17 | 11 Nov 2026 | Work is split into one file per printed part, with shared numbers in `spec/` and checks on every pull request | Several people and AIs can design in parallel without breaking each other's parts | never (how the repo works) |
| D-16 | 8 Nov 2026 | No Z endstop: GRBL homes X and Y only (`HOMING_CYCLE_0` = X and Y), soft limits off, the Pi keeps moves inside the travel | Only 2 switches are needed; the third optical endstop stays as a spare | if we want soft limits on all axes: spare endstop as Z home |
| D-15 | 8 Nov 2026 | LED ring data from Pi GPIO10 (SPI) through a 74HCT125 and 470 ohm; ring and LED card on the 5 V buck; Pi on its own supply | 3.3 V data is not enough for WS2812 at 5 V; separate Pi supply avoids brownouts | |
| D-14 | 8 Nov 2026 | Waveshare 100X zoom lens (0.12-1.8x) at 1.8x instead of the 4x/0.10 objective, 150 mm tube and C-C ring | 3.49 x 2.62 mm field, 48 tiles instead of 221, about 55 mm working distance, about 390 um depth of field; same price | the real resolution is measured: estimate about 8 um (NA not published) meets the 20 um spec but is softer than PCam, so the AI trains with blur augmentation |
| D-13 | 8 Nov 2026 | Raspberry Pi 3B+ instead of the Pi 4 | The Pi only captures, sends G-code and streams tiles; stitching and AI run on the laptop; saves about 2,800 TL | if processing moves onto the Pi |
| D-12 | 1 Nov 2026 | DRV8825 on X and Y (1/16, 1.0 A), A4988 on Z (half step, 0.1 A) after the 28BYJ-48 bipolar mod | GRBL outputs step and dir only; the ULN2003 needs a 4-phase pattern | |
| D-11 | 1 Nov 2026 | LED card on 5 V from the LM2596, on/off from GRBL coolant (M8/M9 on A3), brightness by camera exposure | No free PWM pin worth fighting for; exposure control is cleaner | |
| D-10 | 1 Nov 2026 | Overview camera will be a USB module | The Pi has one camera port and the HQ camera uses it | |
| D-09 | 31 Oct 2026 | Long X axis (95 mm) at the bottom fixed to the base, short Y axis (30 mm) on top; carriages printed in one piece with half-pipe saddles, LM8UU zip-tied | Both rods of an axis sit in one printed part, so they are parallel by print; no supports | |
| D-08 | 28 Oct 2026 | Tile classifier fine-tuned on PCam, heatmap thresholding for segmentation | Public CC0 data, small models train on Colab | if Dice is low: U-Net |
| D-07 | 28 Oct 2026 | Two light channels: transmitted LED and reflected ring | Glass slides need light from below, printed targets need light from above | |
| D-06 | 28 Oct 2026 | Raster scan, X always approached from the same side, 25 % overlap | Removes reversal backlash without calibration | EE494 trajectory study |
| D-05 | 28 Oct 2026 | Pi does acquisition, PC does stitching and AI | The PC has the memory for the mosaic | |
| D-04 | 28 Oct 2026 | GRBL 1.1 on Arduino Uno + CNC Shield V3 | Homing, limits and acceleration work on day one | custom STM32 firmware for EE494 if we need a hardware trigger |
| D-03 | 28 Oct 2026 | Stage on 8 mm rods + LM8UU, T8 lead-8 screws, spring nuts | Cheapest option that meets 250 um with a large margin | MGN12 rails if budget frees up |
| D-01 | 28 Oct 2026 | The slide moves, the optics stay still | Light and optics never move against each other, so one flat-field image works for every tile | never |
