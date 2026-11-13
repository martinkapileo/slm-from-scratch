"""Generate text from a trained checkpoint.

Usage:
    python -m slm.sample --run runs/shakespeare_char --prompt "ROMEO:" --tokens 300
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import torch

from slm.config import ModelConfig
from slm.data import CharTokenizer
from slm.model import GPT


@dataclass
class LoadedRun:
    model: GPT
    tokenizer: CharTokenizer
    config: dict
    iter: int


def load_run(run_dir: str | Path) -> LoadedRun:
    """Load the best checkpoint and its tokenizer from a run directory.

    The tokenizer is read from the run directory when present (runs are then
    self-contained), falling back to the training data_dir for older runs.
    """
    run_dir = Path(run_dir)
    ckpt = torch.load(run_dir / "ckpt.pt", map_location="cpu", weights_only=True)
    tok_path = run_dir / "tokenizer.json"
    if not tok_path.exists():
        tok_path = Path(ckpt["config"]["train"]["data_dir"]) / "tokenizer.json"
    model = GPT(ModelConfig(**ckpt["config"]["model"]))
    model.load_state_dict(ckpt["model"])
    model.eval()
    return LoadedRun(model, CharTokenizer.load(tok_path), ckpt["config"], ckpt.get("iter", -1))


def generate_text(
    run: LoadedRun,
    prompt: str,
    tokens: int,
    temperature: float = 0.8,
    top_k: int | None = None,
    seed: int = 0,
) -> str:
    torch.manual_seed(seed)
    unknown = sorted({c for c in prompt if c not in run.tokenizer.stoi})
    if unknown:
        raise ValueError(f"prompt has characters not in the vocabulary: {unknown}")
    idx = torch.tensor([run.tokenizer.encode(prompt or "\n")], dtype=torch.long)
    out = run.model.generate(idx, tokens, temperature=temperature, top_k=top_k)
    return run.tokenizer.decode(out[0].tolist())


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True, help="run directory containing ckpt.pt")
    p.add_argument("--prompt", default="\n")
    p.add_argument("--tokens", type=int, default=300)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--top-k", type=int, default=None)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    run = load_run(args.run)
    print(generate_text(run, args.prompt, args.tokens, args.temperature, args.top_k, args.seed))


if __name__ == "__main__":
    main()
