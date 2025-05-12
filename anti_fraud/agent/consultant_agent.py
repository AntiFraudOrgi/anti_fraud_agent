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
    
    # default model: gpt-4o
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
        try:
            prompt = self._build_prompt(user_query, fse_list)
            print("🧾 Prompt:\n", prompt)
            response = self._client.chat.completions.create(  # 若你用 `openai==1.x`
                model=self.model,
                messages=[
                    {"role": "system", "content": self._SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            print("❌ 呼叫失敗:", e)
            return "⚠️ 無法產生報告，請檢查輸入格式或 OpenAI 設定"


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


# testing
if __name__ == "__main__":
    # fake input
    user_query = "對方出示房屋產權、印章，我不確定真假。"
    # fse_hits = [
    #     {
    #         "title": "出售：偽造房屋權狀出售",
    #         "fse_id": "FSE-002",
    #         "risk_score": 0.85,
    #         "semantic_similarity": 0.91,
    #     },
    #     {
    #         "title": "偽造房屋權狀出售",
    #         "fse_id": "FSE-002",
    #         "risk_score": 0.48,
    #         "semantic_similarity": 0.16,
    #     },
    # ]
    fse_hits = [{'fse_id': 'FSE-002', 'title': '出售：偽造房屋權狀出售', 'word_similarity': 0.0, 'semantic_similarity': 0.073, 'rule_score': 0.7, 'risk_score': 0.177}, {'fse_id': 'FSE-001', 'title': '租金：假房東收取大額訂金', 'word_similarity': 0.0, 'semantic_similarity': 0.066, 'rule_score': 0.65, 'risk_score': 0.163}, {'fse_id': 'FSE-003', 'title': '貸款：貸款代辦先收手續費後失聯', 'word_similarity': 0.0, 'semantic_similarity': 0.087, 'rule_score': 0.6, 'risk_score': 0.163}]
    agent = consultant_agent()
    report = agent.consult(user_query, fse_hits)
    print("\n🔍 AI 防詐騙專家報告：\n")
    print(report)
