import os
import sys
import time
import pygame
import random
from typing import Tuple, List, Dict, Union, Optional
from setting import GameConfig

# 界面管理類
class UIManager:
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        self.screen = screen
        self.font = font
        self.load_images()

    def load_images(self) -> None:
        """載入遊戲需要的圖片"""
        self.final_building_img = pygame.image.load(os.path.join(GameConfig.ROOTDIR, "resources/images/final_building.png"))
        self.final_building_img = pygame.transform.smoothscale(self.final_building_img, (400, 600))
        self.background = pygame.image.load(os.path.join(GameConfig.ROOTDIR, 'resources/images/game_background.JPG'))
        self.background = pygame.transform.scale(self.background, (GameConfig.WIDTH, GameConfig.HEIGHT))
        
    def draw_background(self) -> None:
        """繪製背景"""
        self.screen.blit(self.background, (0, 0))

    def draw_score(self, score: int) -> None:
        """繪製分數"""
        score_render = self.font.render(f'Score:{score}', 1, (45, 255, 245))
        self.screen.blit(score_render, (20, GameConfig.HEIGHT-40))

    def draw_level(self, level: int) -> None:
        """繪製關卡信息"""
        level_text = self.font.render(f'Level: {level}', True, (255, 255, 255))
        self.screen.blit(level_text, (20, 15))

    def draw_target(self, target: int) -> None:
        """繪製目標分數"""
        target_text = self.font.render(f'Target: {target}', True, (255, 255, 255))
        self.screen.blit(target_text, (GameConfig.WIDTH - 190, 15))

    def draw_timer(self, remaining_time: int) -> None:
        """繪製剩餘時間"""
        timer_text = self.font.render(f'Time: {remaining_time}', 1, (55, 205, 255))
        rect = timer_text.get_rect()
        rect.left, rect.top = (GameConfig.WIDTH-180, GameConfig.HEIGHT-40)
        self.screen.blit(timer_text, rect)

    def draw_gem_count(self, gem_count: Dict[int, int], gem_imgs: List[str]) -> None:
        """繪製寶石消除計數及其圖片"""
        y_offset = 100  # 起始的 y 座標
        x_offset = 20   # 起始的 x 座標
        spacing = 50    # 每種寶石的間距
        gem_size = 30   # 寶石圖片大小

        for gem_type, count in gem_count.items():
            # 載入並縮放寶石圖片
            gem_image = pygame.image.load(gem_imgs[gem_type - 1])
            gem_image = pygame.transform.scale(gem_image, (gem_size, gem_size))
            
            # 繪製寶石圖片
            self.screen.blit(gem_image, (x_offset, y_offset))

            # 繪製消除計數
            count_text = self.font.render(str(count), True, (255, 255, 255))
            self.screen.blit(count_text, (x_offset + gem_size + 10, y_offset))

            # 更新下一個寶石的位置
            y_offset += spacing

    def draw_grids(self) -> None:
        """繪製網格"""
        for x in range(GameConfig.NUMGRID):
            for y in range(GameConfig.NUMGRID):
                rect = pygame.Rect((
                    GameConfig.XMARGIN + x * GameConfig.GRIDSIZE,
                    GameConfig.YMARGIN + y * GameConfig.GRIDSIZE,
                    GameConfig.GRIDSIZE,
                    GameConfig.GRIDSIZE
                ))
                self.draw_block(rect, color=(255, 165, 0), size=1)

    def draw_block(self, block: pygame.Rect, color: Tuple[int, int, int] = (255, 0, 0), size: int = 2) -> None:
        """繪製方塊邊框"""
        pygame.draw.rect(self.screen, color, block, size)

    def draw_building_progress(self, score: int, target_score: int) -> None:
        """繪製建築進度"""
        ratio = min(max(score / target_score, 0), 1)
        image_width, image_height = self.final_building_img.get_size()
        cropped_height = int(image_height * ratio)
        if cropped_height > 0:
            cropped_image = self.final_building_img.subsurface(
                (0, image_height - cropped_height, image_width, cropped_height)
            )
            cropped_pos = (GameConfig.WIDTH - 280, GameConfig.HEIGHT // 2 + (300 - cropped_height))
            self.screen.blit(cropped_image, cropped_pos)