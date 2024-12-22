import os
import sys
import time
import pygame
import random

WIDTH = 800
HEIGHT = 800
NUMGRID = 10
GRIDSIZE = 60
XMARGIN = (WIDTH - GRIDSIZE * NUMGRID) // 2
YMARGIN = (HEIGHT - GRIDSIZE * NUMGRID) // 2
ROOTDIR = os.path.dirname(os.path.abspath(__file__))
FPS = 60

# 拼图类
class Puzzle(pygame.sprite.Sprite):
	def __init__(self, img_path, size, position, downlen, **kwargs):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(img_path)
		self.image = pygame.transform.smoothscale(self.image, size)
		self.rect = self.image.get_rect()
		self.rect.left, self.rect.top = position
		self.downlen = downlen
		self.target_x = position[0]
		self.target_y = position[1] + downlen
		self.type = img_path.split('/')[-1].split('.')[0]
		self.fixed = False
		self.speed_x = 8
		self.speed_y = 8
		self.direction = 'down'
	# Moves the block in the specified direction and stops it when reaching the target position
	def move(self):
		if self.direction == 'down':
			self.rect.top = min(self.target_y, self.rect.top+self.speed_y)
			if self.target_y == self.rect.top:
				self.fixed = True
		elif self.direction == 'up':
			self.rect.top = max(self.target_y, self.rect.top-self.speed_y)
			if self.target_y == self.rect.top:
				self.fixed = True
		elif self.direction == 'left':
			self.rect.left = max(self.target_x, self.rect.left-self.speed_x)
			if self.target_x == self.rect.left:
				self.fixed = True
		elif self.direction == 'right':
			self.rect.left = min(self.target_x, self.rect.left+self.speed_x)
			if self.target_x == self.rect.left:
				self.fixed = True
	# Returns the current coordinates of the block.
	def getPosition(self):
		return self.rect.left, self.rect.top
	# Updates the block's coordinates.
	def setPosition(self, position):
		self.rect.left, self.rect.top = position

