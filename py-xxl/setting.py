import os
from typing import Tuple, List, Dict, Union, Optional

# 定義常用的類型
Position = Tuple[int, int]
Size = Tuple[int, int]

# 遊戲配置類
class GameConfig:
    WIDTH = 900
    HEIGHT = 900
    NUMGRID = 10  # 網格數量
    GRIDSIZE = 64  # 網格大小
    XMARGIN = (WIDTH - GRIDSIZE * NUMGRID) // 2  # X軸邊距
    YMARGIN = (HEIGHT - GRIDSIZE * NUMGRID) // 2  # Y軸邊距
    ROOTDIR = os.path.dirname(os.path.abspath(__file__))  # 根目錄
    FPS = 60  # 幀率