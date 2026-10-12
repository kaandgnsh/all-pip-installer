import importlib.util
import io
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "all-pip-installer"
    / "all-pip.py"
)
SPEC = importlib.util.spec_from_file_location("all_pip_installer", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load the installer module.")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class SelectPackagesTests(unittest.TestCase):
    def test_default_profile_is_curated(self):
        packages = installer.select_packages("basic")
        self.assertEqual(packages, ("requests", "colorama", "rich"))

    def test_additional_packages_are_deduplicated(self):
        packages = installer.select_packages("basic", ("pytest", "requests"))
        self.assertEqual(packages, ("requests", "colorama", "rich", "pytest"))

    def test_invalid_package_name_is_rejected(self):
        with self.assertRaises(ValueError):
            installer.select_packages("basic", ("requests; print('bad')",))

    def test_unknown_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            installer.select_packages("unknown")


class CliTests(unittest.TestCase):
    def test_default_run_is_dry_run(self):
        output = io.StringIO()
        result = installer.main([], run=self.fail, output=output)
        self.assertEqual(result, 0)
        self.assertIn("Dry run only", output.getvalue())
        self.assertIn("Selected packages", output.getvalue())

    def test_list_profiles_does_not_install(self):
        output = io.StringIO()
        result = installer.main(["--list"], run=self.fail, output=output)
        self.assertEqual(result, 0)
        self.assertIn("scraping", output.getvalue())
        self.assertIn("beautifulsoup4", output.getvalue())

    def test_install_requires_confirmation(self):
        output = io.StringIO()
        calls = []

        def fake_run(command, check):
            calls.append((command, check))
            return subprocess.CompletedProcess(command, 0)

        result = installer.main(
            ["--profile", "web", "--install"],
            run=fake_run,
            input_fn=lambda _prompt: "y",
            output=output,
        )
        self.assertEqual(result, 0)
        self.assertEqual(len(calls), 1)
        command, check = calls[0]
        self.assertEqual(command[:3], [sys.executable, "-m", "pip"])
        self.assertEqual(command[3:5], ["install", "requests"])
        self.assertIn("beautifulsoup4", command)
        self.assertFalse(check)

    def test_declining_confirmation_skips_install(self):
        output = io.StringIO()
        result = installer.main(
            ["--install"],
            run=self.fail,
            input_fn=lambda _prompt: "n",
            output=output,
        )
        self.assertEqual(result, 0)
        self.assertIn("cancelled", output.getvalue().lower())

    def test_yes_requires_install_flag(self):
        with self.assertRaises(SystemExit) as raised:
            installer.main(["--yes"], output=io.StringIO())
        self.assertEqual(raised.exception.code, 2)

    def test_invalid_extra_package_is_rejected_by_cli(self):
        with self.assertRaises(SystemExit) as raised:
            installer.main(
                ["--package", "package;echo-no", "--install"],
                output=io.StringIO(),
            )
        self.assertEqual(raised.exception.code, 2)

    def test_pip_failure_code_is_returned(self):
        output = io.StringIO()

        def fake_run(command, check):
            return subprocess.CompletedProcess(command, 2)

        result = installer.main(
            ["--install", "--yes"],
            run=fake_run,
            output=output,
        )
        self.assertEqual(result, 2)
        self.assertIn("status 2", output.getvalue())


if __name__ == "__main__":
    unittest.main()