# 游戏类
class Game():
	def __init__(self, screen, font, gem_imgs, **kwargs):
		self.screen = screen
		self.font = font
		self.gem_imgs = gem_imgs
		self.level = 1
		self.target_score = 100  # 初始目標分數，隨關卡調整
		self.reset()
		self.show_tutorial = True  # 新增屬性，判斷是否顯示教學畫面
		#加載音效
		self.match3_sound = pygame.mixer.Sound(os.path.join(ROOTDIR, 'resources/sounds/match3.mp3'))
		self.match4_sound = pygame.mixer.Sound(os.path.join(ROOTDIR, 'resources/sounds/match4.mp3'))
		self.match5_sound = pygame.mixer.Sound(os.path.join(ROOTDIR, 'resources/sounds/match5.mp3'))
	def showTutorial(self):
		# 教學內容
		self.screen.fill((0, 0, 0))
		title_text = self.font.render("Welcome to Icehappy Game!", True, (255, 255, 0))
		self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

		instruction_lines = [
			"Match 3 or more gems to score points.",
			"Click 2 adjacent gems to swap their positions.",
			"Complete the target score to the next level.",
			"Click anywhere to start the game. Good luck!"
		]

		for i, line in enumerate(instruction_lines):
			instruction_text = self.font.render(line, True, (255, 255, 255))
			self.screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, 200 + i * 50))

		pygame.display.update()

		# 等待玩家按下任意鍵
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					self.show_tutorial = False
					return
	#設置當前關卡的目標分數和遊戲參數。
	def setLevel(self, level):		
		self.level = level
		self.target_score = level * 100  # 每關目標分數遞增
		self.remaining_time = 30 - (level - 1) * 5  # 隨關卡減少時間，但保證最低值
		#self.gem_imgs = self.gem_imgs[:min(7, 3 + level)]  # 增加難度，隨關卡增加寶石種類
	# 开始游戏
	def start(self,level=1):
		clock = pygame.time.Clock()
		# 遍历整个游戏界面更新位置
		overall_moving = True
		# 指定某些对象个体更新位置
		individual_moving = False
		self.setLevel(level)
		print("current level:",level)
		gem_selected_xy = None
		gem_selected_xy2 = None
		swap_again = False
		add_score = 0

		time_pre = int(time.time())
		# 顯示教學畫面
		if self.show_tutorial:
			self.showTutorial()
		
		# 游戏主循环
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
					pygame.quit()
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONUP:
					if (not overall_moving) and (not individual_moving) and (not add_score):
						position = pygame.mouse.get_pos()
						if gem_selected_xy is None:
							gem_selected_xy = self.checkSelected(position)
						else:
							gem_selected_xy2 = self.checkSelected(position)
							if gem_selected_xy2:
								if self.swapGem(gem_selected_xy, gem_selected_xy2):
									individual_moving = True
									swap_again = False
								else:
									gem_selected_xy = None
			if overall_moving:
				overall_moving = not self.dropGems(0, 0)
				# 移动一次可能拼出多个 3 连块
				if not overall_moving:
					res_match = self.isMatch()
					add_score = self.removeMatched(res_match)
					if add_score > 0:
						overall_moving = True
			if individual_moving:
				gem1 = self.getGemByPos(*gem_selected_xy)
				gem2 = self.getGemByPos(*gem_selected_xy2)
				gem1.move()
				gem2.move()
				if gem1.fixed and gem2.fixed:
					res_match = self.isMatch()
					if res_match[0] == 0 and not swap_again:
						swap_again = True
						self.swapGem(gem_selected_xy, gem_selected_xy2)
					else:
						add_score = self.removeMatched(res_match)
						overall_moving = True
						individual_moving = False
						gem_selected_xy = None
						gem_selected_xy2 = None
			self.screen.fill((10,127,127))
			self.drawGrids()
			self.gems_group.draw(self.screen)
			if gem_selected_xy:
				self.drawBlock(self.getGemByPos(*gem_selected_xy).rect)
			if add_score:
				self.drawAddScore(add_score)
				add_score_showtimes = 5

			self.remaining_time -= (int(time.time()) - time_pre)
			time_pre = int(time.time())
			self.showRemainingTime()
			self.drawScore()
			self.drawLevel()
			self.drawTarget()
			if self.remaining_time <= 0:
				return self.score
			pygame.display.update()
			clock.tick(FPS)
	# 初始化
	"""
	def reset(self):
		# 随机生成各个块
		while True:
			self.all_gems = []
			self.gems_group = pygame.sprite.Group()
			for x in range(NUMGRID):
				self.all_gems.append([])
				for y in range(NUMGRID):
					gem = Puzzle(
						img_path=random.choice(self.gem_imgs), 
						size=(GRIDSIZE, GRIDSIZE), 
						position=[XMARGIN+x*GRIDSIZE, YMARGIN+y*GRIDSIZE-NUMGRID*GRIDSIZE], 
						downlen=NUMGRID*GRIDSIZE
						)
					self.all_gems[x].append(gem)
					self.gems_group.add(gem)
			if self.isMatch()[0] == 0:
				break
		# 得分
		self.score = 0
		# 拼出一个的奖励
		self.reward = 10
		# 设置总时间
		self.remaining_time = 300
	
	"""
	def reset(self):
		# 固定生成測試佈局
		self.all_gems = []
		self.gems_group = pygame.sprite.Group()

		# 測試佈局的定義
		# 測試水平與垂直 3 消、4 消、5 消
		test_layout = [
			[1, 1, 2, 1, 3, 4, 5, 6, 1, 1],  # 水平 3 消（最上）
			[4, 4, 1, 4, 4, 3, 5, 6, 5, 1],  # 水平 4 消（第二行）
			[5, 5, 3, 5, 5, 3, 1, 2, 1, 4],  # 水平 5 消（第三行）
			[1, 2, 5, 4, 5, 1, 2, 3, 4, 1],  # 無消除
			[2, 3, 4, 5, 1, 5, 1, 4, 3, 1],  # 水平 3 消（第五行）
			[3, 3, 2, 4, 5, 5, 6, 1, 1, 2],  # 水平 3 消（第六行）
			[6, 6, 3, 6, 6, 2, 5, 4, 5, 1],  # 無消除
			[1, 1, 2, 1, 4, 5, 2, 3, 4, 5],  # 無消除
			[5, 4, 3, 3, 5, 5, 4, 1, 2, 1],  # 水平 4 消（第九行）
			[3, 3, 5, 3, 3, 1, 1, 3, 1, 1]   # 水平 3 消（第十行）
		]

		# 將測試佈局映射到 Puzzle 對象
		for x in range(NUMGRID):
			self.all_gems.append([])
			for y in range(NUMGRID):
				gem_type = test_layout[y][x] if y < len(test_layout) and x < len(test_layout[0]) else random.randint(1, 6)
				gem = Puzzle(
					img_path=self.gem_imgs[gem_type - 1],  # 根據 gem_type 選擇對應圖片
					size=(GRIDSIZE, GRIDSIZE),
					position=[XMARGIN + x * GRIDSIZE, YMARGIN + y * GRIDSIZE],
					downlen=0  # 無需下落動畫
				)
				self.all_gems[x].append(gem)
				self.gems_group.add(gem)

		# 初始化其他屬性
		self.score = 0
		self.reward = 10
		self.remaining_time = 3
	#根據關卡返回目標分數
	def getLevelTarget(self, level):		
		target_scores = {1: 100, 2: 150, 3: 200}  # 可以根據需求調整
		return target_scores.get(level, 300)
	#在遊戲界面顯示當前關卡
	def drawLevel(self):
		level_text = self.font.render(f'Level: {self.level}', True, (255, 255, 255))
		self.screen.blit(level_text, (20, 15))
	# 显示剩余时间
	def showRemainingTime(self):
		remaining_time_render = self.font.render('Timer: %ss' % str(self.remaining_time), 1, (55, 205, 255))
		rect = remaining_time_render.get_rect()
		rect.left, rect.top = (WIDTH-180, HEIGHT-40)
		self.screen.blit(remaining_time_render, rect)
	# 显示得分
	def drawScore(self):
		score_render = self.font.render('Score:'+str(self.score), 1, (45, 255, 245))
		rect = score_render.get_rect()
		self.screen.blit(score_render, (20, HEIGHT-40))
	# 显示目標得分
	def drawTarget(self):
		target_text = self.font.render(f'Target: {self.target_score}', True, (255, 255, 255))
		self.screen.blit(target_text, (WIDTH - 170, 15))
	# 显示加分
	def drawAddScore(self, add_score):
		score_render = self.font.render('+'+str(add_score), 1, (255, 255, 255))
		rect = score_render.get_rect()
		rect.left, rect.top = (5, 250)
		self.screen.blit(score_render, rect)
	# 生成新的拼图块
	def generateNewGems(self, res_match):
		if res_match[0] == 1:
			start = res_match[2]
			match_length = res_match[3]  # 匹配的長度（3、4 或 5）

			while start > -2:
				for each in range(res_match[1], res_match[1] + match_length):
					gem = self.getGemByPos(*[each, start])

					if start == res_match[2]:  # 移除匹配行的方塊
						self.gems_group.remove(gem)
						self.all_gems[each][start] = None
					elif start >= 0:  # 已存在的方塊下移
						
						gem.target_y += GRIDSIZE
						gem.fixed = False
						gem.direction = 'down'
						self.all_gems[each][start + 1] = gem
					else:  # 超出範圍，生成新方塊
						gem = Puzzle(
							img_path=random.choice(self.gem_imgs),
							size=(GRIDSIZE, GRIDSIZE),
							position=[XMARGIN + each * GRIDSIZE, YMARGIN - GRIDSIZE],
							downlen=GRIDSIZE
						)
						self.gems_group.add(gem)
						self.all_gems[each][start + 1] = gem

				start -= 1

		elif res_match[0] == 2:
			start = res_match[2]
			length = res_match[3]  # 消除的垂直長度（3、4 或 5）
			while start > -length-1:  # 處理範圍擴展到 `-length-1`
				
				if start == res_match[2]:
					# 移除起始行的所有匹配方塊
					for each in range(0, length):
						gem = self.getGemByPos(*[res_match[1], start + each])
						self.gems_group.remove(gem)
						self.all_gems[res_match[1]][start + each] = None

				elif start >= 0:
					
					# 處理非初始行的方塊，讓它們掉落
					gem = self.getGemByPos(*[res_match[1], start])
					gem.target_y += GRIDSIZE * length  # 根據匹配長度動態移動
					gem.fixed = False
					gem.direction = 'down'
					self.all_gems[res_match[1]][start + length] = gem

				else:
					# 超出範圍，生成新方塊補充
					gem = Puzzle(
						img_path=random.choice(self.gem_imgs), 
						size=(GRIDSIZE, GRIDSIZE), 
						position=[XMARGIN + res_match[1] * GRIDSIZE, YMARGIN + start * GRIDSIZE],
						downlen=GRIDSIZE * length  # 動態指定掉落距離
					)
					self.gems_group.add(gem)
					self.all_gems[res_match[1]][start + length] = gem

				start -= 1
	# 移除匹配的元素
	def removeMatched(self, res_match):
		if res_match[0] > 0:
			match_length = res_match[3]  # 匹配的長度（3、4、5）
			
			# 設定分數倍率
			if match_length == 3:
				score_multiplier = 1  # 單倍分數
				self.match3_sound.play() 
				self.match3_sound.set_volume(0.5)
			elif match_length == 4:
				score_multiplier = 2  # 雙倍分數
				self.match4_sound.play()
				self.match4_sound.set_volume(0.5)
			elif match_length >= 5:
				score_multiplier = 4  # 四倍分數
				self.match5_sound.play()
				self.match5_sound.set_volume(0.7)
			# 移除匹配元素並計算得分
			self.generateNewGems(res_match)
			match_score = self.reward * score_multiplier
			self.score += match_score
			return match_score  # 返回本次消除的得分
		return 0
	# 游戏界面的网格绘制
	def drawGrids(self):
		for x in range(NUMGRID):
			for y in range(NUMGRID):
				rect = pygame.Rect((XMARGIN+x*GRIDSIZE, YMARGIN+y*GRIDSIZE, GRIDSIZE, GRIDSIZE))
				self.drawBlock(rect, color=(255, 165, 0), size=1)
	# 画矩形 block 框
	def drawBlock(self, block, color=(255, 0, 0), size=2):
		pygame.draw.rect(self.screen, color, block, size)
	# 下落特效
	def dropGems(self, x, y):
		if not self.getGemByPos(x, y).fixed:
			self.getGemByPos(x, y).move()
		if x < NUMGRID-1:
			x += 1
			return self.dropGems(x, y)
		elif y < NUMGRID-1:
			x = 0
			y += 1
			return self.dropGems(x, y)
		else:
			return self.isFull()
	# 是否每个位置都有拼图块了
	def isFull(self):
		for x in range(NUMGRID):
			for y in range(NUMGRID):
				if not self.getGemByPos(x, y).fixed:
					return False
		return True
	# 检查有无拼图块被选中
	def checkSelected(self, position):
		for x in range(NUMGRID):
			for y in range(NUMGRID):
				if self.getGemByPos(x, y).rect.collidepoint(*position):
					return [x, y]
		return None
	# 是否有连续一样的三个块
	def isMatch(self):
		max_match = [0, 0, 0, 0]  # [方向 (1: 橫, 2: 直), 起點x, 起點y, 最大匹配長度]
		checked = [[False] * NUMGRID for _ in range(NUMGRID)]  # 用於標記是否已檢查

		for x in range(NUMGRID):
			for y in range(NUMGRID):
				if checked[x][y]:
					continue  # 跳過已檢查範圍

				# 檢查橫向連續
				match_length = 1
				for i in range(1, 5):
					if x + i < NUMGRID and self.getGemByPos(x, y).type == self.getGemByPos(x + i, y).type:
						match_length += 1
					else:
						break
				if match_length >= 3:
					if match_length > max_match[3]:
						print(match_length)
						max_match = [1, x, y, match_length]
					# 標記已檢查的格子
					for i in range(match_length):
						checked[x + i][y] = True

				# 檢查縱向連續
				match_length = 1
				for i in range(1, 5):
					if y + i < NUMGRID and self.getGemByPos(x, y).type == self.getGemByPos(x, y + i).type:
						match_length += 1
					else:
						break
				if match_length >= 3:
					if match_length > max_match[3]:
						print(match_length)
						max_match = [2, x, y, match_length]
					# 標記已檢查的格子
					for i in range(match_length):
						checked[x][y + i] = True

		return max_match
	# 根据坐标获取对应位置的拼图对象
	def getGemByPos(self, x, y):
		return self.all_gems[x][y]
	# 交换拼图
	def swapGem(self, gem1_pos, gem2_pos):
		margin = gem1_pos[0] - gem2_pos[0] + gem1_pos[1] - gem2_pos[1]
		if abs(margin) != 1:
			return False
		gem1 = self.getGemByPos(*gem1_pos)
		gem2 = self.getGemByPos(*gem2_pos)
		if gem1_pos[0] - gem2_pos[0] == 1:
			gem1.direction = 'left'
			gem2.direction = 'right'
		elif gem1_pos[0] - gem2_pos[0] == -1:
			gem2.direction = 'left'
			gem1.direction = 'right'
		elif gem1_pos[1] - gem2_pos[1] == 1:
			gem1.direction = 'up'
			gem2.direction = 'down'
		elif gem1_pos[1] - gem2_pos[1] == -1:
			gem2.direction = 'up'
			gem1.direction = 'down'
		gem1.target_x = gem2.rect.left
		gem1.target_y = gem2.rect.top
		gem1.fixed = False
		gem2.target_x = gem1.rect.left
		gem2.target_y = gem1.rect.top
		gem2.fixed = False
		self.all_gems[gem2_pos[0]][gem2_pos[1]] = gem1
		self.all_gems[gem1_pos[0]][gem1_pos[1]] = gem2
		return True
	def __repr__(self):
		return self.info

