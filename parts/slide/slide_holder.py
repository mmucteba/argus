# slide holder: pocket for a 75 x 25 slide, levelled on 3 sprung screws
from argus.geo import *
from argus.spec import P, pat

META = dict(name='Slide holder', group='Y', layer=4, sub='Slide holder', step=7, color='holder', orient='zmin',
            note='76 x 26 x 1.2 mm pocket, open window 52 x 22 mm under the tissue area, finger notch at the front. '
                 'Print at 0.12 mm layers for flat datum edges. Gravity holds the slide: 0.5 m/s2 x 5 g is far below friction.',
            hw={'M3x16 screw': 3, 'Spring 5x10 (levelling)': 3})


def build():
    h0, h1 = P['holder_z']
    hold = box(-46, 46, -21, 21, h0, h1)
    return cut(hold, box(-38, 38, -13, 13, P['z_slide_bot'], h1 + 0.1), box(-26, 26, -11, 11, h0 - 0.1, h1 + 0.1),
               box(-7, 7, -21.1, -12, P['z_slide_bot'] - 0.8, h1 + 0.1),
               *[bolt_v(x, y, h1, h0, cb_depth=3.2) for x, y in pat('levelling')])
