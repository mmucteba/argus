# Instructions for AI agents

Read CONTEXT.md before doing anything. Short version:
- one design task = one part file in parts/<module>/; change nothing else unless the task lists it
- read every shared number from argus.spec (P, pat) and every real-world size from F (spec/facts.yaml); never type them in
- if your part is provisional (uses unverified facts), verify those facts first: measure or datasheet, proof in evidence/
- stay inside the envelope in spec/contracts.yaml and keep every hole listed for your part in spec/interfaces.yaml
- need a shared change: write a change request, do not edit spec/, argus/, checks/ or another part
- run `python tools/check.py <part>` then `python tools/check.py`; all must pass
- code comments are short, lowercase, no punctuation
