# MiniMax Adapter Spec

## Scope

This adapter implements a minimal stdio JSON-RPC loop compatible with the
subset of Codex app-server methods used by the bundled Symphony runtime:

- `initialize`
- `initialized`
- `thread/start`
- `turn/start`
- `turn/completed`
- `turn/failed`
- `codex/event/agent_message_content_delta`

## Backend

The backend is the local Claude MiniMax launcher:

- default path: `~/.claude/providers/launchers/claude-minimax`
- overridable by `MINIMAX_CLAUDE_LAUNCHER`

## Failure Rules

- Missing launcher: fail closed
- Unsupported approval policy: fail closed
- Non-zero launcher exit: emit `turn/failed`
- Malformed launcher output: fall back to raw stdout text where possible

