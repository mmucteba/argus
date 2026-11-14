# endstop_board evidence

## Sensor: Vishay TCST2103 (datasheet)

Source: Vishay document 81147, rev 1.0, 17-Aug-09, package drawing 6.550-5040.01-4
https://wwwlegacy.vishay.com/docs/81147/tcst2103.pdf

`tcst2103_package_drawing.png` is the package drawing from that datasheet. Read from it, in mm:

| Value in facts.yaml | Drawing | Was | Note |
|---|---|---|---|
| `fork_l` | 24.5 +-0.1 | 24.5 | match |
| `fork_w` | 6.3 +0.05 -0.10 | 6.3 | match |
| `gap` | 3.1 +0.2 -0.1 | 3.1 | match |
| `hole_spacing` | 19 +-0.1 | 19.0 | match, these are the flange holes of the sensor |
| `base_h` | 3.1 +-0.1 | 2.8 | changed, flange thickness |
| `fork_h` | 10.8 - 3.1 = 7.7 | 8.0 | changed, total height 10.8 +-0.1 is unchanged |
| `hole_d` | 3.3 | new | flange hole diameter |
| `body_l` | 11.9 +-0.1 | new | length of the upper body that carries the two fork arms |
| `axis_h` | 10.8 - 2.6 = 8.2 | new | optical axis above the bottom of the sensor |

The 3.1 +-0.1 dimension on the right of the front view is read as the flange thickness. Confirm it with calipers on the real part.

## Board: not verified yet

`pcb_l`, `pcb_w`, `pcb_t` are still from the Robolink listing and guesses. No maker drawing exists for the red board.

The listing says "TCST2103 type", so the sensor on our boards may be a clone. When the boards arrive, measure with calipers and add photos here:
- board length, width, thickness
- hole spacing and hole diameter
- flange thickness and total sensor height
- fork gap
