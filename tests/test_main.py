import pytest
from click.testing import CliRunner
from src.main import cli


def test_cli_missing_input():
    runner = CliRunner()
    result = runner.invoke(cli, ["nonexistent.txt"])
    assert result.exit_code != 0


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Generate subtitle video" in result.output
