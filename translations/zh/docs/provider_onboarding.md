### 说明

这个中文参考尚未单独翻译完成。为避免丢失启动链与文档映射，下面保留英文权威内容供对照阅读。

### English Source

# Provider Onboarding

This document explains how a forked AIPD repo registers a new execution
provider without editing core routing logic by hand.

## Goals

- keep provider selection semantics in AIPD
- keep provider secrets and local launch details outside repo truth
- let a fork user add a provider like `glm` or `kimi`
- make the result inspectable and editable

## Entry Points

- interactive shell flow:

First go to the repo root:

```bash
cd /Users/lihaozheng/Documents/AI/Product-Dev
```

Then run:

```bash
./bootstrap/provider_onboarding.sh
```

- scripted flow:

First go to the repo root:

```bash
cd /Users/lihaozheng/Documents/AI/Product-Dev
```

Then run:

```bash
python3 scripts/register_provider.py --provider-id glm --assign-roles precision --generate-aipd-launcher
```

## Important

Only type the command itself.

Do not type the Markdown fence markers such as:

```text
```bash
...command...
```
```

## What Gets Generated

- provider registry entry in `config/provider_registry.json`
- local provider profile template under the configured local providers root
- local launcher template
- optional AIPD-mode launcher template
- runtime adapter scaffold under `runtime/<provider>_adapter/`

## Boundaries

- repo truth owns provider registry, policy, and adapter contract
- local machine owns real API keys and launcher activation
- Symphony consumes only resolved `execution_provider`
