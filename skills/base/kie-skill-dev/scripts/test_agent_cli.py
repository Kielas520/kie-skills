import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import agent_cli


class IsolationAgent(agent_cli.Agent):
    name = "isolation-check"

    def __init__(self, checks: str, config: Path):
        super().__init__()
        self.checks = checks
        self.config = config

    def protected_files(self) -> list[Path]:
        return [self.config]

    def command(self, work: Path, cap: int, tools: str, auto_approve: bool) -> str:
        return shlex.join([sys.executable, "-c", self.checks])


class TaskSandboxIsolationTests(unittest.TestCase):
    def test_trigger_and_quality_namespaces(self) -> None:
        for layout in ("coop-trigger", "coop-quality/case-1/with_skill"):
            with self.subTest(layout=layout):
                self.exercise_namespace(layout)

    def exercise_namespace(self, layout: str) -> None:
        agent_cli.SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)
        base = Path(tempfile.mkdtemp(prefix="isolation-check-", dir=agent_cli.SANDBOX_ROOT))
        try:
            workspace = base / "workspace"
            task = workspace / "sample-task with spaces"
            repo = task / "repo"
            sandbox_root = task / ".tmp" / "test"
            arm = sandbox_root / layout
            work = arm / "work"
            work.mkdir(parents=True)
            home = base / "home"
            home.mkdir()
            config = home / "settings.json"
            config.write_text("original", encoding="utf-8")
            visible = [work / "input.txt", arm / "skills" / "SKILL.md"]
            hidden = [
                repo / "source.txt",
                task / "firmware" / "source.txt",
                task / "design.md",
                task / ".tmp" / "docs-tmp" / "notes.md",
                task / ".tmp" / "parameters.json",
                sandbox_root / "other-run" / "secret.txt",
                sandbox_root / "result.json",
                workspace / "other-task" / "secret.txt",
                workspace / "notes.md",
            ]
            if "with_skill" in layout:
                hidden.extend([
                    arm.parent / "without_skill" / "work" / "secret.txt",
                    arm.parent.parent / "case-2" / "with_skill" / "work" / "secret.txt",
                    arm.parent / "case.json",
                ])
            for path in visible + hidden:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("visible" if path in visible else "secret", encoding="utf-8")
            checks = (
                "from pathlib import Path; import os; "
                f"assert os.getuid() == {os.getuid()}; "
                f"assert Path.cwd() == Path({str(work)!r}); "
                f"visible = {json.dumps([str(p) for p in visible])}; "
                f"hidden = {json.dumps([str(p) for p in hidden])}; "
                "assert all(Path(p).read_text() == 'visible' for p in visible); "
                "assert all(not Path(p).exists() or Path(p).read_text() == '' for p in hidden); "
                f"config = Path({str(config)!r}); "
                "assert config.read_text() == 'original'; config.write_text('sandbox'); "
                "Path('output.txt').write_text('completed'); print('namespace isolation passed')"
            )
            with patch.multiple(agent_cli, REPO=repo, TASK_ROOT=task,
                                SANDBOX_ROOT=sandbox_root, HOME=home):
                command = IsolationAgent(checks, config).run("", work, 30, "", False)
                result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((work / "output.txt").read_text(), "completed")
            self.assertEqual(config.read_text(), "original")
            self.assertEqual((arm / "protected" / "settings.json").read_text(), "sandbox")
            for path in hidden:
                self.assertEqual(path.read_text(), "secret")
            print(f"{layout}: {result.stdout.strip()}")
        finally:
            subprocess.run(["gio", "trash", str(base)], check=True)

    def test_outside_work_directory_is_rejected(self) -> None:
        with self.assertRaises(agent_cli.HarnessError):
            agent_cli.test_workspace_masks(agent_cli.REPO)


if __name__ == "__main__":
    unittest.main()
