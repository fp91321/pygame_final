import os
import sys
import pygame
import math
import random
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
        """顯示關卡過渡畫面，包含卡片選擇效果"""
        # 創建時鐘
        clock = pygame.time.Clock()
        
        # 載入背景
        bg_image = pygame.image.load(os.path.join(GameConfig.ROOTDIR, 'resources/images/level_background.jpg'))
        bg_image = pygame.transform.scale(bg_image, (GameConfig.WIDTH, GameConfig.HEIGHT))
        
        # 卡片參數
        card_width = 320
        card_height = 500
        card_spacing = 150
        
        # 計算兩張卡片的位置
        total_width = (card_width * 2) + card_spacing
        start_x = (GameConfig.WIDTH - total_width) // 2
        start_y = (GameConfig.HEIGHT - card_height) // 2
        
        # 明確定義左右卡片的位置
        left_card = pygame.Rect(start_x, start_y, card_width, card_height)
        right_card = pygame.Rect(start_x + card_width + card_spacing, start_y, card_width, card_height)
        card_positions = [left_card, right_card]
        
        # 卡片狀態
        selected_card = -1
        animation_start = 0
        animation_duration = 1300  # 2秒
        is_animating = False
        
        animation_completed = False
        
        running = True
        othercard = (random.randint(-2, 5))*10

        while running:
            current_time = pygame.time.get_ticks()
            
            # 繪製背景
            self.screen.blit(bg_image, (0, 0))
            
            # 繪製提示文字
            if selected_card == -1:
                text = self.font.render("Please chose 1 card", True, (0, 25, 0))
            elif is_animating:
                text = self.font.render("Running...", True, (0, 5, 0))
            else:
                text = self.font.render("Click anywhere to continue", True, (0, 0, 0))  # 修改提示文字
            
            text_rect = text.get_rect(center=(GameConfig.WIDTH // 2, start_y - 90))
            self.screen.blit(text, text_rect)
            
            # 事件處理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if selected_card == -1:  # 如果還沒選擇卡片
                        mouse_pos = pygame.mouse.get_pos()
                        for i, card_rect in enumerate(card_positions):
                            if card_rect.collidepoint(mouse_pos):
                                selected_card = i
                                animation_start = current_time
                                is_animating = True
                    elif animation_completed:  # 如果動畫已完成，任何點擊都會結束循環
                        running = False
                        break
            
            # 繪製卡片
            for i, card_rect in enumerate(card_positions):
                color = (100, 100, 255) if selected_card == i else (40, 40, 50)
                
                # 如果正在動畫中，為選中的卡片添加動畫效果
                if is_animating and selected_card == i:
                    progress = (current_time - animation_start) / animation_duration
                    if progress <= 1:
                        # 簡單的縮放動畫
                        scale = 1 + (math.sin(progress * math.pi) * 0.2)
                        scaled_width = int(card_width * scale)
                        scaled_height = int(card_height * scale)
                        scaled_x = card_rect.centerx - (scaled_width // 2)
                        scaled_y = card_rect.centery - (scaled_height // 2)
                        pygame.draw.rect(self.screen, color, (scaled_x, scaled_y, scaled_width, scaled_height))
                    else:
                        is_animating = False
                        show_result = True
                        animation_completed = True
                else:
                    pygame.draw.rect(self.screen, color, card_rect)
                
                # 繪製卡片內容
                if animation_completed:
                    if i == selected_card:
                        card_text = self.font.render("You choose this card", True, (255, 255, 255))
                    else:
                        
                        card_text = self.font.render(f"{othercard}!", True, (105, 105, 105))
                else:
                    card_text = self.font.render("Chance or Destiny", True, (255, 255, 255))
                
                text_rect = card_text.get_rect(center=card_rect.center)
                self.screen.blit(card_text, text_rect)
            
            # 更新顯示
            pygame.display.flip()
            
            # 限制幀率
            clock.tick(60)
        
        # 顯示分數調整訊息
        overlay = pygame.Surface((GameConfig.WIDTH, GameConfig.HEIGHT))
        overlay.fill((0, 0, 0))
        
        message_text = self.font.render(message, True, (255, 255, 255))
        message_rect = message_text.get_rect(center=(GameConfig.WIDTH // 2, GameConfig.HEIGHT // 2))
        
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(message_text, message_rect)
        othercard = (random.randint(-2, 5))*10
        pygame.display.update()
        pygame.time.wait(2500)  # 顯示3秒

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
            self.screen.blit(self.font_end.render('Congratulations!', True, (5, 25, 0)), (80, 140))
            self.screen.blit(self.font_end.render('You beat the game!', True, (5, 20, 0)), (80, 260))
            self.screen.blit(self.font_end.render(f'Final Scores: {score}', True, (85, 180, 80)), (80, 380))
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