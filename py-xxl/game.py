import os
import sys
import time
import pygame
import random
from typing import Tuple, List, Dict, Union, Optional
from puzzle import Puzzle
from setting import GameConfig
from UI import UIManager
from score import ScoreManager
from sound import SoundManager
from bomb import Bomb

# 定義常用的類型
Position = Tuple[int, int]
Size = Tuple[int, int]

# 遊戲類
class Game:
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, gem_imgs: List[str]):
        self.ui_manager = UIManager(screen, font)
        self.score_manager = ScoreManager()
        self.sound_manager = SoundManager(GameConfig.ROOTDIR)
        self.gem_imgs = gem_imgs
        self.level = 1
        self.show_tutorial = True
        self.gem_count = {i: 0 for i in range(1, len(gem_imgs) + 1)}
        self.reset()

    def reset(self) -> None:
        """重置遊戲狀態"""
        # 測試佈局
        test_layout = [
            [1, 1, 2, 1, 3, 4, 5, 6, 1, 1],
            [4, 4, 1, 4, 4, 3, 5, 6, 5, 1],
            [5, 5, 3, 5, 1, 3, 4, 2, 1, 4],
            [1, 2, 5, 4, 6, 4, 1, 3, 4, 1],
            [2, 3, 5, 5, 1, 4, 5, 4, 3, 1],
            [3, 3, 2, 4, 5, 5, 6, 6, 1, 2],
            [6, 6, 3, 6, 1, 2, 1, 4, 5, 1],
            [1, 1, 2, 1, 4, 5, 1, 3, 4, 1],
            [5, 4, 3, 3, 5, 5, 4, 1, 2, 2],
            [3, 3, 5, 3, 3, 1, 1, 3, 1, 1]
        ]

        self.all_gems = []
        self.gems_group = pygame.sprite.Group()
        
        for x in range(GameConfig.NUMGRID):
            self.all_gems.append([])
            for y in range(GameConfig.NUMGRID):
                gem_type = test_layout[y][x] if y < len(test_layout) and x < len(test_layout[0]) else random.randint(1, 6)
                gem = Puzzle(
                    img_path=self.gem_imgs[gem_type - 1],
                    size=(GameConfig.GRIDSIZE, GameConfig.GRIDSIZE),
                    position=[GameConfig.XMARGIN + x * GameConfig.GRIDSIZE, GameConfig.YMARGIN + y * GameConfig.GRIDSIZE],
                    downlen=0
                )
                self.all_gems[x].append(gem)
                self.gems_group.add(gem)

        self.score_manager.score = 0
        self.remaining_time = 40

    def start(self, level: int = 1) -> int:
        """開始遊戲"""
        if self.show_tutorial:
            self.show_tutorial_screen()

        clock = pygame.time.Clock()
        overall_moving = True
        individual_moving = False
        self.level = level
        self.target_score = self.score_manager.get_level_target(level)
        # 根據關卡調整時間
        self.remaining_time = max(200 - (level - 1) * 60, 60)  # 每關減少60秒，但最少保持120秒
        gem_selected_xy = None
        gem_selected_xy2 = None
        swap_again = False
        add_score = 0
        time_pre = int(time.time())

        while True:
            self.ui_manager.draw_background()
            
            # 檢查是否達到目標分數
            if self.score_manager.score >= self.target_score:
                return self.score_manager.score

            # 處理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not (overall_moving or individual_moving or add_score):
                        position = pygame.mouse.get_pos()
                        if gem_selected_xy is None:
                            gem_selected_xy = self.check_selected(position)
                        else:
                            gem_selected_xy2 = self.check_selected(position)
                            if gem_selected_xy2:
                                if self.swap_gems(gem_selected_xy, gem_selected_xy2):
                                    individual_moving = True
                                    swap_again = False
                                else:
                                    gem_selected_xy = None

            # 更新遊戲狀態
            if overall_moving:
                overall_moving = not self.drop_gems()
                if not overall_moving:
                    res_match = self.check_matches()
                    add_score = self.remove_matched(res_match)
                    if add_score > 0:
                        overall_moving = True

            if individual_moving:
                gem1 = self.get_gem_by_pos(*gem_selected_xy)
                gem2 = self.get_gem_by_pos(*gem_selected_xy2)
                gem1.move()
                gem2.move()
                if gem1.fixed and gem2.fixed:
                    res_match = self.check_matches()
                    if res_match[0] == 0 and not swap_again:
                        swap_again = True
                        self.swap_gems(gem_selected_xy, gem_selected_xy2)
                    else:
                        add_score = self.remove_matched(res_match)
                        overall_moving = True
                        individual_moving = False
                        gem_selected_xy = None
                        gem_selected_xy2 = None

            # 更新時間
            self.remaining_time -= (int(time.time()) - time_pre)
            time_pre = int(time.time())

            # 繪製遊戲界面
            self.ui_manager.draw_grids()
            self.gems_group.draw(self.ui_manager.screen)
            if gem_selected_xy:
                self.ui_manager.draw_block(self.get_gem_by_pos(*gem_selected_xy).rect)

            # 更新界面顯示
            self.ui_manager.draw_building_progress(self.score_manager.score, self.target_score)
            self.ui_manager.draw_timer(self.remaining_time)
            self.ui_manager.draw_score(self.score_manager.score)
            self.ui_manager.draw_level(self.level)
            self.ui_manager.draw_target(self.target_score)
            self.ui_manager.draw_gem_count(self.gem_count, self.gem_imgs)

            if self.remaining_time <= 0:
                return self.score_manager.score

            pygame.display.update()
            clock.tick(GameConfig.FPS)

    def show_tutorial_screen(self) -> None:
        """顯示教學畫面"""
        self.ui_manager.draw_tutorial_background()
        """
        # 教學內容
        title_text = self.ui_manager.font.render("Welcome to Icehappy Game!", True, (255, 255, 0))
        self.ui_manager.screen.blit(title_text, (GameConfig.WIDTH // 2 - title_text.get_width() // 2, 100))
        
        instruction_lines = [
            "Match 3 or more gems to score points.",
            "Click 2 adjacent gems to swap their positions.",
            "Complete the target score to the next level.",
            "Click anywhere to start the game. Good luck!"
        ]

        for i, line in enumerate(instruction_lines):
            instruction_text = self.ui_manager.font.render(line, True, (255, 255, 255))
            self.ui_manager.screen.blit(instruction_text, 
                (GameConfig.WIDTH // 2 - instruction_text.get_width() // 2, 200 + i * 50))
        """
        pygame.display.update()

        # 等待玩家點擊
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    self.show_tutorial = False

    def check_selected(self, position: Position) -> Optional[List[int]]:
        """檢查是否點擊到寶石"""
        for x in range(GameConfig.NUMGRID):
            for y in range(GameConfig.NUMGRID):
                if self.get_gem_by_pos(x, y).rect.collidepoint(*position):
                    return [x, y]
        return None

    def get_gem_by_pos(self, x: int, y: int) -> Puzzle:
        """根據坐標獲取寶石對象"""
        return self.all_gems[x][y]

    def swap_gems(self, pos1: List[int], pos2: List[int]) -> bool:
        """交換兩個寶石的位置"""
        margin = pos1[0] - pos2[0] + pos1[1] - pos2[1]
        if abs(margin) != 1:
            return False

        gem1 = self.get_gem_by_pos(*pos1)
        gem2 = self.get_gem_by_pos(*pos2)

        # 檢查是否有炸彈參與交換
        if isinstance(gem1, Bomb) or isinstance(gem2, Bomb):
            # 如果有炸彈，先進行交換
            self.all_gems[pos2[0]][pos2[1]] = gem1
            self.all_gems[pos1[0]][pos1[1]] = gem2

            # 處理炸彈爆炸
            if isinstance(gem1, Bomb):
                self.process_bomb_explosion(pos2[0], pos2[1])
            else:
                self.process_bomb_explosion(pos1[0], pos1[1])

            return True

        # 正常的寶石交換邏輯
        if pos1[0] - pos2[0] == 1:
            gem1.direction = 'left'
            gem2.direction = 'right'
        elif pos1[0] - pos2[0] == -1:
            gem2.direction = 'left'
            gem1.direction = 'right'
        elif pos1[1] - pos2[1] == 1:
            gem1.direction = 'up'
            gem2.direction = 'down'
        elif pos1[1] - pos2[1] == -1:
            gem2.direction = 'up'
            gem1.direction = 'down'

        # 設置目標位置
        gem1.target_x = gem2.rect.left
        gem1.target_y = gem2.rect.top
        gem2.target_x = gem1.rect.left
        gem2.target_y = gem1.rect.top
        gem1.fixed = False
        gem2.fixed = False

        # 更新網格數據
        self.all_gems[pos2[0]][pos2[1]] = gem1
        self.all_gems[pos1[0]][pos1[1]] = gem2

        return True

    def drop_gems(self) -> bool:
        """處理寶石下落，所有寶石同時下落"""
        all_fixed = True
        # 同時移動所有未固定的寶石
        for x in range(GameConfig.NUMGRID):
            for y in range(GameConfig.NUMGRID):
                gem = self.get_gem_by_pos(x, y)
                if not gem.fixed:
                    gem.move()
                    all_fixed = False
        return all_fixed

    def check_matches(self) -> List[Union[int, List[int]]]:
        """檢查是否有可消除的寶石"""
        # 先檢查特殊形狀
        for x in range(GameConfig.NUMGRID):
            for y in range(GameConfig.NUMGRID):
                # 跳過無效的檢查位置
                if not self.is_valid_pos(x, y):
                    continue
                    
                current_type = self.get_gem_by_pos(x, y).type

                # 檢查T_UP (sss
                #           s
                #           s)
                if (self.is_valid_pos(x + 2, y) and self.is_valid_pos(x + 1, y + 2)):
                    try:
                        if (all(self.get_gem_by_pos(x + i, y).type == current_type for i in range(3)) and
                            self.get_gem_by_pos(x + 1, y + 1).type == current_type and
                            self.get_gem_by_pos(x + 1, y + 2).type == current_type):
                            return [3, x, y, 'T_UP']
                    except IndexError:
                        continue

                # 檢查T_DOWN ( s
                #             s
                #           sss)
                if (self.is_valid_pos(x + 2, y + 2) and self.is_valid_pos(x + 1, y)):
                    try:
                        if (self.get_gem_by_pos(x + 1, y).type == current_type and
                            self.get_gem_by_pos(x + 1, y + 1).type == current_type and
                            all(self.get_gem_by_pos(x + i, y + 2).type == current_type for i in range(3))):
                            return [3, x, y, 'T_DOWN']
                    except IndexError:
                        continue

                # 檢查T_LEFT (s
                #           sss
                #           s)
                if (self.is_valid_pos(x, y + 2) and self.is_valid_pos(x + 2, y + 1)):
                    try:
                        if (self.get_gem_by_pos(x, y).type == current_type and
                            all(self.get_gem_by_pos(x + i, y + 1).type == current_type for i in range(3)) and
                            self.get_gem_by_pos(x, y + 2).type == current_type):
                            return [3, x, y, 'T_LEFT']
                    except IndexError:
                        continue

                # 檢查T_RIGHT (  s
                #             sss
                #               s)
                if (self.is_valid_pos(x + 2, y + 2) and self.is_valid_pos(x + 2, y)):
                    try:
                        if (self.get_gem_by_pos(x + 2, y).type == current_type and
                            all(self.get_gem_by_pos(x + i, y + 1).type == current_type for i in range(3)) and
                            self.get_gem_by_pos(x + 2, y + 2).type == current_type):
                            return [3, x, y, 'T_RIGHT']
                    except IndexError:
                        continue

                # 檢查L_UP (s
                #          s
                #         sss)
                if (self.is_valid_pos(x, y + 2) and self.is_valid_pos(x + 2, y + 2)):
                    try:
                        if (self.get_gem_by_pos(x, y).type == current_type and
                            self.get_gem_by_pos(x, y + 1).type == current_type and
                            all(self.get_gem_by_pos(x + i, y + 2).type == current_type for i in range(3))):
                            return [4, x, y, 'L_UP']
                    except IndexError:
                        continue

                # 檢查L_DOWN (sss
                #             s
                #             s)
                if (self.is_valid_pos(x + 2, y) and self.is_valid_pos(x, y + 2)):
                    try:
                        if (all(self.get_gem_by_pos(x + i, y).type == current_type for i in range(3)) and
                            self.get_gem_by_pos(x, y + 1).type == current_type and
                            self.get_gem_by_pos(x, y + 2).type == current_type):
                            return [4, x, y, 'L_DOWN']
                        
                    except IndexError:
                        continue

                # 檢查L_LEFT (  s
                #              s
                #            sss)
                if (self.is_valid_pos(x + 2, y) and self.is_valid_pos(x, y+2)):
                    try:
                        tmp_current_type=self.get_gem_by_pos(x+2 , y).type
                        if (self.get_gem_by_pos(x+2 , y).type == tmp_current_type and
                            self.get_gem_by_pos(x+2 , y +1).type == tmp_current_type and
                            all(self.get_gem_by_pos(x + i, y+2).type == tmp_current_type for i in range(3))):
                            return [4, x, y, 'L_LEFT']
                        
                    except IndexError:
                        continue

                # 檢查L_RIGHT (sss
                #               s
                #               s)
                if (self.is_valid_pos(x + 2, y + 2) and self.is_valid_pos(x + 2, y)):
                    try:
                        if (all(self.get_gem_by_pos(x + i, y).type == current_type for i in range(3)) and
                            self.get_gem_by_pos(x + 2, y + 1).type == current_type and
                            self.get_gem_by_pos(x + 2, y + 2).type == current_type):
                            return [4, x, y, 'L_RIGHT']
                    except IndexError:
                        continue

        # 檢查一般的直線消除
        max_match = [0, 0, 0, 0]  # [方向, 起點x, 起點y, 最大匹配長度]
        for x in range(GameConfig.NUMGRID):
            for y in range(GameConfig.NUMGRID):
                if not self.is_valid_pos(x, y):
                    continue

                # 檢查橫向
                match_length = 1
                for i in range(1, 5):
                    if not self.is_valid_pos(x + i, y):
                        break
                    try:
                        if self.get_gem_by_pos(x, y).type == self.get_gem_by_pos(x + i, y).type:
                            match_length += 1
                        else:
                            break
                    except IndexError:
                        break
                if match_length >= 3 and match_length > max_match[3]:
                    max_match = [1, x, y, match_length]

                # 檢查縱向
                match_length = 1
                for i in range(1, 5):
                    if not self.is_valid_pos(x, y + i):
                        break
                    try:
                        if self.get_gem_by_pos(x, y).type == self.get_gem_by_pos(x, y + i).type:
                            match_length += 1
                        else:
                            break
                    except IndexError:
                        break
                if match_length >= 3 and match_length > max_match[3]:
                    max_match = [2, x, y, match_length]

        return max_match

    def _get_match_positions(self, res_match: List[Union[int, List[int]]]) -> List[Tuple[int, int]]:
        """獲取匹配位置列表"""
        positions = []
        base_x, base_y = res_match[1], res_match[2]
    
        if res_match[0] == 1:  # 橫向
            positions = [(x, base_y) for x in range(base_x, base_x + res_match[3])]
        elif res_match[0] == 2:  # 縱向
            positions = [(base_x, y) for y in range(base_y, base_y + res_match[3])]
        elif res_match[0] == 3:  # T型
            if res_match[3] == 'T_UP':  # sss
                #                         s
                #                         s
                positions = [
                    (base_x, base_y), (base_x + 1, base_y), (base_x + 2, base_y),  # 頂部橫排
                    (base_x + 1, base_y + 1),  # 中間
                    (base_x + 1, base_y + 2)   # 底部
                ]
            elif res_match[3] == 'T_DOWN':  #  s
                #                           s
                #                         sss
                positions = [
                    (base_x + 1, base_y),     # 頂部
                    (base_x + 1, base_y + 1),  # 中間
                    (base_x, base_y + 2), (base_x + 1, base_y + 2), (base_x + 2, base_y + 2)  # 底部橫排
                ]
            elif res_match[3] == 'T_LEFT':  # s
                #                          sss
                #                          s
                positions = [
                    (base_x, base_y),      # 頂部
                    (base_x, base_y + 1), (base_x + 1, base_y + 1), (base_x + 2, base_y + 1),  # 中間橫排
                    (base_x, base_y + 2)   # 底部
                ]
            elif res_match[3] == 'T_RIGHT':  #   s
                #                          sss
                #                            s
                positions = [
                    (base_x + 2, base_y),   # 頂部
                    (base_x, base_y + 1), (base_x + 1, base_y + 1), (base_x + 2, base_y + 1),  # 中間橫排
                    (base_x + 2, base_y + 2)  # 底部
                ]
        elif res_match[0] == 4:  # L型
            if res_match[3] == 'L_UP':  # s
                #                       s
                #                     sss
                positions = [
                    (base_x, base_y),     # 頂部
                    (base_x, base_y + 1),  # 中間
                    (base_x, base_y + 2), (base_x + 1, base_y + 2), (base_x + 2, base_y + 2)  # 底部橫排
                ]
            elif res_match[3] == 'L_DOWN':  # sss
                #                           s
                #                           s
                positions = [
                    (base_x, base_y), (base_x + 1, base_y), (base_x + 2, base_y),  # 頂部橫排
                    (base_x, base_y + 1),  # 中間
                    (base_x, base_y + 2)   # 底部
                ]
            elif res_match[3] == 'L_LEFT':  #   s
                #                            s
                #                          sss
                positions = [
                    (base_x + 2, base_y),     # 頂部
                    (base_x + 2, base_y + 1),  # 中間
                    (base_x, base_y + 2), (base_x + 1, base_y + 2), (base_x + 2, base_y + 2)  # 底部橫排
                ]
            elif res_match[3] == 'L_RIGHT':  # sss
                #                             s
                #                             s
                positions = [
                    (base_x, base_y), (base_x + 1, base_y), (base_x + 2, base_y),  # 頂部橫排
                    (base_x + 2, base_y + 1),  # 中間
                    (base_x + 2, base_y + 2)   # 底部
                ]

        return positions

    def remove_matched(self, res_match: List[Union[int, List[int]]]) -> int:
        """移除匹配的寶石並計算得分"""
        if res_match[0] == 0:
            return 0

        # 獲取匹配位置
        positions = self._get_match_positions(res_match)
        is_special = res_match[0] in [3, 4]  # 是否是特殊形狀（T型或L型）
        
        # 計算得分和播放音效
        if not is_special:  # 直線消除
            match_length = res_match[3]
            score = self.score_manager.add_score(match_length)
            self.sound_manager.play_match_sound(match_length)
        else:  # T型或L型消除
            score = self.score_manager.add_score(5)
            self.sound_manager.play_match_sound(5)

        # 移除寶石並更新計數
        for x, y in positions:
            gem = self.get_gem_by_pos(x, y)
            if gem and not isinstance(gem, Bomb):  # 不移除炸彈
                gem_type = int(''.join(filter(str.isdigit, gem.type)))
                self.gem_count[gem_type] += 1
                self.gems_group.remove(gem)
                self.all_gems[x][y] = None

        # 生成新的寶石
        self._generate_new_gems(positions)

        # 如果是特殊形狀消除，等所有寶石下落後創建炸彈
        if is_special:
            # 選擇中間位置放置炸彈
            bomb_x = sum(x for x, y in positions) // len(positions)
            bomb_y = sum(y for x, y in positions) // len(positions)

            # 等待所有寶石落下
            waiting = True
            while waiting:
                waiting = False
                for x in range(GameConfig.NUMGRID):
                    for y in range(GameConfig.NUMGRID):
                        gem = self.get_gem_by_pos(x, y)
                        if gem and not gem.fixed:
                            waiting = True
                            gem.move()

            # 創建炸彈
            self.create_bomb(bomb_x, bomb_y)

        return score
    
    def create_bomb(self, x: int, y: int) -> None:
        """在指定位置創建炸彈"""
        position = [
            GameConfig.XMARGIN + x * GameConfig.GRIDSIZE,
            GameConfig.YMARGIN + y * GameConfig.GRIDSIZE
        ]
        bomb = Bomb(position=position)

        # 移除原有的寶石
        original_gem = self.get_gem_by_pos(x, y)
        if original_gem:
            self.gems_group.remove(original_gem)

        # 添加炸彈
        self.gems_group.add(bomb)
        self.all_gems[x][y] = bomb
    
    def process_bomb_explosion(self, bomb_x: int, bomb_y: int) -> None:
        """處理炸彈爆炸效果，包括連鎖爆炸"""
        print(f"Processing bomb at ({bomb_x}, {bomb_y})")

        # 用於追蹤待處理的炸彈位置和所有受影響的位置
        bombs_to_process = [(bomb_x, bomb_y)]
        all_affected_positions = set()
        affected_gems = []  # 儲存所有受影響的寶石，以便按正確順序處理
        total_removed_count = 0

        # 第一階段：收集所有受影響的位置和寶石
        while bombs_to_process:
            current_bomb_x, current_bomb_y = bombs_to_process.pop(0)
            
            # 獲取當前炸彈影響範圍內的所有位置
            for dx in [1, 0, -1]:
                for dy in [-1, 0, 1]:
                    new_x, new_y = current_bomb_x + dx, current_bomb_y + dy
                    if self.is_valid_pos(new_x, new_y) and (new_x, new_y) not in all_affected_positions:
                        gem = self.get_gem_by_pos(new_x, new_y)
                        if gem:
                            affected_gems.append((new_x, new_y, gem))
                            all_affected_positions.add((new_x, new_y))
                            
                            if isinstance(gem, Bomb):
                                print(f"Found bomb at ({new_x}, {new_y})")
                                bombs_to_process.append((new_x, new_y))

        # 第二階段：按照由上到下、由左到右的順序處理寶石
        affected_gems.sort(key=lambda x: (x[1], x[0]))  # 先按y座標（行），再按x座標（列）排序
        
        # 處理每個受影響的寶石
        for x, y, gem in affected_gems:
            try:
                if not isinstance(gem, Bomb):
                    gem_type = int(''.join(filter(str.isdigit, gem.type)))
                    self.gem_count[gem_type] += 1
                    total_removed_count += 1
                
                # 移除當前寶石
                self.gems_group.remove(gem)
                self.all_gems[x][y] = None
                
            except ValueError:
                continue

        # 計算總分數
        score = self.score_manager.add_score(total_removed_count)

        # 根據消除數量播放音效
        if total_removed_count >= 5:
            self.sound_manager.play_match_sound(5)
        elif total_removed_count == 4:
            self.sound_manager.play_match_sound(4)
        elif total_removed_count == 3:
            self.sound_manager.play_match_sound(3)

        # 生成新的寶石
        self._generate_new_gems(list(all_affected_positions))
        
    
    def is_valid_pos(self, x: int, y: int) -> bool:
        """檢查位置是否在網格範圍內"""
        return 0 <= x < GameConfig.NUMGRID and 0 <= y < GameConfig.NUMGRID
    
    
    
    def generate_new_gems(self, res_match: List[Union[int, List[int]]]) -> None:
        """生成新的寶石"""
        def remove_gem(x: int, y: int) -> None:
            """移除指定位置的寶石"""
            gem = self.get_gem_by_pos(x, y)
            self.gems_group.remove(gem)
            self.all_gems[x][y] = None

        def create_new_gem(x: int, position: Position, downlen: int) -> None:
            """創建新的寶石"""
            gem = Puzzle(
                img_path=random.choice(self.gem_imgs),
                size=(GameConfig.GRIDSIZE, GameConfig.GRIDSIZE),
                position=position,
                downlen=downlen
            )
            self.gems_group.add(gem)
            self.all_gems[x][0] = gem

        if res_match[0] in [1, 2]:  # 直線消除
            if res_match[0] == 1:  # 橫向消除
                # 移除匹配的寶石
                for x in range(res_match[1], res_match[1] + res_match[3]):
                    remove_gem(x, res_match[2])
                    
                # 上方的寶石下落
                for x in range(res_match[1], res_match[1] + res_match[3]):
                    for y in range(res_match[2] - 1, -1, -1):
                        if y >= 0:
                            gem = self.get_gem_by_pos(x, y)
                            gem.target_y += GameConfig.GRIDSIZE
                            gem.fixed = False
                            gem.direction = 'down'
                            self.all_gems[x][y + 1] = gem
                        else:
                            # 在頂部生成新寶石
                            create_new_gem(x, 
                                [GameConfig.XMARGIN + x * GameConfig.GRIDSIZE, 
                                 GameConfig.YMARGIN - GameConfig.GRIDSIZE], 
                                GameConfig.GRIDSIZE)

            else:  # 縱向消除
                # 移除匹配的寶石
                for y in range(res_match[2], res_match[2] + res_match[3]):
                    remove_gem(res_match[1], y)
                
                # 創建新寶石
                for i in range(res_match[3]):
                    create_new_gem(res_match[1], 
                        [GameConfig.XMARGIN + res_match[1] * GameConfig.GRIDSIZE, 
                         GameConfig.YMARGIN - (i + 1) * GameConfig.GRIDSIZE], 
                        (i + 1) * GameConfig.GRIDSIZE)

        elif res_match[0] == 3:  # T型消除
            positions = []
            if res_match[3] == 'T_DOWN':  # 正T
                positions = [
                    (res_match[1], res_match[2]),      # 左上
                    (res_match[1] + 1, res_match[2]),  # 中上
                    (res_match[1] + 2, res_match[2]),  # 右上
                    (res_match[1] + 1, res_match[2] + 1)  # 中下
                ]
            elif res_match[3] == 'T_UP':  # 倒T
                positions = [
                    (res_match[1], res_match[2] + 1),      # 左下
                    (res_match[1] + 1, res_match[2]),      # 中上
                    (res_match[1] + 1, res_match[2] + 1),  # 中下
                    (res_match[1] + 2, res_match[2] + 1)   # 右下
                ]
            elif res_match[3] == 'T_RIGHT':  # 右T
                positions = [
                    (res_match[1], res_match[2]),      # 左上
                    (res_match[1], res_match[2] + 1),  # 左中
                    (res_match[1], res_match[2] + 2),  # 左下
                    (res_match[1] + 1, res_match[2] + 1)  # 右中
                ]
            elif res_match[3] == 'T_LEFT':  # 左T
                positions = [
                    (res_match[1] + 1, res_match[2]),      # 右上
                    (res_match[1] + 1, res_match[2] + 1),  # 右中
                    (res_match[1] + 1, res_match[2] + 2),  # 右下
                    (res_match[1], res_match[2] + 1)       # 左中
                ]

            # 移除匹配的寶石
            for x, y in positions:
                remove_gem(x, y)

            # 處理每一列的下落
            affected_columns = set(x for x, y in positions)
            for x in affected_columns:
                # 找出這一列中最高的被消除的位置
                min_y = min(y for px, y in positions if px == x)
                # 處理這一列上方的所有寶石
                empty_spaces = sum(1 for px, y in positions if px == x)
                for y in range(min_y - 1, -1, -1):
                    gem = self.get_gem_by_pos(x, y)
                    gem.target_y += GameConfig.GRIDSIZE * empty_spaces
                    gem.fixed = False
                    gem.direction = 'down'
                    self.all_gems[x][y + empty_spaces] = gem

                # 在頂部生成新寶石
                for i in range(empty_spaces):
                    create_new_gem(x, 
                        [GameConfig.XMARGIN + x * GameConfig.GRIDSIZE, 
                         GameConfig.YMARGIN - (i + 1) * GameConfig.GRIDSIZE], 
                        (i + 1) * GameConfig.GRIDSIZE)

        elif res_match[0] == 4:  # L型消除
            positions = [
                (res_match[1], res_match[2]),      # 左上
                (res_match[1] + 1, res_match[2]),  # 右上
                (res_match[1], res_match[2] + 1),  # 左中
                (res_match[1], res_match[2] + 2)   # 左下
            ]

            # 處理方式與 T 型相同
            for x, y in positions:
                remove_gem(x, y)

            affected_columns = set(x for x, y in positions)
            for x in affected_columns:
                min_y = min(y for px, y in positions if px == x)
                empty_spaces = sum(1 for px, y in positions if px == x)
                for y in range(min_y - 1, -1, -1):
                    gem = self.get_gem_by_pos(x, y)
                    gem.target_y += GameConfig.GRIDSIZE * empty_spaces
                    gem.fixed = False
                    gem.direction = 'down'
                    self.all_gems[x][y + empty_spaces] = gem

                for i in range(empty_spaces):
                    create_new_gem(x, 
                        [GameConfig.XMARGIN + x * GameConfig.GRIDSIZE, 
                         GameConfig.YMARGIN - (i + 1) * GameConfig.GRIDSIZE], 
                        (i + 1) * GameConfig.GRIDSIZE)
                                    
                                    
    def _generate_new_gems(self, removed_positions: List[Tuple[int, int]]) -> None:
        """生成新的寶石，修復掉落順序問題"""
        # 按列分組要處理的位置
        columns = {}
        for x, y in removed_positions:
            if x not in columns:
                columns[x] = []
            columns[x].append(y)

        # 處理每一列
        for x in columns:
            removed_ys = sorted(columns[x])  # 排序以確保從上到下處理
            
            # 1. 找出該列中所有需要下移的現有寶石
            moves = []  # 存儲需要移動的寶石信息：(from_y, to_y, gem)
            empty_slots = []  # 記錄所有空位
            
            # 從底部開始向上遍歷
            for y in range(GameConfig.NUMGRID - 1, -1, -1):
                if y in removed_ys:
                    empty_slots.append(y)
                elif self.all_gems[x][y] is not None and empty_slots:
                    # 將寶石移到最下面的空位
                    target_y = empty_slots.pop(0)
                    moves.append((y, target_y, self.all_gems[x][y]))
                    empty_slots.append(y)  # 當前位置變成空位

            # 2. 執行移動
            for from_y, to_y, gem in moves:
                # 更新寶石目標位置
                gem.target_y = GameConfig.YMARGIN + to_y * GameConfig.GRIDSIZE
                gem.fixed = False
                gem.direction = 'down'
                # 更新網格引用
                self.all_gems[x][to_y] = gem
                self.all_gems[x][from_y] = None

            # 3. 在頂部生成新寶石
            for i, empty_y in enumerate(empty_slots):
                # 計算起始位置，使其在畫面頂部上方
                start_y = GameConfig.YMARGIN - (i + 1) * GameConfig.GRIDSIZE
                target_y = GameConfig.YMARGIN + empty_y * GameConfig.GRIDSIZE
                
                # 創建新寶石
                new_gem = Puzzle(
                    img_path=random.choice(self.gem_imgs),
                    size=(GameConfig.GRIDSIZE, GameConfig.GRIDSIZE),
                    position=[
                        GameConfig.XMARGIN + x * GameConfig.GRIDSIZE,
                        start_y
                    ],
                    downlen=abs(target_y - start_y)
                )
                new_gem.target_y = target_y
                new_gem.fixed = False
                new_gem.direction = 'down'
                
                # 添加到遊戲中
                self.gems_group.add(new_gem)
                self.all_gems[x][empty_y] = new_gem