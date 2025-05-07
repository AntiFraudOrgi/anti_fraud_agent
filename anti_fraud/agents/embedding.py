# -*- coding: utf-8 -*-
"""EmbeddingAgent: 文字 → 向量"""
import numpy as np
from langchain_openai import OpenAIEmbeddings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import os 

os.environ["OPENAI_API_KEY"] = "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"

class EmbeddingAgent:
    """使用 OpenAIEmbeddings 替代 sentence-transformers"""

    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.embedder = OpenAIEmbeddings(model=model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
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

    def calculate_tfidf_similarities(self, user_text: str, script_texts: list[str]) -> list[float]:
        """計算 user_text 與每個 script_text 的字詞相似度（TF-IDF）"""
        tfidf = TfidfVectorizer()
        corpus = [user_text] + script_texts  # 第一個是 user 的輸入
        tfidf_matrix = tfidf.fit_transform(corpus)
        sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
        return sims.tolist()
    
    def calculate_semantic_similarity(self, desc: str, struct: dict) -> float:
        """計算語意相似度（Transformer）"""
        struct_desc = struct.get("description", "")
        
        # 使用 OpenAIEmbeddings 的 embed_documents 方法來獲取嵌入向量
        user_vec = self.embed([desc])[0]  # 获取用户输入的嵌入向量
        struct_vec = self.embed([struct_desc])[0]  # 获取目标结构的嵌入向量
    
        # 計算兩者的語意相似度：使用餘弦相似度來比較兩個嵌入向量
        similarity = cosine_similarity([user_vec], [struct_vec])[0][0]
        return similarity
