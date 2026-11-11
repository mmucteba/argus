# builds build/argus-wiring.html: block diagram, wire list, driver setup, grbl settings, first power-up
import json, html
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from argus import bom as S
from argus.spec import P

E = html.escape

# ---------------- diagram
VB_W, VB_H = 1100, 760
blocks = {
    # key: x, y, w, h, title, sub, gnd, dashed
    'adp': (20, 30, 180, 50, '12 V 3 A adapter', 'centre +, 5.5 x 2.1', False, False),
    'jack': (20, 110, 180, 44, 'DC jack 2.1 mm', 'screw terminals', True, False),
    'fuse': (20, 184, 180, 44, 'Fuse 3 A', '5 x 20 inline holder', False, False),
    'sw': (20, 258, 180, 44, 'Rocker switch KCD1', 'power and e-stop', False, False),
    'bus12': (20, 332, 180, 44, '12 V bus', 'Wago 221', False, False),
    'buck': (250, 332, 190, 52, 'LM2596 buck', '12 V to 5.0 V, set first', True, False),
    'bus5': (250, 432, 190, 44, '5 V bus', 'Wago 221', False, False),
    'shift': (250, 524, 190, 52, '74HCT125', '3.3 V to 5 V, 1 channel', True, False),
    'ring': (250, 628, 190, 52, 'WS2812 ring, 24 LEDs', '1000 uF across 5V-GND', True, False),
    'psu': (20, 678, 180, 44, 'Pi PSU 5.1 V 2.5 A', 'micro USB', False, False),
    'mx': (830, 62, 250, 40, 'NEMA17 · X axis', '17HS4401, 4 wires', False, False),
    'my': (830, 122, 250, 40, 'NEMA17 · Y axis', '17HS4401, 4 wires', False, False),
    'mz': (830, 182, 250, 40, '28BYJ-48 · focus', 'bipolar mod, red unused', False, False),
    'ex': (830, 258, 250, 44, 'X endstop · optical', 'VCC, GND, OUT', True, False),
    'ey': (830, 318, 250, 44, 'Y endstop · optical', 'VCC, GND, OUT', True, False),
    'led': (830, 388, 250, 44, '3 W LED card', 'VCC, GND, SIG', True, False),
    'hq': (830, 560, 250, 44, 'Pi HQ camera · IMX477', 'C/CS mount + zoom lens', False, False),
    'lap': (830, 626, 250, 44, 'Laptop', 'stitching, AI, viewer', False, False),
    'ovc': (830, 692, 250, 44, 'Overview USB camera', 'step 10, later', False, True),
}
wires = [
    # class, points, label, label xy, anchor
    ('w12', [(110, 80), (110, 110)], '', None, ''),
    ('w12', [(110, 154), (110, 184)], '', None, ''),
    ('w12', [(110, 228), (110, 258)], '', None, ''),
    ('w12', [(110, 302), (110, 332)], '', None, ''),
    ('w12', [(200, 346), (225, 346), (225, 100), (490, 100)], '12 V, 20 AWG', (300, 94), 'start'),
    ('w12', [(200, 362), (250, 362)], '', None, ''),
    ('w5', [(345, 384), (345, 432)], '5.0 V', (353, 412), 'start'),
    ('w5', [(345, 476), (345, 524)], 'pin 14', (353, 504), 'start'),
    ('w5', [(250, 454), (232, 454), (232, 654), (250, 654)], '', None, ''),
    ('w5', [(440, 446), (470, 446), (470, 500), (800, 500), (800, 288)], '5 V to endstops, LED card', (642, 494), 'start'),
    ('w5', [(800, 288), (830, 288)], '', None, ''),
    ('w5', [(800, 348), (830, 348)], '', None, ''),
    ('w5', [(800, 418), (830, 418)], '', None, ''),
    ('w5', [(200, 700), (490, 700)], '5.1 V micro USB', (300, 694), 'start'),
    ('mot', [(760, 82), (830, 82)], '', None, ''),
    ('mot', [(760, 142), (830, 142)], '', None, ''),
    ('mot', [(760, 202), (830, 202)], '', None, ''),
    ('sig', [(830, 272), (760, 272)], '', None, ''),
    ('sig', [(830, 332), (760, 332)], '', None, ''),
    ('sig', [(760, 402), (830, 402)], '', None, ''),
    ('sig', [(490, 600), (465, 600), (465, 550), (440, 550)], '', None, ''),
    ('sig', [(345, 576), (345, 628)], '1Y, 470 ohm, DIN', (353, 606), 'start'),
    ('data', [(625, 470), (625, 560)], 'USB A-B', (633, 532), 'start'),
    ('data', [(760, 582), (830, 582)], '', None, ''),
    ('data', [(760, 648), (830, 648)], '', None, ''),
    ('data dash', [(760, 700), (830, 700)], '', None, ''),
]
ports = [
    # text, x, y, anchor (inside the shield and pi blocks)
    ('12-36 V in', 500, 104, 'start'),
    ('X  DRV8825', 750, 86, 'end'), ('Y  DRV8825', 750, 146, 'end'),
    ('Z  A4988', 750, 206, 'end'), ('X-  D9', 750, 276, 'end'), ('Y-  D10', 750, 336, 'end'),
    ('CoolEn  A3', 750, 406, 'end'), ('USB-B', 625, 462, 'middle'),
    ('USB-A', 625, 578, 'middle'), ('CSI', 750, 586, 'end'), ('Ethernet', 750, 652, 'end'), ('USB-A', 750, 704, 'end'),
    ('pin 19  GPIO10', 500, 604, 'start'), ('pin 20  GND', 500, 622, 'start'), ('micro USB', 500, 704, 'start'),
]
inner = [
    # small mono notes inside the shield
    ('Uno pins via the shield', 506, 140), ('D2 D3 D4  step X Y Z', 506, 160), ('D5 D6 D7  dir X Y Z', 506, 178),
    ('D8        enable, all', 506, 196), ('D9 D10    X, Y limits', 506, 214), ('A3        LED: M8 on, M9 off', 506, 232),
    ('D12       free, Z limit later', 506, 250),
    ('Drivers', 506, 290), ('X, Y  1/16 step, 1.0 A', 506, 310), ('Z     1/2 step, 0.1 A', 506, 328),
]


