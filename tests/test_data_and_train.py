import numpy as np

from slm.config import Config, ModelConfig, TrainConfig
from slm.data import CharTokenizer, get_batch, load_split, prepare
from slm.train import train

TEXT = "hello world, this is a tiny corpus for testing. " * 40


def test_tokenizer_roundtrip(tmp_path):
    tok = CharTokenizer.fit(TEXT)
    assert tok.decode(tok.encode(TEXT)) == TEXT
    tok.save(tmp_path / "t.json")
    assert CharTokenizer.load(tmp_path / "t.json").chars == tok.chars


def test_prepare_split_is_contiguous(tmp_path):
    prepare(TEXT, tmp_path, val_frac=0.1)
    train_ids, val_ids = load_split(tmp_path, "train"), load_split(tmp_path, "val")
    assert len(train_ids) + len(val_ids) == len(TEXT)
    tok = CharTokenizer.load(tmp_path / "tokenizer.json")
    assert tok.decode(np.concatenate([train_ids, val_ids]).tolist()) == TEXT


def test_batch_targets_are_shifted_inputs():
    data = np.arange(100, dtype=np.uint16)
    x, y = get_batch(data, block_size=8, batch_size=4, device="cpu")
    assert (y[:, :-1] == x[:, 1:]).all()


def test_training_smoke_reduces_loss(tmp_path):
    prepare(TEXT, tmp_path / "data")
    cfg = Config(
        model=ModelConfig(block_size=16, n_layer=1, n_head=2, n_embd=32, dropout=0.0),
        train=TrainConfig(
            data_dir=str(tmp_path / "data"), out_dir=str(tmp_path / "run"),
            batch_size=8, max_iters=150, eval_interval=50, eval_iters=5,
            learning_rate=3e-3, warmup_iters=5, device="cpu",
        ),
    )
    result = train(cfg)
    assert result["best_val"] < np.log(cfg.model.vocab_size)
    assert (tmp_path / "run" / "ckpt.pt").exists()
    assert (tmp_path / "run" / "metrics.jsonl").exists()