# 添加“开始游戏”页面
def showStartScreen(screen, font):
    # 加载背景图片
	bg_image_path = os.path.join(ROOTDIR, 'resources/images/background.JPG')  # 替换为实际图片名称
	bg_image = pygame.image.load(bg_image_path)    
	# 裁剪背景图片
	#bg_image = pygame.transform.rotate(bg_image, 90)
	bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT)) 
    
    
	while True:
		screen.blit(bg_image, (0, 0))  # 绘制背景图片
        
        # 游戏标题
		title_text = font.render('2024 PyGame Final Project', True, (255, 255, 255))
		title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
		screen.blit(title_text, title_rect)
        
        # 开始提示
		start_text = font.render('Click anywhere to start the game!!', True, (255, 255, 100))
		start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // (7/3)))
		screen.blit(start_text, start_rect)
        
		pygame.display.update()
        
        # 等待玩家点击
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				return
def showLevelTransition(screen, font, next_level):
	"""
	顯示關卡切換過渡畫面
	"""
	bg_color = (0, 0, 0)
	screen.fill(bg_color)
	
	transition_text = font.render(f'Level {next_level}', True, (255, 255, 255))
	transition_rect = transition_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
	screen.blit(transition_text, transition_rect)
	
	pygame.display.update()
	pygame.time.wait(3000)  # 等待3秒

