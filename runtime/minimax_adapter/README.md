# MiniMax Adapter

This directory contains the MiniMax execution adapter for the AIPD-integrated
Symphony runtime.

It is intentionally separate from `runtime/symphony/`.

## Purpose

The adapter exposes a small Codex-app-server-compatible stdio protocol surface
for the AIPD Mission Block flow.

In v1 it does not call MiniMax HTTP APIs directly. Instead it wraps the local
Claude MiniMax launcher and translates launcher results into the subset of
events that the bundled Symphony runtime expects.

## Entry Point

```bash
python3 runtime/minimax_adapter/bin/minimax_app_server.py app-server
```

## Safety

- Missing launcher path fails closed.
- Non-auto approval mode fails closed.
- Secrets are not stored in this directory.

