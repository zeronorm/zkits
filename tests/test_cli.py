from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from zkit import check_env
from zkit.cli import main


class CliTests(unittest.TestCase):
    def test_check_env_returns_runtime_info(self) -> None:
        info = check_env()

        self.assertTrue(info["python_version"])
        self.assertTrue(info["python_executable"])
        self.assertTrue(info["platform"])
        self.assertTrue(info["implementation"])
        self.assertTrue(info["cwd"])

    def test_check_env_command_prints_json(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main(["check_env", "--json"])

        self.assertEqual(exit_code, 0)
        parsed = json.loads(output.getvalue())
        self.assertTrue(parsed["python_version"])
        self.assertTrue(parsed["platform"])


if __name__ == "__main__":
    unittest.main()
