import os
from typing import Tuple, List, Dict, Union, Optional
from puzzle import Puzzle
from setting import GameConfig

# 定義常用的類型
Position = Tuple[int, int]
Size = Tuple[int, int]

class Bomb(Puzzle):
    """炸彈類別"""
    def __init__(self, position: Position):
        super().__init__(
            img_path=os.path.join(GameConfig.ROOTDIR, 'resources/images/bomb.png'),
            size=(GameConfig.GRIDSIZE, GameConfig.GRIDSIZE),
            position=position,
            downlen=0
        )
        self.type = 'bomb'  # 明確設置類型為 'bomb'
        self.is_bomb = True