import { API_BASE, DEFAULT_TOP_K } from "./config.js";

export async function queryFraud(payload = {}, topK = DEFAULT_TOP_K) {
  const res = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...payload, top_k: topK })
  });
  if (!res.ok) throw new Error("API Error");
  return res.json(); // [{fve_id, title, similarity, rule_score, risk_score}, ...]
}
