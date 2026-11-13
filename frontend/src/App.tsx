import { useEffect, useState } from "react";
import { api, MetricRow, RunConfig, RunSummary } from "./api";
import LossChart from "./components/LossChart";
import SamplePanel from "./components/SamplePanel";

const POLL_MS = 5000;
const TARGET_VAL_LOSS = 1.7; // SPEC-001 acceptance criterion

const fmt = (v: number | null | undefined, digits = 4) => (v == null ? "—" : v.toFixed(digits));
const fmtParams = (n: number | null) => (n == null ? "—" : `${(n / 1e6).toFixed(2)}M`);
const fmtTime = (s: number | null) =>
  s == null ? "—" : s < 60 ? `${s.toFixed(0)}s` : `${Math.floor(s / 60)}m ${Math.round(s % 60)}s`;

function isLive(run: RunSummary) {
  return Date.now() / 1000 - run.updated < 120;
}

export default function App() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<MetricRow[]>([]);
  const [config, setConfig] = useState<RunConfig | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Poll the run list so live training shows up without a refresh.
  useEffect(() => {
    let cancelled = false;
    const load = () =>
      api
        .runs()
        .then((r) => {
          if (cancelled) return;
          setRuns(r);
          setError(null);
          setSelected((cur) => cur ?? r.sort((a, b) => b.updated - a.updated)[0]?.name ?? null);
        })
        .catch((e) => !cancelled && setError(String(e.message ?? e)));
    load();
    const id = setInterval(load, POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  const current = runs.find((r) => r.name === selected) ?? null;

  useEffect(() => {
    if (!selected) return;
    api.metrics(selected).then(setMetrics).catch(() => setMetrics([]));
    api.config(selected).then(setConfig).catch(() => setConfig(null));
  }, [selected, current?.updated]);

  return (
    <div className="layout">
      <header>
        <h1>SLM Dashboard</h1>
        <span className="muted">Phase 1 · character-level GPT</span>
      </header>

      {error && <div className="error">API unreachable: {error}</div>}

      <aside className="card">
        <h2>Runs</h2>
        {runs.length === 0 && <p className="muted">No runs yet. Train one with python -m slm.train.</p>}
        <ul className="run-list">
          {runs.map((r) => (
            <li key={r.name}>
              <button className={r.name === selected ? "active" : ""} onClick={() => setSelected(r.name)}>
                <span className="run-name">
                  {r.name}
                  {isLive(r) && <span className="live">live</span>}
                </span>
                <span className="muted small">
                  best val {fmt(r.best_val, 3)} · iter {r.last_iter ?? "—"}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <main>
        {current && (
          <>
            <section className="stats">
              <Stat label="Best val loss" value={fmt(current.best_val)}
                hint={current.best_val != null && current.best_val < TARGET_VAL_LOSS ? "meets target" : `target < ${TARGET_VAL_LOSS}`}
                good={current.best_val != null && current.best_val < TARGET_VAL_LOSS} />
              <Stat label="Train loss" value={fmt(current.last_train)} />
              <Stat label="Train − val gap" value={fmt(current.last_train != null && current.last_val != null ? current.last_val - current.last_train : null, 3)}
                hint="large gap = overfitting" />
              <Stat label="Iteration" value={String(current.last_iter ?? "—")} />
              <Stat label="Parameters" value={fmtParams(current.params)} />
              <Stat label="Elapsed" value={fmtTime(current.elapsed_s)} />
            </section>

            <section className="card">
              <h2>Loss curves</h2>
              <LossChart rows={metrics} target={TARGET_VAL_LOSS} />
            </section>

            <div className="two-col">
              <SamplePanel run={current.name} enabled={current.has_checkpoint} />
              <section className="card">
                <h2>Config</h2>
                {config ? <ConfigTable config={config} /> : <p className="muted">No config.</p>}
              </section>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function Stat({ label, value, hint, good }: { label: string; value: string; hint?: string; good?: boolean }) {
  return (
    <div className="card stat">
      <div className="muted small">{label}</div>
      <div className="stat-value">{value}</div>
      {hint && <div className={`small ${good ? "good" : "muted"}`}>{hint}</div>}
    </div>
  );
}

function ConfigTable({ config }: { config: RunConfig }) {
  return (
    <table className="config">
      <tbody>
        {(["model", "train"] as const).flatMap((section) =>
          Object.entries(config[section]).map(([k, v]) => (
            <tr key={`${section}.${k}`}>
              <td className="muted">{section}.{k}</td>
              <td>{String(v)}</td>
            </tr>
          )),
        )}
      </tbody>
    </table>
  );
}
