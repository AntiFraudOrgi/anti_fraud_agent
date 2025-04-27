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

    def _precompute_embeddings(self) -> np.ndarray:
        descriptions = [s["description"] for s in self.scripts]
        return self.embedder.embed(descriptions)
