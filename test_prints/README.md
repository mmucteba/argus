# Test prints

Small prints that check the printer and the real parts before the big parts are printed. They are not part of the machine, so they are not in the assembly checks; each one only has to be one valid solid, fit the bed and print without supports.

A file here has `META = dict(name=..., orient='zmin', note=...)` and `build()` returning a solid at the origin. `python tools/check.py <file name>` checks one; `tools/build.py --files` puts them in the print pack under `test_prints/`.
