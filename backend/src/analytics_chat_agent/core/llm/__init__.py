"""
大規模言語モデル（LLM）関連の機能を提供するモジュール
"""

from .gemini import call_gemini
from .gpt import call_gpt

__all__ = ["call_gemini", "call_gpt"] 