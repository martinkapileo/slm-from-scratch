import importlib

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from slm.config import Config, ModelConfig, TrainConfig  # noqa: E402
from slm.data import prepare  # noqa: E402
from slm.train import train  # noqa: E402


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("dash")
    prepare("to be or not to be, that is the question. " * 50, tmp / "data")
    train(Config(
        model=ModelConfig(block_size=16, n_layer=1, n_head=2, n_embd=16, dropout=0.0),
        train=TrainConfig(
            data_dir=str(tmp / "data"), out_dir=str(tmp / "runs" / "tiny"),
            batch_size=4, max_iters=20, eval_interval=10, eval_iters=2, warmup_iters=2, device="cpu",
        ),
    ))
    mp = pytest.MonkeyPatch()
    mp.setenv("SLM_RUNS_DIR", str(tmp / "runs"))
    import slm.dashboard.api as api
    importlib.reload(api)
    yield TestClient(api.app)
    mp.undo()


def test_list_runs(client):
    runs = client.get("/api/runs").json()
    assert [r["name"] for r in runs] == ["tiny"]
    assert runs[0]["has_checkpoint"] and runs[0]["evals"] == 3


def test_metrics_and_config(client):
    assert [r["iter"] for r in client.get("/api/runs/tiny/metrics").json()] == [0, 10, 20]
    assert client.get("/api/runs/tiny/config").json()["model"]["n_embd"] == 16


def test_sample(client):
    r = client.post("/api/runs/tiny/sample", json={"prompt": "to be", "tokens": 10})
    assert r.status_code == 200
    assert r.json()["text"].startswith("to be") and len(r.json()["text"]) == 15


def test_sample_rejects_unknown_characters(client):
    assert client.post("/api/runs/tiny/sample", json={"prompt": "Z!"}).status_code == 422


def test_path_traversal_is_rejected(client):
    assert client.get("/api/runs/..%2F..%2Fetc/metrics").status_code == 404
    assert client.get("/api/runs/missing/metrics").status_code == 404
