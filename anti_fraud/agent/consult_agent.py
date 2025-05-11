import json, os
from pathlib import Path
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# Use absolute path to avoid issues: ../
BASE_DIR = Path(__file__).resolve().parent.parent
LAW_PATH  = BASE_DIR / "law.json"
LAW_DB    = json.loads(LAW_PATH.read_text(encoding="utf-8"))

# prompt template
SYSTEM_PROMPT = """
You are a senior Anti‑Fraud Counselor at “AntiFraud AI”, focusing on real‑estate scams.
You will receive four fields: user_query, fse, risk_score, semantic_similarity.
You should consult {LAW_DB} and cite the applicable articles at the end of your recommendations.

Report requirements:
1. Always reply in **Traditional Chinese**.
2. Tone: empathetic and professional; do not frighten or belittle the user.
3. Output exactly three sections:
   (1) **Overall Risk Level** — High / Medium / Low, plus a one‑sentence summary.  
   (2) **Key Red Flags** — 3–5 bullet points, one line each.  
   (3) **Actionable Recommendations** — step‑by‑step bullets, may include official or legal hotlines.  
       • [IMPORTANT] If a relevant article exists in {LAW_DB}, append one line at the end or you should stricty skip this step:
         “⚖ 法律依據：〈Law name & article number〉”.

4. When referring to an FSE (Fraud Script Entry), mention only the script title and risk score; never expose internal IDs.
5. Do not give definitive legal advice or guarantees; encourage consulting a lawyer or land‑registration professional when appropriate.
6. You should always use traditional chinese to response.
"""

USER_PROMPT = """
user query: {user_query}
corresponded fraud script entry: {fse}
risk_score: {risk_score}
semantic_similarity: {semantic_similarity}
"""

# reconstruct user prompt
def _build_prompt(user_query: str, fse_hits: list[dict]) -> str:
    chunks = []
    # pick top 2
    for fse in fse_hits[:2]:  
        chunks.append(
            USER_PROMPT.format(
                user_query=user_query,
                fse=fse["title"],                    
                risk_score=f"{fse['risk_score']:.2f}",
                semantic_similarity=f"{fse['semantic_similarity']:.2f}",
            )
        )
    return "\n---\n".join(chunks)


def consult(user_query: str, fse_list: list[dict]) -> str:
    prompt = _build_prompt(user_query, fse_list)
    response = client.responses.create(
        model = "gpt-4o",
        input = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
    )
    return response.output_text

if __name__ == "__main__":
    # 模擬使用者敘述
    user_query = "對方出示房屋產權、印章，我不確定真假。"

    # 模擬最相似的 FSE 結果
    fse_hits = [
        {
            "title": "出售：偽造房屋權狀出售",
            "fse_id": "FSE-002",
            "risk_score": 0.85,
            "semantic_similarity": 0.91,
        },
        {
            "title": "偽造房屋權狀出售",
            "fse_id": "FSE-002",
            "risk_score": 0.48,
            "semantic_similarity": 0.16,
        },
    ]
    report = consult(user_query, fse_hits)
    print("\n🔍 AI 防詐騙專家報告：\n")
    print(report)