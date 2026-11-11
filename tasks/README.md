# Task files

Each `.md` here becomes a GitHub issue automatically when it lands on `main` (workflow `open-tasks`); a file whose title already has an issue is skipped.

Make a design task:
```
python tools/task.py <part> --goal "..." --inputs "..." --who "Fable (hard geometry)" --out tasks/<part>.md
```
`--who` is one of: `Fable (hard geometry)`, `Any strong AI`, `Anyone, small change`. Add `--also <file>` when the task may change a second file, like the module's `bought.py`.
