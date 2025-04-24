# -*- coding: utf-8 -*-
"""EmbeddingAgent: 文字 → 向量"""
from typing import List
import numpy as np
from langchain_openai import OpenAIEmbeddings
import os 

os.environ["OPENAI_API_KEY"] = "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"

class EmbeddingAgent:
    """使用 OpenAIEmbeddings 替代 sentence-transformers"""

    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.embedder = OpenAIEmbeddings(model=model_name)

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        回傳 shape=(len(texts), dim) 的 numpy 陣列。
        LangChain 的 OpenAIEmbeddings 回傳的是 list[list[float]]。
        """
        embeddings = self.embedder.embed_documents(texts)
        return np.array(embeddings)

    def similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """餘弦相似度"""
        vec_a = vec_a / np.linalg.norm(vec_a)
        vec_b = vec_b / np.linalg.norm(vec_b)
        return float(np.dot(vec_a, vec_b))
