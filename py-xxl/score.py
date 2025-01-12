import random
from typing import Tuple, List, Dict, Union, Optional
# 分數管理類
class ScoreManager:
    def __init__(self):
        self.score = 0
        self.reward = 10
        self.target_scores = {1: 150, 2: 300, 3: 700}  # 各關卡目標分數
    
    def get_level_target(self, level: int) -> int:
        """獲取指定關卡的目標分數"""
        return self.target_scores.get(level, 300)
    
    def add_score(self, match_length: int) -> int:
        """根據消除長度增加分數"""
        score_multiplier = 1 if match_length == 3 else 2 if match_length == 4 else 4
        match_score = self.reward * score_multiplier
        self.score += match_score
        return match_score
    
    def adjust_score(self) -> str:
        """隨機調整分數並返回提示訊息"""
        score_change = 10 * random.randint(-2, 5)
        self.score += score_change
        self.score = max(0, self.score)
        
        if score_change > 0:
            return f"Bonus! Score + {score_change}!"
        elif score_change < 0:
            return f"Penalty! Score - {abs(score_change)}!"
        return "No score adjustment this time."