from __future__ import annotations

import json
import os
import pathlib
import statistics
import time
from functools import lru_cache
from typing import List

import numpy as np
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

###############################################################################
# CONFIG
###############################################################################

# 0‑1 threshold over which we warn the user. Adjust empirically.
FRAUD_THRESHOLD: float = 0.42
os.environ["OPENAI_API_KEY"] = ""
# We hard‑code a tiny demo library of “FVE” fraud scripts.
# In production these could come from a database or remote store.
FRAUD_SCRIPTS_RAW: List[dict[str, str]] = [
    {
        "id": "deposit_scam",
        "title": "假租屋收取訂金",
        "script": (
            "詐騙者宣稱房源熱門、需要先匯訂金才能保留。收到款項後即人間蒸發，"
            "或帶看前臨時取消。通常價格異常便宜，並急迫催促匯款。"
        ),
    },
    {
        "id": "identity_theft",
        "title": "冒用業主身分出售",
        "script": (
            "偽造房屋權狀或屋主身分證件，假扮所有人對外出售並收取頭期款。"
            "常以無法現場看屋、屋主人在國外等理由拖延。"
        ),
    },
    {
        "id": "fake_agency_fees",
        "title": "假仲介收服務費",
        "script": (
            "自稱合法仲介但查無此公司，要求先支付高額服務費或文件費用。"
            "合約內容模糊，拒絕提供仲介證號。"
        ),
    },
]

# OpenAI model names (can be updated centrally)
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY not set in environment variables.")

###############################################################################
# HELPER FUNCTIONS
###############################################################################

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute the cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


@lru_cache(maxsize=None)
def embed(text: str) -> np.ndarray:  # noqa: D401
    """Thin wrapper around OpenAI embedding endpoint (with simple retry)."""
    for attempt in range(3):
        try:
            response = openai.embeddings.create(
                model=EMBED_MODEL,
                input=text,
            )
            return np.array(response.data[0].embedding)
        except openai.OpenAIError as e:  # transient error → exponential back‑off
            time.sleep(1.5 ** attempt)
            if attempt == 2:
                raise e


###############################################################################
# INITIALIZE FRAUD SCRIPT VECTORS
###############################################################################

def _prepare_script_library() -> List[dict]:
    """Vectorize all fraud scripts on start‑up."""
    enriched = []
    for entry in FRAUD_SCRIPTS_RAW:
        vec = embed(entry["script"])
        enriched.append({**entry, "vector": vec})
    return enriched


FRAUD_SCRIPTS = _prepare_script_library()

###############################################################################
# BUSINESS LOGIC
###############################################################################

def analyse_fraud(user_text: str) -> dict:
    """Return the best matching script, score (0‑100), and raw similarities."""

    user_vec = embed(user_text)

    sims = [cosine_similarity(user_vec, fs["vector"]) for fs in FRAUD_SCRIPTS]

    best_idx = int(np.argmax(sims))
    best_script = FRAUD_SCRIPTS[best_idx]
    best_sim = sims[best_idx]

    # Simple min‑max scale to 0‑100 (similarity ranges roughly −0.1‑0.9 for text‑embeddings)
    score = round(max(0.0, (best_sim - 0.2)) / 0.7 * 100, 1)
    score = min(max(score, 0.0), 100.0)

    return {
        "score": score,
        "script": best_script,
        "similarities": {fs["id"]: round(s, 4) for fs, s in zip(FRAUD_SCRIPTS, sims)},
    }


###############################################################################
# LLM EXPLANATION
###############################################################################

def generate_explanation(user_text: str, analysis: dict) -> str:
    """Use chat model to explain result to user in natural language."""

    fraud_flag = analysis["score"] >= FRAUD_THRESHOLD * 100
    system_prompt = (
        "你是一位房地產法律與詐騙預防專家。根據內部詐騙腳本相似度計算結果，"
        "向使用者說明其遭遇是否疑似詐騙以及建議後續行動。"
    )

    user_prompt = (
        "使用者描述：" + user_text + "\n\n"
        f"系統偵測分數：{analysis['score']} 分 (0‑100)\n"
        f"最相似腳本：{analysis['script']['title']}\n"
        f"腳本內容：{analysis['script']['script']}\n"
    )

    response = openai.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()


###############################################################################
# FASTAPI
###############################################################################

app = FastAPI(title="Real‑Estate Fraud AI", version="0.1")


class AnalyseRequest(BaseModel):
    text: str


class AnalyseResponse(BaseModel):
    score: float  # 0‑100
    explanation: str
    script_id: str
    debug_similarities: dict[str, float] | None = None  # optional detail


@app.post("/analyze", response_model=AnalyseResponse)
async def analyze_endpoint(req: AnalyseRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    analysis = analyse_fraud(req.text)
    explanation = generate_explanation(req.text, analysis)

    return AnalyseResponse(
        score=analysis["score"],
        explanation=explanation,
        script_id=analysis["script"]["id"],
        debug_similarities=analysis["similarities"],  # comment out in prod if undesired
    )


###############################################################################
# LOCAL DEV ENTRY POINT
###############################################################################

if __name__ == "__main__":
    # Running as script: `python main.py` → start server on localhost:8000
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
