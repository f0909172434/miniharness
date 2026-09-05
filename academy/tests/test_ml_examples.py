"""以獨立 ML 環境檢查未來資訊隔離、梯度與短訓練；不要求核心安裝 PyTorch。"""
import importlib.util
from pathlib import Path
import pytest
import torch

PATH = Path(__file__).resolve().parents[1] / 'examples/tiny_lm.py'
SPEC = importlib.util.spec_from_file_location('tiny_lm', PATH)
tiny = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tiny)


@pytest.fixture
def model():
    torch.set_num_threads(2)
    torch.manual_seed(42)
    return tiny.TinyLM()


def test_future_tokens_cannot_change_prefix_logits(model):
    left = tiny.encode('read the code.').unsqueeze(0)
    right = left.clone()
    right[:, 5:] = (right[:, 5:] + 3) % len(tiny.CHARS)
    with torch.no_grad():
        a, b = model(left), model(right)
    assert a.shape == (1, left.shape[1], len(tiny.CHARS))
    assert torch.allclose(a[:, :5], b[:, :5], atol=1e-6)
    assert not torch.allclose(a[:, 5:], b[:, 5:])


def test_attention_receives_finite_nonzero_gradient(model):
    tiny.sentence_loss(model, tiny.TRAIN[0]).backward()
    grad = model.attention.qkv.weight.grad
    assert grad is not None and torch.isfinite(grad).all() and grad.abs().sum() > 0


def test_short_training_updates_parameters_and_reduces_fixture_loss(model):
    before = tiny.measure(model, tiny.TRAIN)['nll']
    initial = model.attention.qkv.weight.detach().clone()
    tiny.train(model, tiny.TRAIN, 15, 42)
    assert not torch.equal(initial, model.attention.qkv.weight)
    assert tiny.measure(model, tiny.TRAIN)['nll'] < before


def test_context_limit_is_explicit(model):
    with pytest.raises(ValueError, match='context exceeded'):
        model(torch.zeros((1, tiny.CONTEXT + 1), dtype=torch.long))
