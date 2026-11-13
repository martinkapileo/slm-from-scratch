"""Generate text from a trained checkpoint.

Usage:
    python -m slm.sample --run runs/shakespeare_char --prompt "ROMEO:" --tokens 300
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from slm.config import ModelConfig
from slm.data import CharTokenizer
from slm.model import GPT


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True, help="run directory containing ckpt.pt")
    p.add_argument("--prompt", default="\n")
    p.add_argument("--tokens", type=int, default=300)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--top-k", type=int, default=None)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    torch.manual_seed(args.seed)
    ckpt = torch.load(Path(args.run) / "ckpt.pt", map_location="cpu")
    model_cfg = ModelConfig(**ckpt["config"]["model"])
    tok = CharTokenizer.load(Path(ckpt["config"]["train"]["data_dir"]) / "tokenizer.json")

    model = GPT(model_cfg)
    model.load_state_dict(ckpt["model"])
    model.eval()

    idx = torch.tensor([tok.encode(args.prompt)], dtype=torch.long)
    out = model.generate(idx, args.tokens, temperature=args.temperature, top_k=args.top_k)
    print(tok.decode(out[0].tolist()))


if __name__ == "__main__":
    main()
