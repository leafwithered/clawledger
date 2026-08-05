import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "clawledger"


class PluginBundleTests(unittest.TestCase):
    def test_skill_only_manifest_is_protocol_shaped(self) -> None:
        manifest = tomllib.loads((PLUGIN / "manifest.toml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "clawledger")
        self.assertEqual(manifest["version"], "0.1.3")
        self.assertEqual(manifest["capabilities"], ["skill"])
        self.assertEqual(manifest["permissions"], [])
        self.assertNotIn("wasm_path", manifest)

    def test_skill_bundle_contains_required_frontmatter_and_wrapper(self) -> None:
        skill = (PLUGIN / "skills" / "clawledger" / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        self.assertIn("name: clawledger", skill)
        self.assertIn("description:", skill)
        self.assertTrue((PLUGIN / "skills" / "clawledger" / "scripts" / "clawledger_cli.py").is_file())


if __name__ == "__main__":
    unittest.main()
