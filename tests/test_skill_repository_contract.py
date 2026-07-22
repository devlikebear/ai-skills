import unittest
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ANALYZER_ROOT = REPO_ROOT / "codex" / "skills" / "source-analyzer"
SKILL_GENERATOR_ROOT = REPO_ROOT / ".codex" / "skills" / "skill-generator"
PUBLIC_SKILLS_ROOT = REPO_ROOT / "codex" / "skills"
CLAUDE_CODE_PLUGIN_ROOT = REPO_ROOT / "claude-code" / "plugin"
MARKETPLACE_ROOT = REPO_ROOT / ".claude-plugin"
CODEX_PLUGIN_MARKETPLACE_ROOT = REPO_ROOT / ".agents" / "plugins"
CODEX_PLUGIN_ROOT = REPO_ROOT / "plugins" / "source-analyzer-tools"
CODEX_WORKFLOW_PLUGIN_ROOT = REPO_ROOT / "plugins" / "code-workflow"
SOURCE_ANALYZER_MCP_ROOT = REPO_ROOT / "servers" / "source-analyzer-mcp"
EXPECTED_PUBLIC_SKILLS = {
    "source-analyzer",
    "implement",
    "plan-for-codex",
    "refactor",
    "review",
    "github-flow",
}
EXPECTED_PLUGIN_SKILLS = {
    "source-analyzer",
    "implement",
    "plan",
    "refactor",
    "review",
    "github-flow",
}


