from __future__ import annotations

import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYNC = ROOT / "scripts/sync-zed-mcp"


def load_sync():
    loader = SourceFileLoader("sync_zed_mcp", str(SYNC))
    spec = spec_from_loader("sync_zed_mcp", loader)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SyncZedMcpTests(unittest.TestCase):
    def test_parse_codex_mcp_servers(self):
        sync = load_sync()
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.toml"
            config.write_text(
                """
[mcp_servers.playwright]
command = "/opt/homebrew/bin/npx"
args = ["-y", "@playwright/mcp@latest"]

[mcp_servers.context7]
url = "https://mcp.context7.com/mcp"
""",
                encoding="utf-8",
            )
            servers = sync.parse_codex_mcp_servers(config)

        self.assertEqual(servers["playwright"]["command"], "/opt/homebrew/bin/npx")
        self.assertEqual(servers["playwright"]["args"], ["-y", "@playwright/mcp@latest"])
        self.assertEqual(servers["context7"]["url"], "https://mcp.context7.com/mcp")

    def test_sync_zed_settings_preserves_existing_context_server(self):
        sync = load_sync()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            zed = root / "settings.json"
            codex = root / "config.toml"
            zed.write_text(
                '{\n  "context_servers": {\n    "codex-skills": {"command": "python3"}\n  },\n}\n',
                encoding="utf-8",
            )
            codex.write_text(
                """
[mcp_servers.trigger]
command = "/opt/homebrew/bin/npx"
args = ["trigger.dev@latest", "mcp", "--readonly"]
""",
                encoding="utf-8",
            )
            imported = sync.sync_zed_settings(zed, codex, [], "", False)
            settings = sync.parse_jsonc(zed)

        self.assertEqual(list(imported), ["trigger"])
        self.assertIn("codex-skills", settings["context_servers"])
        self.assertEqual(
            settings["context_servers"]["trigger"]["args"],
            ["trigger.dev@latest", "mcp", "--readonly"],
        )


if __name__ == "__main__":
    unittest.main()