def gnd_glyph(x, y):
    return (f'<g class="gnd"><line x1="{x}" y1="{y}" x2="{x}" y2="{y + 5}"/><line x1="{x - 6}" y1="{y + 5}" x2="{x + 6}" y2="{y + 5}"/>'
            f'<line x1="{x - 4}" y1="{y + 8}" x2="{x + 4}" y2="{y + 8}"/><line x1="{x - 2}" y1="{y + 11}" x2="{x + 2}" y2="{y + 11}"/></g>')


svg = [f'<svg viewBox="0 0 {VB_W} {VB_H}" role="img" aria-labelledby="dgt dgd"><title id="dgt">ARGUS wiring diagram</title>'
       f'<desc id="dgd">12 V adapter through fuse and switch to the CNC shield and the 5 V buck; the buck feeds the LED card, '
       f'the LED ring through a 74HCT125 and the endstops; the shield drives two NEMA17 and the 28BYJ-48 and reads the X and Y '
       f'endstops; the Pi talks to the Uno over USB, reads the HQ camera over CSI and sends tiles to the laptop.</desc>']
for cls, pts, lab, lxy, anc in wires:
    d = ' '.join(f'{x},{y}' for x, y in pts)
    svg.append(f'<polyline class="w {cls}" points="{d}"/>')
for k, (x, y, w, h, t, s, g, dash) in blocks.items():
    svg.append(f'<g class="blk{" dash" if dash else ""}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5"/>'
               f'<text class="bt" x="{x + 10}" y="{y + 19}">{E(t)}</text><text class="bs" x="{x + 10}" y="{y + h - 9}">{E(s)}</text>'
               f'{gnd_glyph(x + w - 14, y + 7) if g else ""}</g>')
svg.append('<g class="blk big"><rect x="490" y="30" width="270" height="440" rx="6"/>'
           '<text class="bt" x="506" y="52">Arduino Uno + CNC Shield V3</text><text class="bs" x="506" y="68">GRBL 1.1, homing X and Y only</text>'
           + gnd_glyph(746, 37) + '</g>')
svg.append('<g class="blk big"><rect x="490" y="560" width="270" height="160" rx="6"/>'
           '<text class="bt" x="560" y="650">Raspberry Pi 3B+</text><text class="bs" x="560" y="668">scan service, picamera2</text></g>')
for t, x, y in inner:
    svg.append(f'<text class="pin" x="{x}" y="{y}">{E(t)}</text>')
for t, x, y, a in ports:
    svg.append(f'<text class="port" x="{x}" y="{y}" text-anchor="{a}">{E(t)}</text>')
for cls, pts, lab, lxy, anc in wires:
    if lab:
        svg.append(f'<text class="wl" x="{lxy[0]}" y="{lxy[1]}" text-anchor="{anc}">{E(lab)}</text>')
svg.append('</svg>')
SVG = '\n'.join(svg)

