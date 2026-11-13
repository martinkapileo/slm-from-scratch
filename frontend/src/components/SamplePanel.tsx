import { FormEvent, useState } from "react";
import { api } from "../api";

export default function SamplePanel({ run, enabled }: { run: string; enabled: boolean }) {
  const [prompt, setPrompt] = useState("ROMEO:");
  const [tokens, setTokens] = useState(300);
  const [temperature, setTemperature] = useState(0.8);
  const [topK, setTopK] = useState("");
  const [seed, setSeed] = useState(0);
  const [output, setOutput] = useState<string | null>(null);
  const [meta, setMeta] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await api.sample(run, {
        prompt, tokens, temperature, seed, top_k: topK ? Number(topK) : null,
      });
      setOutput(res.text);
      setMeta(`checkpoint from iter ${res.checkpoint_iter}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card">
      <h2>Generate text</h2>
      <form onSubmit={onSubmit} className="sample-form">
        <label className="wide">
          Prompt
          <input value={prompt} onChange={(e) => setPrompt(e.target.value)} />
        </label>
        <label>
          Tokens
          <input type="number" min={1} max={2000} value={tokens} onChange={(e) => setTokens(Number(e.target.value))} />
        </label>
        <label title="Lower = safer and more repetitive; higher = more creative and more errors">
          Temperature
          <input type="number" step={0.1} min={0.1} max={2} value={temperature} onChange={(e) => setTemperature(Number(e.target.value))} />
        </label>
        <label title="Only sample from the k most likely characters (blank = all)">
          Top-k
          <input type="number" min={1} placeholder="all" value={topK} onChange={(e) => setTopK(e.target.value)} />
        </label>
        <label>
          Seed
          <input type="number" value={seed} onChange={(e) => setSeed(Number(e.target.value))} />
        </label>
        <button type="submit" disabled={!enabled || busy}>
          {busy ? "Generating…" : enabled ? "Generate" : "No checkpoint yet"}
        </button>
      </form>
      {error && <div className="error">{error}</div>}
      {output != null && (
        <>
          <div className="muted small">{meta}</div>
          <pre className="sample">{output}</pre>
        </>
      )}
    </section>
  );
}
