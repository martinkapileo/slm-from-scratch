"""Tokenization and batching.

Phase 1 uses a character-level tokenizer: every unique character is a token.
It is the simplest tokenizer that works, which makes it ideal for learning.
Phase 2 replaces it with BPE (subword) tokenization.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch


class CharTokenizer:
    def __init__(self, chars: list[str]):
        self.chars = chars
        self.stoi = {ch: i for i, ch in enumerate(chars)}
        self.itos = {i: ch for i, ch in enumerate(chars)}

    @classmethod
    def fit(cls, text: str) -> CharTokenizer:
        return cls(sorted(set(text)))

    @property
    def vocab_size(self) -> int:
        return len(self.chars)

    def encode(self, text: str) -> list[int]:
        return [self.stoi[c] for c in text]

    def decode(self, ids: list[int]) -> str:
        return "".join(self.itos[i] for i in ids)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps({"type": "char", "chars": self.chars}))

    @classmethod
    def load(cls, path: str | Path) -> CharTokenizer:
        return cls(json.loads(Path(path).read_text())["chars"])


def prepare(text: str, out_dir: str | Path, val_frac: float = 0.1) -> CharTokenizer:
    """Tokenize raw text and write train.bin / val.bin / tokenizer.json.

    The split is contiguous (first 90% train, last 10% val), not random:
    shuffling characters would leak validation text into training.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tok = CharTokenizer.fit(text)
    ids = np.array(tok.encode(text), dtype=np.uint16)
    n_val = int(len(ids) * val_frac)
    ids[:-n_val].tofile(out / "train.bin")
    ids[-n_val:].tofile(out / "val.bin")
    tok.save(out / "tokenizer.json")
    return tok


def load_split(data_dir: str | Path, split: str) -> np.ndarray:
    return np.fromfile(Path(data_dir) / f"{split}.bin", dtype=np.uint16)


def get_batch(
    data: np.ndarray, block_size: int, batch_size: int, device: str
) -> tuple[torch.Tensor, torch.Tensor]:
    """Sample random windows. y is x shifted one token left: the model learns
    to predict token t+1 from tokens 0..t, at every position at once."""
    ix = np.random.randint(0, len(data) - block_size - 1, size=batch_size)
    x = torch.stack([torch.from_numpy(data[i : i + block_size].astype(np.int64)) for i in ix])
    y = torch.stack([torch.from_numpy(data[i + 1 : i + 1 + block_size].astype(np.int64)) for i in ix])
    return x.to(device), y.to(device)
