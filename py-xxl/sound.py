import os
import pygame
from typing import Tuple, List, Dict, Union, Optional

class SoundManager:
    def __init__(self, rootdir: str):
        # 載入音效
        self.match3_sound = pygame.mixer.Sound(os.path.join(rootdir, 'resources/sounds/match3.mp3'))
        self.match4_sound = pygame.mixer.Sound(os.path.join(rootdir, 'resources/sounds/match4.mp3'))
        self.match5_sound = pygame.mixer.Sound(os.path.join(rootdir, 'resources/sounds/match5.mp3'))
    
    def play_match_sound(self, match_length: int) -> None:
        """根據消除長度播放對應音效"""
        if match_length == 3:
            self.match3_sound.set_volume(0.5)
            self.match3_sound.play()
        elif match_length == 4:
            self.match4_sound.set_volume(0.5)
            self.match4_sound.play()
        elif match_length >= 5:
            self.match5_sound.set_volume(0.7)
            self.match5_sound.play()