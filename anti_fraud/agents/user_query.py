"""把使用者送來的 JSON 做最基本欄位正規化"""

class UserQueryService:
    @staticmethod
    def normalize(payload: dict[str]) -> dict[str]:
        """
        payload structure：
        {
          "description": "...自由文字...",
          "amount": 60000,
          "has_title_deed": false,
          "role": "房東"
        }
        只做簡易 pass‑through，可在此加 Regex / NER 解析地址、身份別...
        """
        allowed = {"amount": 0, "has_title_deed": False, "role": ""}
        out = {k: payload.get(k, v) for k, v in allowed.items()}
        return out
