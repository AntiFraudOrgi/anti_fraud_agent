from similarity.user_query import UserQueryService
from similarity.script_registry import ScriptRegistry
from similarity.embedding import EmbeddingAgent
from similarity.rule_engine import RuleEngineAgent
from similarity.fusion_score import FusionScoringAgent


# -------- 系統初始化 --------
DATA_PATH = "anti_fraud/fse.json"

embedder = EmbeddingAgent()
registry = ScriptRegistry(DATA_PATH, embedder)
rule_engine = RuleEngineAgent()
fusion_agent = FusionScoringAgent(embedder, rule_engine, registry)

def ask():
    desc = input("請描述你遇到的狀況：").strip()
    if not desc:
        print("Bye!")
    # 其餘欄位可留空
    amount_in = input("💰 交易金額 (留空略過)：").strip()
    has_deed_in = input("📄 是否拿到權狀文件？(y/N)：").strip().lower()
    role_in = input("🧑‍💼 對方身分 (房東/仲介/貸款代辦… 可留空)：").strip()
    
    payload: dict[str] = {
        "description": desc,
        "amount": int(amount_in) if amount_in else 0,
        "has_title_deed": has_deed_in.startswith("y"),
        "role": role_in,
    }

    # -------- 計算最相似 FSE --------
    struct = UserQueryService.normalize(payload)
    top_hits = fusion_agent.evaluate(desc, struct, top_k=3)
        
    print("\n📊 推薦結果 (RiskScore↑)：")
    for i, hit in enumerate(top_hits, 1):
        print(f" {i}. {hit['title']}  "
              f"[FSE: {hit['fse_id']}]  "
              f"Risk: {hit['risk_score']:.2f}  "
             f"(語意相似度: {hit['semantic_similarity']:.2f} / 字詞相似度: {hit['word_similarity']:.2f})")
    print("-" * 60)

# ---------- 程式進入點 ----------
if __name__ == "__main__":
    while True:
         ask()