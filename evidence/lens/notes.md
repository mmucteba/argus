# lens evidence

## Maker's page and outline drawing (Waveshare)

Source: https://www.waveshare.com/product/100x-microscope-lens-for-pi.htm
`outline_drawing.png` is a screenshot of Waveshare's outline drawing for this lens (unit mm), as shown on the product pages of Waveshare and of the shop we buy from (Devresel).

### Dimensioned on the drawing

| Value in facts.yaml | Drawing | Was | Note |
|---|---|---|---|
| `d` | 39 | 39.0 | match, barrel diameter at the front end |
| `length` | 112 | 112.0 | match, front end to the shoulder where the C mount thread starts (thread not included) |
| `flange_d` | 44.5 | new | cone flange at the camera end, wider than the barrel |
| `thread_d` | 1"-32UN = 25.4 | new | C mount thread |

### From the spec table on the same page

Magnification 0.12x to 1.8x, operating distance 55 to 285 mm, image format 1/2", weight 202 g, C/CS mount with adapter. No NA or F-number is published.

### Not dimensioned: scaled from the drawing, rough only

The drawing is not to one scale (about 6.6 px/mm along the lens, about 8 px/mm across it), so treat these as plus or minus a few mm. Distances are from the front end of the lens:

| Feature | From the front end |
|---|---|
| front rings and groove | 0 to about 15 mm |
| plain barrel | about 15 to 36 mm |
| knurled zoom ring, slightly wider than the barrel (about 41 mm) | about 36 to 52 mm |
| plain barrel | about 52 to 98 mm |
| 44.5 mm flange and cone | about 98 to 108 mm |

Why it matters: the lens clamp sits at z 148 to 192. With the lens front at z 123 (focal plane 68 plus working distance 55) that is 25 to 69 mm from the front end, so the clamp would sit on the zoom ring. The clamp must grip a plain section and leave the zoom ring free; the long plain section is the rear one.

## Still unverified

- `wd_max_zoom` 55: the page gives 55 to 285 mm for the whole zoom range and does not say which end belongs to 1.8x. Measure the height at best focus.
- `na_est` 0.04: an estimate, not published. Measure the resolution on the bench (slanted edge or a resolution target).
- `thread_len` 4.0: assumed, not on the drawing.
- Zoom ring position and width: measure with calipers when the lens arrives.
