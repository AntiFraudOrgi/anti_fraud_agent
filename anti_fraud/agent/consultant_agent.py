import json
import os
from pathlib import Path
import openai
from dotenv import load_dotenv

class consultant_agent:

    _SYSTEM_PROMPT = """
    You are a senior Anti‑Fraud Counselor at “AntiFraud AI”, focusing on real‑estate scams.
    You will receive four fields: user_query, fse, risk_score, semantic_similarity.

    Report requirements:
    1. Always reply in **Traditional Chinese**.
    2. Tone: empathetic and professional; do not frighten or belittle the user.
    3. Output exactly three sections:
    (1) **Overall Risk Level** — High / Medium / Low, plus a one‑sentence summary.  
    (2) **Key Red Flags** — 3–5 bullet points, one line each.  
    (3) **Actionable Recommendations** — step‑by‑step bullets, may include official or legal hotlines.  

    4. When referring to an FSE (Fraud Script Entry), mention only the script title and risk score; never expose internal IDs.
    5. Do not give definitive legal advice or guarantees; encourage consulting a lawyer or land‑registration professional when appropriate.
    6. You should always use traditional chinese to response.
    """

    _USER_PROMPT_TMPL = """
    user query: {user_query}
    corresponded fraud script entry: {fse}
    risk_score: {risk_score}
    semantic_similarity: {semantic_similarity}
    """

    def __init__(self, model: str = "gpt-4o", max_fse: int = 2):
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self._client = openai.OpenAI()
        self.model = model
        self.max_fse = max_fse

        # law consultation!!!
        self.base_dir: Path = Path(__file__).resolve().parent
        # self.law_path: Path = self.base_dir / "law.json"
        # self.law_db: list[dict] = json.loads(self.law_path.read_text("utf-8"))

    def consult(self, user_query: str, fse_list: list[dict]) -> str:
        # tidy user prompt 
        prompt = self._build_prompt(user_query, fse_list)
        response = self._client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": self._SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return response.output_text

    def _build_prompt(self, user_query: str, fse_hits: list[dict]) -> str:
        chunks: list[str] = []
        for fse in fse_hits[: self.max_fse]:
            chunks.append(
                self._USER_PROMPT_TMPL.format(
                    user_query=user_query,
                    fse=fse["title"],
                    risk_score=f"{fse['risk_score']:.2f}",
                    semantic_similarity=f"{fse['semantic_similarity']:.2f}",
                )
            )
        return "\n---\n".join(chunks)

def consult(user_query: str, fse_list: list[dict]) -> str:  
    agent = consultant_agent()
    return agent.consult(user_query, fse_list)


# testing
if __name__ == "__main__":
    # fake input
    user_query = "對方出示房屋產權、印章，我不確定真假。"
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
