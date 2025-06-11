"""
データベース接続の基底クラス
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class DatabaseConnection(ABC):
    """データベース接続の基底クラス"""

    def __init__(self, settings: Dict[str, Any]):
        """
        Args:
            settings: データベース接続設定
        """
        self.settings = settings
        self._connection: Optional[Any] = None

    @property
    def connection(self) -> Any:
        """データベース接続を取得"""
        if self._connection is None:
            self._connection = self._connect()
        return self._connection

    @abstractmethod
    def _connect(self) -> Any:
        """データベースに接続"""
        pass

    @abstractmethod
    def close(self) -> None:
        """データベース接続を閉じる"""
        pass

    def __enter__(self):
        """コンテキストマネージャーのエントリーポイント"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーの終了処理"""
        self.close() 