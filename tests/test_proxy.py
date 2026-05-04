from __future__ import annotations

import importlib.util
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROXY = ROOT / "bin/zed-codex-skills-acp"


def load_proxy():
    loader = SourceFileLoader("zed_codex_skills_acp", str(PROXY))
    spec = importlib.util.spec_from_loader("zed_codex_skills_acp", loader)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ProxyTests(unittest.TestCase):
    def test_command_name_normalizes_text(self):
        proxy = load_proxy()
        self.assertEqual(
            proxy.command_name("Main API Domain Development!"),
            "Main-API-Domain-Development",
        )
        self.assertEqual(proxy.command_name("/review"), "review")

    def test_parse_frontmatter_reads_name_description(self):
        proxy = load_proxy()
        metadata = proxy.parse_frontmatter("---\nname: demo\ndescription: Demo skill\n---\n# Body")
        self.assertEqual(metadata, {"name": "demo", "description": "Demo skill"})

    def test_merge_available_commands_preserves_existing(self):
        proxy = load_proxy()
        proxy.skill_commands = lambda: [
            {"name": "demo-skill", "description": "Demo", "input": {"hint": "<task>"}}
        ]
        message = {
            "params": {
                "update": {
                    "sessionUpdate": "available_commands_update",
                    "availableCommands": [{"name": "review", "description": "Review"}],
                }
            }
        }
        merged = proxy.merge_available_commands(message)
        names = [command["name"] for command in merged["params"]["update"]["availableCommands"]]
        self.assertEqual(names, ["review", "demo-skill"])


if __name__ == "__main__":
    unittest.main()
