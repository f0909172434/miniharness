"""正常、邊界與異常三類測試的參考。"""
import pytest
from numeric import clamp

def test_normal():
    assert clamp(3, 0, 5) == 3

def test_boundary():
    assert clamp(-1, 0, 5) == 0
    assert clamp(6, 0, 5) == 5
    assert clamp(5, 0, 5) == 5
    assert clamp(0, 0, 0) == 0

def test_error():
    with pytest.raises(ValueError):
        clamp(1, 5, 0)
