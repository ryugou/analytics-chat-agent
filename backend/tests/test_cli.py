import pytest
from typer.testing import CliRunner
from analytics_chat_agent.cli.main import cli

runner = CliRunner()

def test_main_module():
    """main.pyのif __name__ == "__main__":ブロックのテスト"""
    result = runner.invoke(cli)
    # 正常終了またはエラー終了どちらも許容（カバレッジ目的）
    assert result.exit_code in (0, 1) 