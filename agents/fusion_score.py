# -*- coding: utf-8 -*-
"""FusionScoringAgent: 語意相似度 + 規則分數 → 最終 RiskScore"""

import numpy as np

W_SIM = 0.7      # 語意相似度權重
W_RULE = 0.3     # 規則權重
assert abs(W_SIM + W_RULE - 1.0) < 1e-6


class FusionScoringAgent:
    def __init__(self, embedding_agent, rule_engine_agent, script_registry):
        self.embedder = embedding_agent
        self.rule_engine = rule_engine_agent
        self.registry = script_registry  # 提供腳本+向量+baseline

    # ---------- 主入口 ----------
    def evaluate(self, user_text: str, user_struct: dict[str], top_k: int = 3) -> list[dict]:
        """
        回傳 top‑k 結果：
        [{
            'fve_id': ...,
            'title': ...,
            'similarity': 0.83,
            'rule_score': 0.74,
            'risk_score': 0.80
        }, ...]
        """
        user_vec = self.embedder.embed([user_text])[0]  # shape=(dim,)
        sims = np.dot(self.registry.script_matrix, user_vec)  # (N,)

        results = []
        for idx, sim in enumerate(sims):
            s = self.registry.scripts[idx]
            rule_score = self.rule_engine.score(user_struct, s["calc_rules"], s["baseline_score"])
            final_score = W_SIM * sim + W_RULE * rule_score
            results.append(
                {
                    "fse_id": s["fse_id"],
                    "title": s["title"],
                    "similarity": round(sim, 3),
                    "rule_score": round(rule_score, 3),
                    "risk_score": round(final_score, 3),
                }
            )

        results.sort(key=lambda x: x["risk_score"], reverse=True)
        return results[:top_k]
