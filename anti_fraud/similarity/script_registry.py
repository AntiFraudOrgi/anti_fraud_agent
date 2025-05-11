# -*- coding: utf-8 -*-
"""載入 FVE 腳本＋向量化後快取"""

import json
import os
import numpy as np
from agents.embedding import EmbeddingAgent


class ScriptRegistry:
    def __init__(self, json_path: str, embedder: EmbeddingAgent):
        self.scripts = json.load(open(json_path, "r", encoding="utf-8"))
        self.embedder = embedder
        self.script_matrix = self._precompute_embeddings()  # shape=(N, dim)
        self.similarity_scores = self._compute_similarity_scores()  # 儲存相似度分數

    def _precompute_embeddings(self) -> np.ndarray:
        descriptions = [s["description"] for s in self.scripts]
        return self.embedder.embed(descriptions)

    def _compute_similarity_scores(self) -> np.ndarray:
        """
        計算並儲存每個腳本的相似度分數，這裡可以根據需求計算字詞相似度或語意相似度。
        例如：
            - 這裡簡單使用語意相似度的範例
        """
        similarity_scores = []  # 儲存每個腳本的相似度
        for idx, script in enumerate(self.scripts):
            # 計算語意相似度
            # 假設你已經有了某種方法計算語意相似度或字詞相似度
            # 這裡使用腳本本身與某個預設的樣本描述進行相似度計算
            sample_text = "預設樣本文本"  # 可以根據實際需求定義
            similarity = self.embedder.similarity(self.script_matrix[idx], self.embedder.embed([sample_text])[0])
            similarity_scores.append(similarity)
        
        return np.array(similarity_scores)

    def get_script_by_id(self, fve_id: str) -> dict:
        """根據 FVE ID 查找腳本"""
        return next((s for s in self.scripts if s["fve_id"] == fve_id), None)

    def get_top_k_similar_scripts(self, user_vector: np.ndarray, top_k: int = 3) -> list:
        """
        根據用戶向量和預計算的向量，返回最相似的 top-k 腳本。
        """
        sims = np.dot(self.script_matrix, user_vector)
        sorted_indices = np.argsort(sims)[::-1][:top_k]
        return [self.scripts[idx] for idx in sorted_indices]
