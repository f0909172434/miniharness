"""讓 pytest 從倉庫根目錄直接找到 miniharness 包。"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
