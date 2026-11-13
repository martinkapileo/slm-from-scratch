"""Training loop.

Usage:
    python -m slm.train --config configs/shakespeare_char.toml

Writes to cfg.train.out_dir:
    ckpt.pt        best checkpoint by validation loss
    metrics.jsonl  one JSON line per eval (replaced by MLflow in Phase 2)
    config.json    the exact config used, for reproducibility
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from pathlib import Path

import numpy as np
import torch

from slm.config import Config, load_config
from slm.data import CharTokenizer, get_batch, load_split
from slm.model import GPT


def pick_device(pref: str) -> str:
    if pref != "auto":
        return pref
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def lr_at(it: int, cfg: Config) -> float:
    """Linear warmup, then cosine decay from learning_rate to min_lr."""
    t = cfg.train
    if it < t.warmup_iters:
        return t.learning_rate * (it + 1) / t.warmup_iters
    progress = (it - t.warmup_iters) / max(1, t.max_iters - t.warmup_iters)
    coeff = 0.5 * (1.0 + math.cos(math.pi * min(progress, 1.0)))
    return t.min_lr + coeff * (t.learning_rate - t.min_lr)


@torch.no_grad()
def estimate_loss(model: GPT, splits: dict, cfg: Config, device: str) -> dict[str, float]:
    """Average loss over several batches. model.eval() disables dropout."""
    model.eval()
    out = {}
    for name, data in splits.items():
        losses = torch.zeros(cfg.train.eval_iters)
        for k in range(cfg.train.eval_iters):
            x, y = get_batch(data, cfg.model.block_size, cfg.train.batch_size, device)
            _, loss = model(x, y)
            losses[k] = loss.item()
        out[name] = losses.mean().item()
    model.train()
    return out


def train(cfg: Config) -> dict[str, float]:
    t = cfg.train
    random.seed(t.seed)
    np.random.seed(t.seed)
    torch.manual_seed(t.seed)
    device = pick_device(t.device)

    tok = CharTokenizer.load(Path(t.data_dir) / "tokenizer.json")
    cfg.model.vocab_size = tok.vocab_size
    splits = {"train": load_split(t.data_dir, "train"), "val": load_split(t.data_dir, "val")}

    model = GPT(cfg.model).to(device)
    print(f"device={device} params={model.num_params() / 1e6:.2f}M vocab={tok.vocab_size}")

    # AdamW: decay weight matrices, but not biases / LayerNorm / embeddings' 1-D params.
    decay = [p for p in model.parameters() if p.dim() >= 2]
    no_decay = [p for p in model.parameters() if p.dim() < 2]
    optim = torch.optim.AdamW(
        [{"params": decay, "weight_decay": t.weight_decay}, {"params": no_decay, "weight_decay": 0.0}],
        lr=t.learning_rate,
        betas=(0.9, 0.95),
    )

    out = Path(t.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "config.json").write_text(json.dumps(cfg.to_dict(), indent=2))
    tok.save(out / "tokenizer.json")  # makes the run directory self-contained
    metrics_f = open(out / "metrics.jsonl", "w")

    best_val = float("inf")
    last = {}
    t0 = time.time()
    for it in range(t.max_iters + 1):
        lr = lr_at(it, cfg)
        for g in optim.param_groups:
            g["lr"] = lr

        if it % t.eval_interval == 0 or it == t.max_iters:
            last = estimate_loss(model, splits, cfg, device)
            row = {
                "iter": it, "lr": lr, **last,
                "elapsed_s": round(time.time() - t0, 1), "params": model.num_params(),
            }
            metrics_f.write(json.dumps(row) + "\n")
            metrics_f.flush()
            print(f"iter {it:5d} | train {last['train']:.4f} | val {last['val']:.4f} | lr {lr:.2e}")
            if last["val"] < best_val:
                best_val = last["val"]
                torch.save({"model": model.state_dict(), "config": cfg.to_dict(), "iter": it}, out / "ckpt.pt")
            if it == t.max_iters:
                break

        x, y = get_batch(splits["train"], cfg.model.block_size, t.batch_size, device)
        _, loss = model(x, y)
        optim.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), t.grad_clip)
        optim.step()

    metrics_f.close()
    return {**last, "best_val": best_val}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--max-iters", type=int, help="override train.max_iters")
    args = p.parse_args()
    cfg = load_config(args.config)
    if args.max_iters is not None:
        cfg.train.max_iters = args.max_iters
    print(json.dumps(train(cfg)))


if __name__ == "__main__":
    main()
