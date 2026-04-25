# Bootstrap Entry Points

This directory contains the single-repo entrypoints for the bundled AIPD
distribution.

Current stage:

- `install.sh` checks the local prerequisites and builds the bundled Symphony runtime
- `init_project.sh` initializes an external `PROJECT_ROOT` from the bundled templates
- `render_workflow.py` renders an AIPD-compatible Symphony workflow file for one project
- `run_symphony.sh` starts the bundled Symphony runtime against one external `PROJECT_ROOT`

These scripts do not yet implement the full AIPD bridge. They are stage-one
distribution entrypoints so the repository can move toward one-download setup.
