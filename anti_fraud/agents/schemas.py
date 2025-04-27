from pydantic import BaseModel, Field
from typing import Optional


class QueryIn(BaseModel):
    description: str = Field(..., example="對方自稱屋主，要求先匯 6 萬訂金才可簽約")
    amount: Optional[int] = Field(0, example=60000)
    has_title_deed: Optional[bool] = Field(False, example=False)
    role: Optional[str] = Field("", example="房東")


class ResultSchema(BaseModel):
    fve_id: str
    title: str
    similarity: float
    rule_score: float
    risk_score: float
