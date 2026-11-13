"""Tests that encode the fundamentals: each one checks a property every GPT must have."""

import math

import torch

from slm.config import ModelConfig
from slm.model import GPT


def tiny_cfg(**kw) -> ModelConfig:
    base = dict(vocab_size=20, block_size=16, n_layer=2, n_head=2, n_embd=32, dropout=0.0)
    base.update(kw)
    return ModelConfig(**base)


def test_forward_shapes():
    model = GPT(tiny_cfg())
    idx = torch.randint(0, 20, (3, 10))
    logits, loss = model(idx, idx)
    assert logits.shape == (3, 10, 20)
    assert loss.ndim == 0


def test_initial_loss_is_near_uniform():
    """An untrained model should be ~uniformly unsure: loss ~= ln(vocab_size).

    Targets must be independent of inputs: with weight tying, an untrained model
    already slightly favors predicting its own input token, so targets == inputs
    would give a loss noticeably below ln(vocab_size).
    """
    torch.manual_seed(0)
    model = GPT(tiny_cfg())
    idx = torch.randint(0, 20, (8, 16))
    targets = torch.randint(0, 20, (8, 16))
    _, loss = model(idx, targets)
    assert abs(loss.item() - math.log(20)) < 0.3


def test_causality_future_tokens_do_not_leak():
    """Changing a later token must not change predictions at earlier positions."""
    torch.manual_seed(0)
    model = GPT(tiny_cfg()).eval()
    a = torch.randint(0, 20, (1, 12))
    b = a.clone()
    b[0, 8:] = (b[0, 8:] + 1) % 20
    la, _ = model(a)
    lb, _ = model(b)
    assert torch.allclose(la[:, :8], lb[:, :8], atol=1e-6)
    assert not torch.allclose(la[:, 8:], lb[:, 8:])


def test_can_overfit_a_single_batch():
    """If a model can't memorize one batch, something is broken."""
    torch.manual_seed(0)
    model = GPT(tiny_cfg())
    x = torch.randint(0, 20, (4, 16))
    y = torch.roll(x, -1, dims=1)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3)
    for _ in range(300):
        _, loss = model(x, y)
        opt.zero_grad()
        loss.backward()
        opt.step()
    assert loss.item() < 0.1


def test_generate_appends_tokens_and_respects_context():
    model = GPT(tiny_cfg(block_size=8)).eval()
    out = model.generate(torch.zeros((1, 1), dtype=torch.long), max_new_tokens=20, top_k=5)
    assert out.shape == (1, 21)
