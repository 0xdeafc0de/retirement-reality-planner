# Contributing

Thanks for helping improve Retirement Reality Planner. The project is still
early, so small, focused changes are easiest to review and merge.

## Local Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/pytest -q
```

## Development Guidelines

- Keep changes incremental and focused.
- Add or update tests when behavior changes.
- Update `README.md` when a command, option, output, or user-facing behavior
  changes.
- Prefer clear financial assumptions over hidden defaults.
- Treat example datasets as examples, not financial advice.

## Pull Requests

Before opening a pull request, run:

```bash
.venv/bin/pytest -q
```

Include a short summary of what changed and any modeling assumptions that matter
for users.

## Financial Disclaimer

This project is for education and planning exploration. It is not investment,
tax, legal, or retirement advice.