# ---------------- wire list
W = [
    ('12 V power, 20 AWG', [
        ('w12', '12 V adapter plug', 'DC jack', 'plug in last, after everything else is wired'),
        ('w12', 'DC jack +', 'Fuse holder, in', '3 A glass fuse, 5 x 20'),
        ('w12', 'Fuse holder, out', 'Rocker switch, pin 1', ''),
        ('w12', 'Rocker switch, pin 2', '12 V Wago', ''),
        ('gnd', 'DC jack -', 'GND Wago', 'black'),
        ('w12', '12 V Wago', 'CNC shield + (12-36 V terminal)', 'tighten the screw terminal hard, pull-test the wire'),
        ('gnd', 'GND Wago', 'CNC shield -', ''),
        ('w12', '12 V Wago', 'LM2596 IN+', '22 AWG is enough from here'),
        ('gnd', 'GND Wago', 'LM2596 IN-', ''),
    ]),
    ('5 V rail, 22 AWG', [
        ('w5', 'LM2596 OUT+', '5 V Wago', 'turn the screw to 5.0 V with nothing on the output first'),
        ('gnd', 'LM2596 OUT-', 'GND Wago', ''),
        ('w5', '5 V Wago', 'LED card VCC', ''),
        ('gnd', 'GND Wago', 'LED card GND', ''),
        ('w5', '5 V Wago', 'LED ring 5V', '1000 uF 16 V across ring 5V and GND, stripe leg to GND'),
        ('gnd', 'GND Wago', 'LED ring GND', ''),
        ('w5', '5 V Wago', 'X and Y endstop VCC', 'the shield limit headers only have S and GND'),
        ('w5', '5 V Wago', '74HCT125 pin 14 (VCC)', 'also pins 4, 10, 13 to 5 V (unused channels off)'),
        ('gnd', 'GND Wago', '74HCT125 pin 7 (GND) and pin 1 (1OE)', 'also pins 5, 9, 12 to GND (unused inputs)'),
    ]),
    ('Signals, jumper wires', [
        ('sig', 'Pi pin 19 (GPIO10, SPI MOSI)', '74HCT125 pin 2 (1A)', 'M-F jumper'),
        ('gnd', 'Pi pin 20 (GND)', 'GND Wago', 'the ring data needs a shared ground'),
        ('sig', '74HCT125 pin 3 (1Y)', '470 ohm, then ring DIN', 'put the resistor at the ring end'),
        ('sig', 'Shield CoolEn (A3), S pin', 'LED card SIG', 'GRBL M8 turns it on, M9 off'),
        ('sig', 'X endstop OUT', 'Shield X- S pin (D9)', 'endstop GND to the X- GND pin next to it'),
        ('sig', 'Y endstop OUT', 'Shield Y- S pin (D10)', 'endstop GND to the Y- GND pin'),
    ]),
    ('Motors', [
        ('mot', 'NEMA17 X (Dupont cable)', 'Shield X header 2B 2A 1A 1B', 'one coil pair on 1A 1B, the other on 2A 2B; a pair reads about 1.8 ohm'),
        ('mot', 'NEMA17 Y', 'Shield Y header', 'same; if an axis runs backwards flip one pair or set $3'),
        ('mot', '28BYJ-48 (after the mod)', 'Shield Z header', 'orange + pink on 1A 1B, yellow + blue on 2A 2B, red not connected'),
    ]),
    ('Pi, camera, laptop', [
        ('data', 'Pi USB-A', 'Uno USB-B', 'cable comes with the Uno; also powers the Uno and shield logic'),
        ('data', 'Pi CSI (between HDMI and audio)', 'HQ camera', '50 cm FFC; silver contacts face the HDMI port. Copy the camera end from the 200 mm cable'),
        ('w5', 'Pi PSU 5.1 V 2.5 A', 'Pi micro USB', 'its own supply, not the buck'),
        ('data', 'Pi Ethernet', 'Laptop', 'Cat6 1 m, or the Pi 5 GHz Wi-Fi'),
        ('data', 'Overview USB camera', 'Pi USB-A', 'step 10, later'),
    ]),
]
n = 0
rows = []
for grp, items in W:
    rows.append(f'<tr class="grp"><th colspan="4" scope="colgroup">{E(grp)}</th></tr>')
    for cls, a, b, note in items:
        n += 1
        rows.append(f'<tr><td class="num">{n}</td><td><span class="sw {cls}"></span>{E(a)}</td><td>{E(b)}</td>'
                    f'<td class="note">{E(note)}</td></tr>')
WIRES = '\n'.join(rows)

