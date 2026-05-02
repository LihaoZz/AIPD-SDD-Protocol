# DeepSeek Adapter Spec

## Scope

This adapter implements the same minimal stdio JSON-RPC loop as the MiniMax
adapter for the subset of Codex app-server methods used by the bundled
Symphony runtime:

- `initialize`
- `initialized`
- `thread/start`
- `turn/start`
- `turn/completed`
- `turn/failed`
- `codex/event/agent_message_content_delta`

## Backend

The backend is the local DeepSeek launcher:

- default path: `~/.claude/providers/launchers/claude-deepseek`
- overridable by `DEEPSEEK_CLAUDE_LAUNCHER`

## Failure Rules

- Missing launcher: fail closed
- Unsupported approval policy: fail closed
- Non-zero launcher exit: emit `turn/failed`
- Malformed launcher output: fall back to raw stdout text where possible

