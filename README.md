# ARGUS T18

Low-cost automated pathology slide scanner, METU EE493 capstone, team T18.

This repo is the single source of truth for the machine: every printed part as code, the shared numbers they depend on, the parts list, the wiring, and checks that prove the parts still fit together. Many people and AIs can work on different parts at the same time; the checks catch anything that breaks.

- **New here? Paste [START.md](START.md) into your AI:** it sets you up and walks you through your first task
- **Türkçe rehber, görev almak için:** [REHBER.md](REHBER.md)
- **For AI agents:** [CONTEXT.md](CONTEXT.md)
- **Why things are the way they are:** [DECISIONS.md](DECISIONS.md)
- **Open work:** the Issues tab. `design` = a printed part, `change-request` = a shared number has to change, `software` = later.

## See the current machine

**Project site: https://mmucteba.github.io/argus/** — overview, verification map, 3D viewer, parts and budget, wiring. It rebuilds itself after every push and every morning.

For the files, open the **Actions** tab, then the latest green run on `main`, and download **argus-build**. Inside:
- `argus-viewer.html`: the 3D model with every part, build steps, checks and prices
- `ARGUS_T18_print_pack_*.zip`: STL files already oriented for printing
- `ARGUS_T18_scanner_*.step`: the full assembly for any CAD program
- `ARGUS_T18_base_drilling_template_*_A3.pdf`: 1:1 template for the plywood
- `argus-parts.html`, `argus-wiring.html`: the parts and budget page and the wiring page

## Commands

```
pip install -r requirements.txt          # python 3.13
python tools/status.py                   # every printed part and what is open
python tools/check.py lens_clamp         # check one part, seconds
python tools/check.py                    # check everything, about a minute
python tools/task.py led_tower --goal "..." --inputs "..."   # prompt for a design task
python tools/build.py --files            # viewer, STEP, STL pack, drilling template into build/
```

Or open the repo in a **Codespace** (Code button, then Codespaces): Python, the libraries, Claude Code and Codex are installed for you.
