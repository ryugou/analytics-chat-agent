"""
バージョンコマンドの実装
"""

from rich.console import Console
from ... import __version__

# Richコンソールの作成
console = Console()

def version():
    """バージョン情報を表示"""
    console.print(f"Analytics Chat Agent バージョン {__version__}") 