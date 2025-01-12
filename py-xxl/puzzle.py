import pygame
from typing import Tuple, List, Dict, Union, Optional

# 定義常用的類型
Position = Tuple[int, int]
Size = Tuple[int, int]

# 寶石類
class Puzzle(pygame.sprite.Sprite):
    def __init__(self, img_path: str, size: Size, position: Position, downlen: int):
        super().__init__()
        self.image = pygame.image.load(img_path)
        self.image = pygame.transform.smoothscale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position
        self.downlen = downlen
        self.target_x = position[0]
        self.target_y = position[1] + downlen
        self.type = img_path.split('/')[-1].split('.')[0]
        self.fixed = False
        self.speed_x = 16
        self.speed_y = 16
        self.direction = 'down'

    def move(self) -> None:
        """移動寶石"""
        if self.direction == 'down':
            self.rect.top = min(self.target_y, self.rect.top + self.speed_y)
        elif self.direction == 'up':
            self.rect.top = max(self.target_y, self.rect.top - self.speed_y)
        elif self.direction == 'left':
            self.rect.left = max(self.target_x, self.rect.left - self.speed_x)
        elif self.direction == 'right':
            self.rect.left = min(self.target_x, self.rect.left + self.speed_x)
        
        if (self.direction in ['down', 'up'] and self.rect.top == self.target_y) or (self.direction in ['left', 'right'] and self.rect.left == self.target_x):
            self.fixed = True