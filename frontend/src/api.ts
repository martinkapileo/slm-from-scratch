export interface RunSummary {
  name: string;
  evals: number;
  last_iter: number | null;
  last_train: number | null;
  last_val: number | null;
  best_val: number | null;
  elapsed_s: number | null;
  params: number | null;
  has_checkpoint: boolean;
  updated: number;
}

export interface MetricRow {
  iter: number;
  lr: number;
  train: number;
  val: number;
  elapsed_s: number;
}

export interface RunConfig {
  model: Record<string, number | string>;
  train: Record<string, number | string>;
}

export interface SampleRequest {
  prompt: string;
  tokens: number;
  temperature: number;
  top_k: number | null;
  seed: number;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `${res.status} ${res.statusText}`);
  }
  return res.json();
}

const enc = encodeURIComponent;

export const api = {
  runs: () => request<RunSummary[]>("/api/runs"),
  metrics: (run: string) => request<MetricRow[]>(`/api/runs/${enc(run)}/metrics`),
  config: (run: string) => request<RunConfig>(`/api/runs/${enc(run)}/config`),
  sample: (run: string, body: SampleRequest) =>
    request<{ text: string; checkpoint_iter: number }>(`/api/runs/${enc(run)}/sample`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
};
