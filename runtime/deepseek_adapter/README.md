# DeepSeek Adapter

This directory contains the DeepSeek execution adapter for the AIPD-integrated
Symphony runtime.

It is intentionally separate from both `runtime/symphony/` and
`runtime/minimax_adapter/`.

## Purpose

The adapter exposes a small Codex-app-server-compatible stdio protocol surface
for the AIPD Mission Block flow.

In v1 it wraps a local DeepSeek launcher and translates launcher results into
the subset of events that the bundled Symphony runtime expects.

## Entry Point

```bash
python3 runtime/deepseek_adapter/bin/deepseek_app_server.py app-server
```

## Safety

- Missing launcher path fails closed.
- Non-auto approval mode fails closed.
- Secrets are not stored in this directory.

