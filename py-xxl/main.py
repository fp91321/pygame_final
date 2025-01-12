from typing import Tuple, List, Dict, Union, Optional
from gamescene import GameScene
# 定義常用的類型
Position = Tuple[int, int]
Size = Tuple[int, int]

def main():
    """主程序"""
    game_scene = GameScene()
    game_scene.run()

if __name__ == '__main__':
    main()