def showEndScreen(screen, font_end, score):
	"""
	顯示遊戲結束畫面，返回是否重新開始遊戲的布林值
	"""
	bg_image_path = os.path.join(ROOTDIR, 'resources/images/endgame.JPG')  # 替換為實際圖片名稱
	bg_image = pygame.image.load(bg_image_path)    
	bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))  # 調整圖片大小
	
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False  # 結束遊戲
			if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
				return True  # 重新開始遊戲
		
		# 繪製結束畫面內容
		screen.blit(bg_image, (0, 0))  # 繪製背景圖片
		screen.blit(font_end.render('Game Over', True, (255, 200, 0)), (80, 140))
		screen.blit(font_end.render(f'Final Scores: {score}', True, (255, 200, 0)), (80, 260))
		screen.blit(font_end.render('Press R to Restart', True, (255, 200, 0)), (80, 380))
		pygame.display.update()

def showVictoryScreen(screen, font_end, score):
	"""
	顯示遊戲通關畫面
	"""
	bg_image_path = os.path.join(ROOTDIR, 'resources/images/victory.JPG')  # 勝利背景圖片
	bg_image = pygame.image.load(bg_image_path)
	bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
	
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
		
		screen.blit(bg_image, (0, 0))
		screen.blit(font_end.render('Congratulations!', True, (255, 255, 0)), (80, 140))
		screen.blit(font_end.render('You beat the game!', True, (255, 200, 0)), (80, 260))
		screen.blit(font_end.render(f'Final Scores: {score}', True, (255, 200, 0)), (80, 380))
		pygame.display.update()

# 初始化游戏
def gameInit():
	pygame.init()
	pygame.mixer.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption('2024_PyGame_Final_Project')
	
	# 加載字體
	font = pygame.font.SysFont('Arial', 30, bold=True)
	font_end = pygame.font.SysFont('Arial', 50, bold=True)
	#
	
	# 顯示開始頁面
	showStartScreen(screen, font)
	
	# 加載圖片
	gem_imgs = []
	for i in range(1, 8):
		gem_imgs.append(os.path.join(ROOTDIR, 'resources/images/gem%s.png' % i))

	game = Game(screen, font, gem_imgs)

	level = 1
	max_level = 3  # 總關卡數

	while level <= max_level:
		# 遊戲開始
		score = game.start(level)  # 傳入當前關卡

		if score >= game.getLevelTarget(level):
			if level < max_level:
				showLevelTransition(screen, font, level + 1)  # 顯示過渡畫面
			level += 1
		else:
			restart = showEndScreen(screen, font_end, score)
			if restart:
				level = 1
				game.reset()
			else:
				pygame.quit()
				sys.exit()

	showVictoryScreen(screen, font_end, score)  # 通關後的勝利畫面
	pygame.quit()
	sys.exit()



if __name__ == '__main__':
	gameInit()