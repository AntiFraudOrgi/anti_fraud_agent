# -*- coding: utf-8 -*-
"""RuleEngineAgent: 依 calc_rules 公式計算風險分"""

import math
from asteval import Interpreter  # 安全的 eval 替代

_SAFE_NAMES = {"sqrt": math.sqrt, "abs": abs, "min": min, "max": max}


class RuleEngineAgent:
    """將 user_info dict 餵入腳本中的 calc_rules 公式"""

    def __init__(self):
        self._aeval = Interpreter(usersyms=_SAFE_NAMES, err_writer=None)

    def score(self, user_info: dict[str], calc_rule: str, baseline: float, similarity_score: float = 1.0) -> float:
        """
        Args
        ----
        user_info : {'amount': 60000, 'has_title_deed': False, ...}
        calc_rule : str, e.g. "risk = baseline + 0.2*(amount>50000) + 0.1*(not has_title_deed)"
        baseline  : float, base risk in [0,1)
        similarity_score : float, 預設為 1.0，可根據相似度調整風險分數
        """
        _locals = {"baseline": baseline, "similarity_score": similarity_score, **user_info}
        try:
            self._aeval.symtable.update(_locals)
            self._aeval(calc_rule)
            return float(self._aeval.symtable.get("risk", baseline))
        except Exception:
            # 若公式錯誤，退回 baseline
            return baseline
