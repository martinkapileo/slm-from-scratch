"""Typed configuration loaded from TOML files in configs/.

Keeping every hyperparameter in a versioned config file (not hard-coded) is the
first step toward reproducible experiments.
"""

from __future__ import annotations

import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class ModelConfig:
    vocab_size: int = 0  # filled in from the tokenizer at train time
    block_size: int = 128  # context length (tokens the model can see)
    n_layer: int = 4
    n_head: int = 4
    n_embd: int = 128
    dropout: float = 0.1


@dataclass
class TrainConfig:
    data_dir: str = "data/shakespeare_char"
    out_dir: str = "runs/default"
    batch_size: int = 32
    max_iters: int = 2000
    eval_interval: int = 200
    eval_iters: int = 50
    learning_rate: float = 1e-3
    min_lr: float = 1e-4
    warmup_iters: int = 100
    weight_decay: float = 0.1
    grad_clip: float = 1.0
    seed: int = 1337
    device: str = "auto"  # "auto" | "cpu" | "cuda" | "mps"


@dataclass
class Config:
    model: ModelConfig = field(default_factory=ModelConfig)
    train: TrainConfig = field(default_factory=TrainConfig)

    def to_dict(self) -> dict:
        return asdict(self)


def load_config(path: str | Path) -> Config:
    with open(path, "rb") as f:
        raw = tomllib.load(f)
    return Config(
        model=ModelConfig(**raw.get("model", {})),
        train=TrainConfig(**raw.get("train", {})),
    )
