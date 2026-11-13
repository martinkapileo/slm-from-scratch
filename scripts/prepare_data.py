"""Turn a raw text file into train/val token files.

Usage:
    # any text file you own (your target domain)
    python scripts/prepare_data.py --input path/to/corpus.txt --out data/my_corpus

    # the classic starter dataset (~1MB of Shakespeare)
    python scripts/prepare_data.py --download shakespeare --out data/shakespeare_char
"""

from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

from slm.data import prepare

SOURCES = {
    "shakespeare": "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt",
}


def main() -> None:
    p = argparse.ArgumentParser()
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="path to a UTF-8 text file")
    src.add_argument("--download", choices=SOURCES)
    p.add_argument("--out", required=True)
    p.add_argument("--val-frac", type=float, default=0.1)
    args = p.parse_args()

    if args.download:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        raw_path = out / "input.txt"
        if not raw_path.exists():
            urllib.request.urlretrieve(SOURCES[args.download], raw_path)
        text = raw_path.read_text(encoding="utf-8")
    else:
        text = Path(args.input).read_text(encoding="utf-8")

    tok = prepare(text, args.out, args.val_frac)
    print(f"chars={len(text):,} vocab={tok.vocab_size} -> {args.out}")


if __name__ == "__main__":
    main()
