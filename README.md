# zed-codex-skills-acp

Expose local Codex and agent skills as slash commands in Zed's Codex ACP UI.

Zed talks to external agents over ACP. The current `codex-acp` adapter handles Codex in Zed, but it only advertises its built-in slash commands to the Zed composer. This wrapper sits between Zed and `codex-acp`, adds your local skills to the slash-command list, and rewrites `/skill-name ...` into a normal Codex prompt that asks Codex to use that skill.

```text
Zed -> zed-codex-skills-acp -> codex-acp -> Codex
```

## What It Does

- Scans local skill folders at runtime:
  - `~/.codex/skills`
  - `~/.agents/skills`
  - `~/.claude/skills`
  - workspace `.agents/skills`, `.codex/skills`, and `.claude/skills`
  - Codex plugin cache skill folders
- Adds discovered skills to Zed's slash picker for the custom agent.
- Rewrites prompts like `/architecture-reviewer review this spec` into:

```text
Use the local skill named `architecture-reviewer` from `/path/to/SKILL.md` for this task.

Task: review this spec
```

Everything else is forwarded to the real `codex-acp` process unchanged.

## Install

Clone this repo:

```sh
git clone https://github.com/MangKong-coder/zed-codex-skills-acp.git
cd zed-codex-skills-acp
chmod +x bin/zed-codex-skills-acp scripts/zed-codex-skills-acp-install
```

Print the Zed settings snippet:

```sh
scripts/zed-codex-skills-acp-install
```

Add the printed block to your Zed `settings.json`. It will look like this:

```json
{
  "agent_servers": {
    "Codex Skills": {
      "type": "custom",
      "command": "/usr/bin/python3",
      "args": ["/absolute/path/to/zed-codex-skills-acp/bin/zed-codex-skills-acp"],
      "env": {}
    }
  }
}
```

Then open Zed's Agent Panel and start a new thread with `Codex Skills`.

## Configuration

If the wrapper cannot find `codex-acp`, set `REAL_CODEX_ACP`:

```json
{
  "agent_servers": {
    "Codex Skills": {
      "type": "custom",
      "command": "/usr/bin/python3",
      "args": ["/absolute/path/to/zed-codex-skills-acp/bin/zed-codex-skills-acp"],
      "env": {
        "REAL_CODEX_ACP": "/absolute/path/to/codex-acp"
      }
    }
  }
}
```

To scan extra workspace roots, set `CODEX_SKILLS_EXTRA_ROOTS` as a colon-separated list:

```json
{
  "env": {
    "CODEX_SKILLS_EXTRA_ROOTS": "/path/to/project-a:/path/to/project-b"
  }
}
```

Logs are written to `~/.cache/zed-codex-skills-acp/proxy.log` by default. Override that with `ZED_CODEX_SKILLS_ACP_LOG`.

## Notes

- This is a local compatibility wrapper, not an official Zed or OpenAI project.
- It does not modify Codex behavior beyond expanding selected slash commands before the real `codex-acp` sees them.
- Already-open Zed agent threads keep their existing ACP process. Start a new `Codex Skills` thread after changing settings.

## Development

Run the small test suite:

```sh
python3 -m unittest discover -s tests
```

## Sync Existing MCP Servers Into Zed

Zed does not automatically read MCP servers from Codex or Claude config files. This repo includes a sync command that mirrors compatible local MCP server entries into Zed's `context_servers`.

Preview the import:

```sh
scripts/sync-zed-mcp --dry-run
```

Apply it:

```sh
scripts/sync-zed-mcp
```

By default this reads `~/.codex/config.toml` and writes `~/.config/zed/settings.json`, creating a `.bak` backup beside the Zed settings file first.

You can also import Claude-style `.mcp.json` files:

```sh
scripts/sync-zed-mcp --mcp-json /path/to/.mcp.json
```

Supported server shapes:

- stdio servers with `command`, optional `args`, and optional `env`
- HTTP servers with `url`, optional `headers`, and optional `timeout`

Unsupported fields are ignored rather than guessed.
