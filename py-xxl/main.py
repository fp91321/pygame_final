import os
import sys
import time
import pygame
import random

# Game Configuration
WIDTH, HEIGHT = 800, 800
GRID_COUNT = 8
GRID_SIZE = 70
XMARGIN = (WIDTH - GRID_SIZE * GRID_COUNT) // 2
YMARGIN = (HEIGHT - GRID_SIZE * GRID_COUNT) // 2
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FPS = 60

# Puzzle Class
class Puzzle(pygame.sprite.Sprite):
    def __init__(self, img_path, size, position, down_offset):
        super().__init__()
        self.image = pygame.transform.smoothscale(pygame.image.load(img_path), size)
        self.rect = self.image.get_rect(topleft=position)
        self.target_pos = (position[0], position[1] + down_offset)
        self.type = os.path.splitext(os.path.basename(img_path))[0]
        self.fixed = False
        self.speed = 10
        self.direction = 'down'

    def move(self):
        if not self.fixed:
            if self.direction == 'down':
                self.rect.y += self.speed
                if self.rect.y >= self.target_pos[1]:
                    self.rect.y = self.target_pos[1]
                    self.fixed = True

    def set_position(self, position):
        self.rect.topleft = position

# Game Class
class Game:
    def __init__(self, screen, font, gem_imgs):
        self.screen = screen
        self.font = font
        self.gem_imgs = gem_imgs
        self.reset_game()

    def start(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_events()
            self.update_game_state()
            self.draw_game()
            pygame.display.update()
            clock.tick(FPS)

    def reset_game(self):
        self.score = 0
        self.remaining_time = 30
        self.generate_grid()

    def generate_grid(self):
        while True:
            self.gems_group = pygame.sprite.Group()
            self.grid = [[self.create_gem(x, y) for y in range(GRID_COUNT)] for x in range(GRID_COUNT)]
            if not self.find_matches():
                break

    def create_gem(self, x, y):
        position = (XMARGIN + x * GRID_SIZE, YMARGIN + y * GRID_SIZE - GRID_COUNT * GRID_SIZE)
        gem = Puzzle(random.choice(self.gem_imgs), (GRID_SIZE, GRID_SIZE), position, GRID_COUNT * GRID_SIZE)
        self.gems_group.add(gem)
        return gem

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update_game_state(self):
        # Update gem movements
        for gem in self.gems_group:
            gem.move()

    def draw_game(self):
        self.screen.fill((127, 127, 127))
        self.draw_grid()
        self.gems_group.draw(self.screen)
        self.draw_score()
        self.draw_timer()

    def draw_grid(self):
        for x in range(GRID_COUNT):
            for y in range(GRID_COUNT):
                rect = pygame.Rect(XMARGIN + x * GRID_SIZE, YMARGIN + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, (255, 165, 0), rect, 1)

    def draw_score(self):
        score_surf = self.font.render(f'Score: {self.score}', True, (85, 65, 0))
        self.screen.blit(score_surf, (30, 15))

    def draw_timer(self):
        timer_surf = self.font.render(f'Time Left: {self.remaining_time}s', True, (75, 205, 255))
        self.screen.blit(timer_surf, (WIDTH - 220, 15))

    def find_matches(self):
        # Check for matches in the grid (return True if matches exist)
        return False

# Initialize Game
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('2024 PyGame Final Project')
    font = pygame.font.Font(os.path.join(ROOT_DIR, 'resources/simsun.ttc'), 25)
    gem_imgs = [os.path.join(ROOT_DIR, f'resources/images/gem{i}.png') for i in range(1, 8)]

    game = Game(screen, font, gem_imgs)
    while True:
        game.start()
        game.reset_game()

if __name__ == '__main__':
    main()
