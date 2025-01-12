import os
import sys
import pygame
from typing import Tuple, List, Dict, Union, Optional
from setting import GameConfig
from game import Game

# 定義常用的類型
Position = Tuple[int, int]
Size = Tuple[int, int]

# 遊戲場景類
class GameScene:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((GameConfig.WIDTH, GameConfig.HEIGHT))
        pygame.display.set_caption('2024_PyGame_Final_Project')
        
        self.font = pygame.font.SysFont('Arial', 35, bold=True)
        self.font_end = pygame.font.SysFont('Arial', 50, bold=True)
        
        # 載入寶石圖片
        self.gem_imgs = [
            os.path.join(GameConfig.ROOTDIR, f'resources/images/gem{i}.png')
            for i in range(1, 8)
        ]
        
        self.game = Game(self.screen, self.font, self.gem_imgs)
        self.max_level = 3

    def show_start_screen(self) -> None:
        """顯示開始畫面"""
        bg_image = pygame.image.load(os.path.join(GameConfig.ROOTDIR, 'resources/images/background.JPG'))
        bg_image = pygame.transform.scale(bg_image, (GameConfig.WIDTH, GameConfig.HEIGHT))
        
        waiting = True
        while waiting:
            self.screen.blit(bg_image, (0, 0))
            
            start_text = self.font.render('Click anywhere to start the game!!', True, (105, 105, 100))
            start_rect = start_text.get_rect(center=(GameConfig.WIDTH // 2, GameConfig.HEIGHT - 80))
            self.screen.blit(start_text, start_rect)
            
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

    def show_level_transition(self, next_level: int, message: str) -> None:
        """顯示關卡過渡畫面，分兩個階段"""
        # 第一階段：顯示關卡背景
        bg_image = pygame.image.load(os.path.join(GameConfig.ROOTDIR, 'resources/images/level_background.jpg'))
        bg_image = pygame.transform.scale(bg_image, (GameConfig.WIDTH, GameConfig.HEIGHT))
        
        waiting_click = True
        while waiting_click:
            self.screen.blit(bg_image, (0, 0))
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    waiting_click = False

        # 第二階段：顯示分數調整訊息
        overlay = pygame.Surface((GameConfig.WIDTH, GameConfig.HEIGHT))
        overlay.fill((0, 0, 0))  # 黑色背景
        
        # 渲染分數調整訊息
        message_text = self.font.render(message, True, (255, 255, 255))
        message_rect = message_text.get_rect(center=(GameConfig.WIDTH // 2, GameConfig.HEIGHT // 2))
        
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(message_text, message_rect)
        
        pygame.display.update()
        pygame.time.wait(3000)  # 顯示3秒

    def show_end_screen(self, score: int) -> bool:
        """顯示遊戲結束畫面"""
        bg_image = pygame.image.load(os.path.join(GameConfig.ROOTDIR, 'resources/images/endgame.JPG'))
        bg_image = pygame.transform.scale(bg_image, (GameConfig.WIDTH, GameConfig.HEIGHT))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    return True
            
            self.screen.blit(bg_image, (0, 0))
            self.screen.blit(self.font_end.render('Game Over', True, (255, 200, 0)), (80, 140))
            self.screen.blit(self.font_end.render(f'Final Scores: {score}', True, (255, 200, 0)), (80, 260))
            self.screen.blit(self.font_end.render('Press R to Restart', True, (255, 200, 0)), (80, 380))
            pygame.display.update()

    def show_victory_screen(self, score: int) -> None:
        """顯示遊戲勝利畫面"""
        bg_image = pygame.image.load(os.path.join(GameConfig.ROOTDIR, 'resources/images/victory.JPG'))
        bg_image = pygame.transform.scale(bg_image, (GameConfig.WIDTH, GameConfig.HEIGHT))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
            
            self.screen.blit(bg_image, (0, 0))
            self.screen.blit(self.font_end.render('Congratulations!', True, (255, 255, 0)), (80, 140))
            self.screen.blit(self.font_end.render('You beat the game!', True, (255, 200, 0)), (80, 260))
            self.screen.blit(self.font_end.render(f'Final Scores: {score}', True, (255, 200, 0)), (80, 380))
            pygame.display.update()

    def run(self) -> None:
        """運行遊戲"""
        self.show_start_screen()
        
        level = 1
        while level <= self.max_level:
            # 開始遊戲
            score = self.game.start(level)
            print(f"Level {level} completed with score: {score}")  # 調試輸出
            print(f"Target score was: {self.game.score_manager.get_level_target(level)}")  # 調試輸出
            
            # 檢查是否達到目標分數
            if score >= self.game.score_manager.get_level_target(level):
                print(f"Advancing to next level")  # 調試輸出
                if level < self.max_level:
                    message = self.game.score_manager.adjust_score()
                    self.show_level_transition(level + 1, message)
                level += 1
                # 重置遊戲狀態但保持分數
                current_score = self.game.score_manager.score
                #self.game.reset()
                self.game.score_manager.score = current_score
            else:
                # 遊戲失敗，顯示結束畫面
                restart = self.show_end_screen(score)
                if restart:
                    level = 1
                    self.game.reset()
                else:
                    pygame.quit()
                    sys.exit()

        # 通關後顯示勝利畫面
        self.show_victory_screen(score)
        pygame.quit()
        sys.exit()