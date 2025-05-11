# -*- coding: utf-8 -*-
"""FusionScoringAgent: 語意相似度 + 規則分數 → 最終 RiskScore"""

import numpy as np

W_SIM = 0.3      # 字詞相似度權重
W_RULE = 0.2     # 規則權重
W_SEMANTIC = 0.5 # 語意相似度權重
assert abs(W_SIM + W_RULE + W_SEMANTIC - 1.0) < 1e-6


class FusionScoringAgent:
    def __init__(self, embedding_agent, rule_engine_agent, script_registry):
        self.embedder = embedding_agent
        self.rule_engine = rule_engine_agent
        self.registry = script_registry  # 提供腳本+向量+baseline

    # ---------- 主入口 ----------
    def evaluate(self, user_text: str, user_struct: dict[str], top_k: int = 3, use_tfidf: bool = True) -> list[dict]:
        """
        回傳 top‑k 結果：同時計算字詞相似度與語意相似度
        """
        if use_tfidf:
            # 計算字詞相似度（TF-IDF）
            word_sims = self.embedder.calculate_tfidf_similarities(
                user_text=user_text,
                script_texts=[s["title"] for s in self.registry.scripts]
            )
        else:
            # 使用嵌入向量進行計算
            user_vec = self.embedder.embed([user_text])[0]  # shape=(dim,)
            word_sims = np.dot(self.registry.script_matrix, user_vec)  # (N,)

        # 計算語意相似度（例如使用 Transformer 模型）
        semantic_sims = []
        for s in self.registry.scripts:
            semantic_sim = self.embedder.calculate_semantic_similarity(user_text, s)  # 假設這是語意相似度的計算方法
            semantic_sims.append(semantic_sim)

        results = []
        for idx, word_sim in enumerate(word_sims):
            s = self.registry.scripts[idx]
            # 這裡的語意相似度來自上面計算的結果
            semantic_sim = semantic_sims[idx]
            
            # 結合語意相似度、字詞相似度與規則分數
            rule_score = self.rule_engine.score(user_struct, s["calc_rules"], s["baseline_score"])
            final_score = W_SIM * word_sim + W_SEMANTIC * semantic_sim + W_RULE * rule_score

            results.append(
                {
                    "fse_id": s["fse_id"],
                    "title": s["title"],
                    "word_similarity": round(word_sim, 3),
                    "semantic_similarity": round(semantic_sim, 3),
                    "rule_score": round(rule_score, 3),
                    "risk_score": round(final_score, 3),
                }
            )

        results.sort(key=lambda x: x["risk_score"], reverse=True)
        return results[:top_k]