# ---------------- grbl settings, numbers from the model
xy_steps = P['steps_rev'] * P['microsteps'] / P['lead']
z_steps = round(4076 / P['m4_pitch'])
vmax = P['vmax'] * 60
GRBL = [
    ('$0', '10', 'step pulse, us'), ('$1', '25', 'step idle delay, ms'), ('$2', '0', 'step pulse invert'),
    ('$3', '0', 'direction invert mask; flip a bit if an axis jogs the wrong way'), ('$4', '0', 'enable invert'),
    ('$5', '0', 'limit pins invert; set 1 if Pn shows X or Y with the fork empty'), ('$6', '0', 'probe invert'),
    ('$10', '1', 'report machine position'), ('$11', '0.010', 'junction deviation, mm'), ('$12', '0.002', 'arc tolerance, mm'),
    ('$13', '0', 'report in mm'),
    ('$20', '0', 'soft limits off: no Z switch, the Pi keeps moves inside the travel'),
    ('$21', '1', 'hard limits on X- and Y-'), ('$22', '1', 'homing on'), ('$23', '3', 'home X and Y toward minus'),
    ('$24', '50', 'homing feed, mm/min'), ('$25', '600', 'homing seek, mm/min'), ('$26', '250', 'homing debounce, ms'),
    ('$27', '1.000', 'homing pull-off, mm'),
    ('$30', '1000', 'spindle max (unused)'), ('$31', '0', 'spindle min (unused)'), ('$32', '0', 'laser mode off'),
    ('$100', f'{xy_steps:.0f}', f'X steps/mm: 200 x 16 / {P["lead"]:.0f} mm lead'),
    ('$101', f'{xy_steps:.0f}', 'Y steps/mm'),
    ('$102', f'{z_steps}', f'Z steps/mm: 4076 half-steps per rev / {P["m4_pitch"]} mm (1:1 gears)'),
    ('$110', f'{vmax:.0f}', f'X max rate, mm/min ({P["vmax"]:.0f} mm/s)'), ('$111', f'{vmax:.0f}', 'Y max rate, mm/min'),
    ('$112', '10', 'Z max rate, mm/min (about 14 rpm on the 28BYJ)'),
    ('$120', f'{P["accel"]:.0f}', 'X accel, mm/s2'), ('$121', f'{P["accel"]:.0f}', 'Y accel, mm/s2'), ('$122', '5', 'Z accel, mm/s2'),
    ('$130', f'{P["x_travel"][1] - P["x_travel"][0]:.0f}', 'X travel, mm'), ('$131', f'{P["y_travel"][1] - P["y_travel"][0]:.0f}', 'Y travel, mm'),
    ('$132', f'{P["z_travel"][1] - P["z_travel"][0]:.0f}', 'Z travel, mm'),
]
GRBL_TXT = '\n'.join(f'{k}={v}' for k, v, _ in GRBL)
_r = [f'<tr><td class="k">{k}</td><td class="v">{v}</td><td class="note">{E(d)}</td></tr>' for k, v, d in GRBL]
GRBL_ROWS = '\n'.join(_r[:17])
GRBL_ROWS2 = '\n'.join(_r[17:])

# ---------------- shopping status for the wiring parts
keys = ['adapter', 'dcjack', 'fuse', 'switch', 'wago', 'wiring', 'buck', 'shifter', 'jumper', 'camcable', 'psu', 'sd', 'eth']
by = {r['key']: r for r in S.rows()}
PARTS = '\n'.join(
    f'<li><span class="st st-{by[k]["status"]}">{E(S.STATUS_TXT[by[k]["status"]])}</span>'
    f'<span class="pi">{"<a href=" + json.dumps(by[k]["url"]) + " target=_blank rel=noopener>" + E(by[k]["item"]) + "</a>" if by[k]["url"] else E(by[k]["item"])}'
    f'<small>{E(by[k]["store"])} · {by[k]["qty"]} x · {("about " if by[k]["status"] == "later" else "") + format(round(by[k]["total"]), ",") + " TL" if by[k]["total"] else "price ?"}</small></span></li>'
    for k in keys)

page = open(ROOT / 'tools' / 'pages' / 'wiring_template.html', encoding='utf-8').read()
for k, v in {'__SVG__': SVG, '__WIRES__': WIRES, '__GRBL_ROWS__': GRBL_ROWS, '__GRBL_ROWS2__': GRBL_ROWS2, '__GRBL_TXT__': E(GRBL_TXT),
             '__PARTS__': PARTS, '__NWIRES__': str(n), '__ZSTEPS__': str(z_steps)}.items():
    page = page.replace(k, v)
open(ROOT / 'build' / 'argus-wiring.html', 'w', encoding='utf-8').write(page)
print('ok', n, 'wires', len(page) // 1024, 'KB')