class SkillRepositoryContractTests(unittest.TestCase):
    def test_all_skill_frontmatter_descriptions_are_quoted(self):
        for skill_path in REPO_ROOT.glob("**/SKILL.md"):
            content = skill_path.read_text(encoding="utf-8")
            frontmatter = content.split("---", 2)[1]
            self.assertRegex(
                frontmatter,
                re.compile(r'^description:\s+".+"$', re.MULTILINE),
                msg=f"description must be quoted in {skill_path}",
            )

    def test_public_skills_have_flat_structure(self):
        actual = {path.name for path in PUBLIC_SKILLS_ROOT.iterdir() if path.is_dir()}
        self.assertTrue(EXPECTED_PUBLIC_SKILLS.issubset(actual))

        for skill_name in EXPECTED_PUBLIC_SKILLS:
            root = PUBLIC_SKILLS_ROOT / skill_name
            self.assertTrue((root / "SKILL.md").exists(), msg=f"missing SKILL.md for {skill_name}")
            self.assertTrue((root / "agents" / "openai.yaml").exists(), msg=f"missing agents/openai.yaml for {skill_name}")
            self.assertTrue((root / "shared").is_dir(), msg=f"missing shared dir for {skill_name}")
            self.assertFalse((root / "ko").exists(), msg=f"{skill_name} should not have ko/ directory")
            self.assertFalse((root / "en").exists(), msg=f"{skill_name} should not have en/ directory")

    def test_source_analyzer_has_checkpoint_script(self):
        self.assertTrue((SOURCE_ANALYZER_ROOT / "shared" / "scripts" / "checkpoint_manager.py").exists())

    def test_public_skills_language_policy_is_auto_detect(self):
        for skill_name in EXPECTED_PUBLIC_SKILLS:
            content = (PUBLIC_SKILLS_ROOT / skill_name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(
                "Respond in the same language the user writes in.",
                content,
                msg=f"{skill_name} SKILL.md should use auto-detect language policy",
            )

    def test_codex_source_analyzer_skill_documents_cli_and_mcp_search(self):
        content = (SOURCE_ANALYZER_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Search CLI", content)
        self.assertIn('python3 "$CHECKPOINT_SCRIPT" search "query text" --top-k 5', content)
        self.assertIn('python3 "$CHECKPOINT_SCRIPT" get-module server-chat-pipeline', content)
        self.assertIn("## Search MCP integration", content)
        self.assertIn("analysis.search", content)
        self.assertIn("If none of these files exist, create `AGENTS.md`", content)

    def test_skill_generator_wrapper_exists_in_dot_codex(self):
        self.assertTrue((SKILL_GENERATOR_ROOT / "SKILL.md").exists())
        self.assertTrue((SKILL_GENERATOR_ROOT / "agents" / "openai.yaml").exists())
        self.assertFalse((SKILL_GENERATOR_ROOT / "ko").exists())
        self.assertFalse((SKILL_GENERATOR_ROOT / "en").exists())
        root_skill = (SKILL_GENERATOR_ROOT / "SKILL.md").read_text(encoding="utf-8")
        root_agent = (SKILL_GENERATOR_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("skill-creator", root_skill)
        self.assertIn("wrapper", root_skill.lower())
        self.assertIn("Respond in the same language the user writes in.", root_skill)
        self.assertIn('display_name: "Skill Generator"', root_agent)

    def test_public_repo_readme_mentions_codex_skills_and_installer(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("AI Skills Repository", readme)
        self.assertIn("codex/skills/source-analyzer", readme)
        self.assertIn("codex/skills/implement", readme)
        self.assertIn("codex/skills/plan-for-codex", readme)
        self.assertIn("codex/skills/refactor", readme)
        self.assertIn("codex/skills/review", readme)
        self.assertIn(".codex/skills/skill-generator", readme)
        self.assertIn("scripts/install_codex_skill.sh", readme)

    def test_public_repo_readme_mentions_claude_code_plugin(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("code-workflow", readme)
        self.assertIn("/plugin marketplace add", readme)
        self.assertIn("/plugin install", readme)

    def test_public_repo_readme_matches_current_release_and_flat_layout(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        version = (REPO_ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()

        self.assertIn(f"Current release: `{version}`", readme)
        self.assertNotIn("skill-generator/\n      README.md", readme)
        self.assertNotIn("ko/", readme)
        self.assertNotIn("en/", readme)
        self.assertIn("scripts/publish_wiki.sh", readme)

    def test_public_repo_readme_includes_mcp_usage_examples(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("codex mcp list", readme)
        self.assertIn("analysis.search", readme)
        self.assertIn("analysis.get_module", readme)

    # --- Plugin marketplace tests ---

    def test_plugin_manifest_exists_and_is_valid_json(self):
        manifest_path = CLAUDE_CODE_PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        self.assertTrue(manifest_path.exists(), msg="missing plugin.json")
        import json
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "code-workflow")
        self.assertIn("version", manifest)
        self.assertIn("description", manifest)

    def test_marketplace_json_exists_and_is_valid(self):
        marketplace_path = MARKETPLACE_ROOT / "marketplace.json"
        self.assertTrue(marketplace_path.exists(), msg="missing marketplace.json")
        import json
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        self.assertEqual(marketplace["name"], "ai-skills")
        self.assertIn("owner", marketplace)
        self.assertIn("plugins", marketplace)
        self.assertGreater(len(marketplace["plugins"]), 0)
        plugin_entry = marketplace["plugins"][0]
        self.assertEqual(plugin_entry["name"], "code-workflow")
        self.assertIn("source", plugin_entry)

    def test_plugin_skills_exist(self):
        skills_root = CLAUDE_CODE_PLUGIN_ROOT / "skills"
        actual = {path.name for path in skills_root.iterdir() if path.is_dir()}
        self.assertTrue(EXPECTED_PLUGIN_SKILLS.issubset(actual))
        for skill_name in EXPECTED_PLUGIN_SKILLS:
            skill_md = skills_root / skill_name / "SKILL.md"
            self.assertTrue(skill_md.exists(), msg=f"missing SKILL.md for plugin skill {skill_name}")

    def test_plugin_skills_are_bilingual(self):
        skills_root = CLAUDE_CODE_PLUGIN_ROOT / "skills"
        for skill_name in EXPECTED_PLUGIN_SKILLS:
            content = (skills_root / skill_name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(
                "Detect the user's language",
                content,
                msg=f"plugin skill {skill_name} should have bilingual language policy",
            )

    def test_plugin_skills_do_not_reference_codex_home(self):
        for skill_path in CLAUDE_CODE_PLUGIN_ROOT.glob("**/SKILL.md"):
            content = skill_path.read_text(encoding="utf-8")
            self.assertNotIn(
                "CODEX_HOME",
                content,
                msg=f"plugin skill {skill_path} should not reference CODEX_HOME",
            )

    def test_github_flow_requires_explicit_invocation_on_both_platforms(self):
        codex_agent = (
            PUBLIC_SKILLS_ROOT / "github-flow" / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")
        claude_skill = (
            CLAUDE_CODE_PLUGIN_ROOT / "skills" / "github-flow" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("allow_implicit_invocation: false", codex_agent)
        self.assertRegex(
            claude_skill,
            re.compile(r"^disable-model-invocation:\s*true$", re.MULTILINE),
        )

    def test_github_flow_checks_worktree_before_checkout_or_pull(self):
        skill_paths = [
            PUBLIC_SKILLS_ROOT / "github-flow" / "SKILL.md",
            CLAUDE_CODE_PLUGIN_ROOT / "skills" / "github-flow" / "SKILL.md",
        ]

        for skill_path in skill_paths:
            content = skill_path.read_text(encoding="utf-8")
            status_position = content.find("git status --short --branch")
            checkout_position = content.find("git checkout")
            pull_position = content.find("git pull")

            self.assertGreaterEqual(
                status_position,
                0,
                msg=f"missing worktree preflight in {skill_path}",
            )
            self.assertTrue(
                checkout_position < 0 or status_position < checkout_position,
                msg=f"git status must precede checkout in {skill_path}",
            )
            self.assertTrue(
                pull_position < 0 or status_position < pull_position,
                msg=f"git status must precede pull in {skill_path}",
            )

    def test_plugin_references_directory_exists(self):
        refs_dir = CLAUDE_CODE_PLUGIN_ROOT / "references"
        self.assertTrue(refs_dir.is_dir(), msg="missing references directory in plugin")
        expected_refs = [
            "work-order.md",
            "refactor-work-order.md",
            "review-checklist.md",
            "refactoring-checklist.md",
            "refactoring-patterns.md",
            "checkpoint-template.md",
            "refactor-template.md",
            "tidy-first-rules.md",
            "security-triage-checklist.md",
            "tutorial-template.md",
            "github-flow-checklist.md",
        ]
        for ref in expected_refs:
            self.assertTrue((refs_dir / ref).exists(), msg=f"missing reference {ref} in plugin")

    def test_plugin_checkpoint_script_exists(self):
        self.assertTrue(
            (CLAUDE_CODE_PLUGIN_ROOT / "scripts" / "checkpoint_manager.py").exists(),
            msg="missing checkpoint_manager.py in plugin",
        )

    def test_plugin_source_analyzer_uses_claude_plugin_root(self):
        content = (CLAUDE_CODE_PLUGIN_ROOT / "skills" / "source-analyzer" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("CLAUDE_PLUGIN_ROOT", content)

    def test_claude_plugin_mcp_config_exists(self):
        self.assertTrue((CLAUDE_CODE_PLUGIN_ROOT / ".mcp.json").exists(), msg="missing .mcp.json in Claude plugin")
        import json

        config = json.loads((CLAUDE_CODE_PLUGIN_ROOT / ".mcp.json").read_text(encoding="utf-8"))
        server = config["mcpServers"]["source-analyzer-search"]
        self.assertEqual(server["command"], "bash")
        self.assertEqual(server["args"][0], "-c")
        self.assertIn("$CLAUDE_PLUGIN_ROOT/servers/source-analyzer-mcp/server.py", server["args"][1])
        self.assertIn("PATH", server.get("env", {}))

    def test_codex_plugin_marketplace_exists(self):
        marketplace_path = CODEX_PLUGIN_MARKETPLACE_ROOT / "marketplace.json"
        self.assertTrue(marketplace_path.exists(), msg="missing Codex marketplace.json")
        import json

        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        plugin_names = {item["name"] for item in marketplace["plugins"]}
        self.assertIn("source-analyzer-tools", plugin_names)

    def test_codex_plugin_bundle_exists(self):
        self.assertTrue((CODEX_PLUGIN_ROOT / ".codex-plugin" / "plugin.json").exists(), msg="missing Codex plugin manifest")
        self.assertTrue((CODEX_PLUGIN_ROOT / ".mcp.json").exists(), msg="missing Codex plugin MCP config")
        self.assertTrue((CODEX_PLUGIN_ROOT / "servers" / "source-analyzer-mcp" / "server.py").exists())

    def test_codex_workflow_plugin_manifest_and_components(self):
        import json

        manifest_path = CODEX_WORKFLOW_PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        version = (REPO_ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()

        self.assertEqual(manifest["name"], "code-workflow")
        self.assertEqual(manifest["version"], version)
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["mcpServers"], "./.mcp.json")
        self.assertEqual(manifest["interface"]["displayName"], "Code Workflow")

        bundled_skills = {
            path.name
            for path in (CODEX_WORKFLOW_PLUGIN_ROOT / "skills").iterdir()
            if path.is_dir()
        }
        self.assertEqual(bundled_skills, EXPECTED_PUBLIC_SKILLS)
        self.assertTrue((CODEX_WORKFLOW_PLUGIN_ROOT / ".mcp.json").exists())

        analyzer_skill = (
            CODEX_WORKFLOW_PLUGIN_ROOT / "skills" / "source-analyzer" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("${PLUGIN_ROOT}/skills/source-analyzer", analyzer_skill)
        self.assertNotIn("CODEX_HOME", analyzer_skill)

        mcp_config = json.loads(
            (CODEX_WORKFLOW_PLUGIN_ROOT / ".mcp.json").read_text(encoding="utf-8")
        )
        server = mcp_config["mcpServers"]["source-analyzer-search"]
        self.assertIn("${PLUGIN_ROOT}/skills/source-analyzer", " ".join(server["args"]))

    def test_codex_workflow_plugin_is_registered_in_marketplace(self):
        import json

        marketplace = json.loads(
            (CODEX_PLUGIN_MARKETPLACE_ROOT / "marketplace.json").read_text(encoding="utf-8")
        )
        entries = {item["name"]: item for item in marketplace["plugins"]}
        entry = entries["code-workflow"]

        self.assertEqual(entry["source"]["path"], "./plugins/code-workflow")
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")

    def test_codex_workflow_plugin_skill_bundle_matches_canonical_sources(self):
        for skill_name in EXPECTED_PUBLIC_SKILLS - {"source-analyzer"}:
            canonical_root = PUBLIC_SKILLS_ROOT / skill_name
            bundled_root = CODEX_WORKFLOW_PLUGIN_ROOT / "skills" / skill_name
            canonical_files = {
                path.relative_to(canonical_root)
                for path in canonical_root.rglob("*")
                if path.is_file()
            }
            bundled_files = {
                path.relative_to(bundled_root)
                for path in bundled_root.rglob("*")
                if path.is_file()
            }

            self.assertEqual(canonical_files, bundled_files)
            for relative_path in canonical_files:
                self.assertEqual(
                    (canonical_root / relative_path).read_bytes(),
                    (bundled_root / relative_path).read_bytes(),
                    msg=f"Codex plugin skill drift: {skill_name}/{relative_path}",
                )

        canonical_analyzer = PUBLIC_SKILLS_ROOT / "source-analyzer"
        bundled_analyzer = CODEX_WORKFLOW_PLUGIN_ROOT / "skills" / "source-analyzer"
        for relative_path in [
            "agents/openai.yaml",
            "shared/scripts/checkpoint_manager.py",
            "shared/scripts/source_analyzer_search.py",
            "shared/scripts/publish_wiki.sh",
        ]:
            self.assertEqual(
                (canonical_analyzer / relative_path).read_bytes(),
                (bundled_analyzer / relative_path).read_bytes(),
                msg=f"Codex plugin analyzer drift: {relative_path}",
            )

    def test_codex_plugin_readme_includes_install_and_usage_examples(self):
        plugin_readme = (CODEX_PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("scripts/install_codex_skill.sh source-analyzer --with-mcp", plugin_readme)
        self.assertIn("codex mcp list", plugin_readme)

    def test_source_analyzer_search_script_exists(self):
        self.assertTrue(
            (SOURCE_ANALYZER_ROOT / "shared" / "scripts" / "source_analyzer_search.py").exists(),
            msg="missing source_analyzer_search.py in codex distribution",
        )

    def test_source_analyzer_mcp_sync_script_exists(self):
        self.assertTrue((REPO_ROOT / "scripts" / "sync_source_analyzer_mcp.sh").exists())

    def test_source_analyzer_search_sources_are_synced(self):
        canonical_search = (SOURCE_ANALYZER_MCP_ROOT / "source_analyzer_search.py").read_text(encoding="utf-8")
        for path in [
            SOURCE_ANALYZER_ROOT / "shared" / "scripts" / "source_analyzer_search.py",
            SOURCE_ANALYZER_ROOT / "shared" / "mcp" / "source-analyzer-mcp" / "source_analyzer_search.py",
            CLAUDE_CODE_PLUGIN_ROOT / "scripts" / "source_analyzer_search.py",
            CLAUDE_CODE_PLUGIN_ROOT / "servers" / "source-analyzer-mcp" / "source_analyzer_search.py",
            CODEX_PLUGIN_ROOT / "servers" / "source-analyzer-mcp" / "source_analyzer_search.py",
        ]:
            self.assertEqual(
                canonical_search,
                path.read_text(encoding="utf-8"),
                msg=f"search source drift detected: {path}",
            )

    def test_source_analyzer_constraints_codex_has_prefer_rg(self):
        codex_content = (SOURCE_ANALYZER_ROOT / "SKILL.md").read_text(encoding="utf-8")
        claude_content = (CLAUDE_CODE_PLUGIN_ROOT / "skills" / "source-analyzer" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Prefer `rg", codex_content, msg="Codex source-analyzer should include 'Prefer rg' in constraints")
        self.assertNotIn("Prefer `rg", claude_content, msg="Claude source-analyzer should not include 'Prefer rg' in constraints")

    def test_source_analyzer_fallback_file_codex_creates_agents_md(self):
        codex_content = (SOURCE_ANALYZER_ROOT / "SKILL.md").read_text(encoding="utf-8")
        claude_content = (CLAUDE_CODE_PLUGIN_ROOT / "skills" / "source-analyzer" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("create `AGENTS.md`", codex_content)
        self.assertIn("create `CLAUDE.md`", claude_content)

    def test_checkpoint_manager_sources_are_synced(self):
        canonical = (CLAUDE_CODE_PLUGIN_ROOT / "scripts" / "checkpoint_manager.py").read_text(encoding="utf-8")
        codex_copy = (SOURCE_ANALYZER_ROOT / "shared" / "scripts" / "checkpoint_manager.py").read_text(encoding="utf-8")
        self.assertEqual(
            canonical,
            codex_copy,
            msg="checkpoint_manager.py drift detected between Claude and Codex distributions",
        )

    def test_source_analyzer_mcp_server_sources_are_synced(self):
        canonical_server = (SOURCE_ANALYZER_MCP_ROOT / "server.py").read_text(encoding="utf-8")
        for path in [
            SOURCE_ANALYZER_ROOT / "shared" / "mcp" / "source-analyzer-mcp" / "server.py",
            CLAUDE_CODE_PLUGIN_ROOT / "servers" / "source-analyzer-mcp" / "server.py",
            CODEX_PLUGIN_ROOT / "servers" / "source-analyzer-mcp" / "server.py",
        ]:
            self.assertEqual(
                canonical_server,
                path.read_text(encoding="utf-8"),
                msg=f"server source drift detected: {path}",
            )


if __name__ == "__main__":
    unittest.main()
