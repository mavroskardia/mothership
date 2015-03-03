import random, math, zipfile, os

import pygame
from pygame.locals import *

RESOLUTION = (800,600)

class TitleScreen(object):
	
	def __init__(self, game, alpha=0, show_high_scores=True):
		self.game = game
		self.screen = pygame.display.get_surface()
		self.screen.fill((0,0,0))
		self.choice_font = pygame.font.Font('resources/century.ttf', 30)
		self.alpha = alpha		
		self.modes = ['play', 'highscores', 'quit'] if show_high_scores else ['play', 'quit']
		self.show_high_scores = show_high_scores
		
	def run(self): 		
		self.mode_selected = 0
		self.title_text = pygame.font.Font('resources/century.ttf', 80).render("Mothership", True, (255, 90, 0))
		
		self.done = False
		while not self.done:
			self.handle_input()
			self.render()
			
		return self.modes[self.mode_selected]

	def handle_input(self):
		events = pygame.event.get()
		for e in events:
			if e.type == KEYDOWN:
				if e.key == K_DOWN: self.mode_selected += 1
				elif e.key == K_UP: self.mode_selected -= 1
				elif e.key == K_RETURN: self.done = True
			elif e.type == QUIT: self.done = True
				
		if self.mode_selected > len(self.modes)-1: self.mode_selected = 0
		if self.mode_selected < 0: self.mode_selected = len(self.modes) - 1

	def render(self):
		surf = pygame.Surface(RESOLUTION)
		sw, sh = surf.get_size()
		
		tx = (sw - self.title_text.get_width()) / 2
		ty = (sh - self.title_text.get_height()) / 4
		
		surf.blit(self.title_text, (tx, ty))

		if self.show_high_scores:
			if self.mode_selected == 0:
				play_choice = self.choice_font.render("Play", True, (255,255,255))
				score_choice = self.choice_font.render("High Scores", True, (100,100,100))
				quit_choice = self.choice_font.render("Quit", True, (100,100,100))
			elif self.mode_selected == 1:
				play_choice = self.choice_font.render("Play", True, (100,100,100))
				score_choice = self.choice_font.render("High Scores", True, (255,255,255))
				quit_choice = self.choice_font.render("Quit", True, (100,100,100))
			elif self.mode_selected == 2:
				play_choice = self.choice_font.render("Play", True, (100,100,100))
				score_choice = self.choice_font.render("High Scores", True, (100,100,100))
				quit_choice = self.choice_font.render("Quit", True, (255,255,255))

			c1x = (sw - play_choice.get_width()) / 2
			c1y = (sh - play_choice.get_height()) / 2
			
			c2x = (sw - score_choice.get_width()) / 2
			c2y = c1y + 40
			
			c3x = (sw - quit_choice.get_width()) / 2
			c3y = c2y + 40
				
			surf.blit(play_choice, (c1x, c1y))
			surf.blit(score_choice, (c2x, c2y))									
			surf.blit(quit_choice, (c3x, c3y))
			
		else:
			if self.mode_selected == 0:
				play_choice = self.choice_font.render("Play", True, (255,255,255))
				quit_choice = self.choice_font.render("Quit", True, (100,100,100))
			elif self.mode_selected == 1:
				play_choice = self.choice_font.render("Play", True, (100,100,100))
				quit_choice = self.choice_font.render("Quit", True, (255,255,255))			
			
			c1x = (sw - play_choice.get_width()) / 2
			c1y = (sh - play_choice.get_height()) / 2
			
			c2x = (sw - quit_choice.get_width()) / 2
			c2y = c1y + 40			
				
			surf.blit(play_choice, (c1x, c1y))
			surf.blit(quit_choice, (c2x, c2y))
			
		surf.set_alpha(self.alpha)
		self.screen.blit(surf, (0,0))
		pygame.display.flip()
		surf.fill((0,0,0))
		pygame.time.delay(50)
		self.alpha += 1
		self.alpha = min(255, self.alpha)
		
class Object(object):
	
	hits = 0
	
	def __repr__(self): return "Generic Object"
	def __str__(self): return "Generic Object"
	
	def collides_with(self, object):
		return self.x >= object.x and self.x <= object.x+object.width and self.y >= object.y and self.y <= object.y+object.height

class FloaterText(Object):
	
	def __init__(self, game, (x,y), text, time=2000):
		self.game = game
		self.x, self.y = x, y
		self.text = text
		self.time = time
		self.current_time = 0
		self.speed = 0.5
		self.alpha = 255
		self.width, self.height = 0, 0
		
	def update(self, ticks):
		self.current_time += ticks
		
		if self.current_time > self.time: 
			self.current_time = self.time
			self.game.remove_object(self)
		
		self.y -= self.speed
		self.alpha = 255 - ( (float(self.current_time) / float(self.time)) * 255.)
		
	def render(self, surface):
		txt = self.game.float_font.render(self.text, True, (self.alpha,self.alpha,self.alpha))
		surface.blit(txt, (self.x, self.y))
		
class Explosion(Object):
	
	def __repr__(self): return "Explosion"
	def __str__(self): return "Explosion"
	
	def __init__(self, game, (x,y), magnitude):
		self.game = game
		self.x, self.y = x, y
		self.width, self.height = 0,0
		self.radius = 1
		self.stage = 0
		self.max_stages = max(1,magnitude)
		self.stage_interval = 200
		self.current_ticks = 0
		self.game.explosion_sound.play()
		
	def update(self, ticks):
		
		if self.stage >= self.max_stages: self.game.remove_object(self)
		
		self.current_ticks += ticks
		
		if self.current_ticks > self.stage_interval:
			self.current_ticks = 0
			self.stage += 1
			
		self.radius += 2
	
	def render(self, surface):		
		surf = pygame.Surface((self.radius*2+5, self.radius*2+5)).convert_alpha()
		surf.fill((0,0,0,0))
		surf.lock()
		r = random.randint(6, max(10, 6*self.stage))
		for i in range(r):
			x = self.radius * math.cos(i) + self.radius
			y = self.radius * math.sin(i) + self.radius
			sz = random.randint(1,3)
			c = (max(0, 255-self.stage*(255/self.max_stages)),0,0)
			if sz == 1: surf.set_at((int(x),int(y)), c)
			else: pygame.draw.circle(surf, c, (int(x), int(y)), sz)
			
		surf.unlock()
				
		surface.blit(surf, (self.x-self.radius, self.y-self.radius))
		
	def hit(self, hitter): pass
		
class Missile(Object):
	def __repr__(self): return "Missile"
	def __str__(self): return "Missile"
	
	def __init__(self, owner, game, velocity=0.5, acceleration=1.1, direction=-1):
		self.owner = owner
		self.game = game
		self.vel = velocity
		self.accel = acceleration
		self.dir = direction
		
		self.image = self.game.missile_image_up if direction == -1 else self.game.missile_image_down
		self.width, self.height = self.image.get_size()

		self.x = (owner.x+(owner.width-self.width)/2)
		self.y = owner.y - self.height/2 if direction == -1 else owner.y + owner.height
		
		self.game.missile_sound.play()
		
	def update(self, ticks):
		self.y += self.dir * self.vel
		self.vel *= self.accel
		
		if self.dir == -1 and self.y < 0: self.game.remove_object(self)
		elif self.dir == 1 and self.y > self.game.screen.get_height(): self.game.remove_object(self)
		
		for object in self.game.objects:
			if self.is_valid_target(object) and self.collides_with(object): 
				self.game.remove_object(self)
				self.game.add_object(Explosion(self.game, (self.x+self.width/2, self.y+self.height/2), 5))		
				object.hit(self)
			
	def is_valid_target(self, object):
		if object == self: return False
		
		if isinstance(object, Missile):
			if object.owner != self.owner: return True
		else:
			if self.owner != object: return True
			
		return False
					
	def hit(self, hitter):
		if self in self.game.objects: self.game.remove_object(self)
		self.game.score += 50		
		
	def collides_with(self, object):
		return self.x >= object.x and self.x <= object.x+object.width and self.y >= object.y and self.y <= object.y+object.height
		
	def render(self, surface): surface.blit(self.image, (self.x, self.y))

class Ship(Object):
	
	def __repr__(self): return "Generic Ship"
	def __str__(self): return "Generic Ship"
	
	width = 32
	height = 32
	x = 400
	y = 500
	color = (200,0,0)

	def __init__(self, game):
		self.x_speed = 0
		self.x_factor = 1
		self.y_speed = 0
		self.y_factor = 1
		self.game = game
		self.moving_left = False
		self.moving_right = False
		self.moving_up = False
		self.moving_down = False

	def update(self, ticks):
		if self.moving_left: self.x_speed -= self.x_factor
		if self.moving_right: self.x_speed += self.x_factor
		if self.moving_down: self.y_speed += self.y_factor
		if self.moving_up: self.y_speed -= self.y_factor

		self.x += self.x_speed
		self.y += self.y_speed
		
		self.x_speed *= 0.9 # deceleration
		self.y_speed *= 0.9

	def render(self, surface):		
		pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), 2)

class Player(Ship):
	
	def __repr__(self): return "Player Ship"
	def __str__(self): return "Player Ship"
	
	fire_interval = 150
	current_ticks = 0
	can_fire = True
	invincible = 0
	
	def __init__(self, game):
		Ship.__init__(self, game)
		
		self.main_frame = pygame.image.load('resources/plane.gif').convert()
		self.left_frame1 = pygame.image.load('resources/plane_turning_left_1.gif').convert()
		self.left_frame2 = pygame.image.load('resources/plane_turning_left_2.gif').convert()
		self.right_frame1 = pygame.image.load('resources/plane_turning_right_1.gif').convert()
		self.right_frame2 = pygame.image.load('resources/plane_turning_right_2.gif').convert()
		
		self.current_frame = self.main_frame
	
	def update(self, ticks):
		Ship.update(self, ticks)
		
		self.y = max(0, self.y)
		self.y = min(self.y, self.game.screen.get_height()-self.height)
		self.x = max(-self.width/2, self.x)
		self.x = min(self.x, self.game.screen.get_width()-self.width/2)

		if self.invincible > 0: self.invincible -= ticks
		
		self.current_ticks += ticks
		
		if self.current_ticks > self.fire_interval: 
			self.can_fire = True
			self.current_ticks = 0

		if self.x_speed > -1 and self.x_speed < 1: self.current_frame = self.main_frame
		elif self.x_speed <= -1 and self.x_speed > -4: self.current_frame = self.left_frame1
		elif self.x_speed <= -4: self.current_frame = self.left_frame2
		elif self.x_speed >= 1 and self.x_speed < 4: self.current_frame = self.right_frame1
		elif self.x_speed >= 4: self.current_frame = self.right_frame2
			
		self.width = self.current_frame.get_width()
		self.height = self.current_frame.get_height()
		
		for obj in self.game.objects:
			if self != obj and self.collides_with(obj): self.hit(obj)

	def hit(self, hitter):
		assert isinstance(hitter, Object), "Can only be hit by Objects"
		
		if self.invincible > 0: return
		if isinstance(hitter, Missile):
			if hitter.owner == self: return
			
		for i in range(random.randint(1,10)):
			x = random.randint(-30,30)
			self.game.add_object(Explosion(self.game, (x+self.x+self.width/2, x+self.y+self.height/2), 10))
		
		self.game.lives -= 1
		self.x, self.y = 400, 500
		self.invincible = 1500
		
		if self.game.lives < 0: 
			self.game.lives = 0
			self.game.show_game_over()
	
	def render(self, surface):
		surface.blit(self.current_frame, (self.x, self.y))
		
	def fire(self):
		if self.can_fire:
			self.game.add_object(Missile(self, self.game))
			self.can_fire = False

class Mothership(Ship):
	
	def __repr__(self): return "Mothership"
	def __str__(self): return "Mothership"
	
	def __init__(self, game):
		Ship.__init__(self, game)		
		self.current_frame = pygame.image.load('resources/Nightmare.gif').convert()
		self.width, self.height = self.current_frame.get_size()
		self.x, self.y = 0, 20
		self.fire_interval = 100 + 100*game.difficulty_factor
		self.max_fire_interval = 5000/game.difficulty
		self.current_ticks = 0
		self.tolerance = 10+game.difficulty
		self.hits = 0
		self.max_hits = int(game.difficulty * 10)
		self.mask = self.create_mask(self.current_frame.get_colorkey())
		self.mask.set_alpha(0)
		self.x_factor = 0.5 + game.difficulty_factor
		self.moving_right = True
		self.moving_down = True
		
	def create_mask(self, colorkey=0x000000):
		surf = pygame.Surface((self.width, self.height))
		surf.lock()
		for y in xrange(self.height):
			for x in xrange(self.width):
				px = self.current_frame.get_at((x,y))
				if px == colorkey: surf.set_at((x,y), (0,0,0,0))
				else: surf.set_at((x,y), (100,0,0,0))
		surf.unlock()
		return surf
		
	def render(self, surface):
		surface.blit(self.current_frame, (self.x, self.y))
		surface.blit(self.mask, (self.x, self.y))
	
	def hit(self, hitter):
		self.hits += 1
		self.mask.set_alpha((180/self.max_hits*self.hits))
		if self.hits >= self.max_hits:
			for i in range(5):
				mag = random.randint(-30, 30)
				self.game.add_object(Explosion(self.game, (self.x+mag+self.width/2, self.y+mag+self.height/2), abs(mag)))
			self.game.score += 1000
			self.game.remove_object(self)
			self.game.increase_difficulty()
			
	def update(self, ticks):
		Ship.update(self, ticks)
		
		self.current_ticks += ticks
		
		if self.current_ticks > self.fire_interval:
			self.current_ticks = 0
			self.fire_interval = random.randint(10, int(self.max_fire_interval))
			self.game.add_object(Missile(self, self.game, 0.1, 1.1, 1))
			self.color = (0,200,0)
			
		self.width, self.height = self.current_frame.get_size()
			
		self.do_movements()
		
	def do_movements(self):
		if self.game.difficulty < 10:
			# basic figure 8
			if self.x+self.width/2 >= RESOLUTION[0]: 
				self.moving_right = False
				self.moving_left = True
			if self.x <= 0:
				self.moving_right = True
				self.moving_left = False
				
			if self.y <= 0: 
				self.moving_down = True
				self.moving_up = False
			if self.y >= RESOLUTION[1]/2-self.height:
				self.moving_down = False
				self.moving_up = True
		else:
			# track with the player
			self.moving_right = self.x+self.width/2 < self.game.player.x+self.game.player.width/2
			self.moving_left = self.x+self.width/2 > self.game.player.x+self.game.player.width/2
			self.moving_down = self.game.player.y > 3*RESOLUTION[1]/4 and self.y+self.height < RESOLUTION[1]/3
			self.moving_up = self.game.player.y < 3*RESOLUTION[1]/4 and self.y > 0
		
class Game(object):
	
	def __init__(self):
		self.screen = pygame.display.set_mode(RESOLUTION, FULLSCREEN)
		pygame.mixer.init()
		pygame.font.init()
		self.fps_font = pygame.font.Font(None, 18)
		self.score_font = pygame.font.Font('resources/century.ttf', 24)
		self.float_font = self.fps_font
		self.clock = pygame.time.Clock()
		
		self.high_score_table = HighScoreTable()
		
		self.current_song = pygame.mixer.Sound('resources/bgm.ogg')
		self.current_channel = None	
		self.explosion_sound = pygame.mixer.Sound('resources/explosion.ogg')
		self.explosion_sound.set_volume(0.4)
		self.missile_sound = pygame.mixer.Sound('resources/missile.ogg')
		self.missile_sound.set_volume(0.1)
		self.one_up_sound = pygame.mixer.Sound('resources/oneup.ogg')
		self.one_up_sound.set_volume(0.8)
		
		missile_image = pygame.image.load('resources/missile00.png').convert()
		self.missile_image_up = pygame.transform.rotate(missile_image, 90)
		self.missile_image_down = pygame.transform.rotate(missile_image, -90)
		
		self.starfield = Starfield()
		
	def __get_s(self): return self.__score
	def __set_s(self, score): 
		self.__score = score
		if self.__score >= self.next_free_life:
			self.add_object(FloaterText(self, (self.player.x+self.player.width, self.player.y), "1up"))
			self.lives += 1
			self.one_up_sound.play(2)
			self.next_free_life += 5000
		
	score = property(__get_s, __set_s, None, "Score")
		
	def setup_game(self):
		self.player = Player(self)
		self.objects = set([self.player])
		self.objects_to_remove = set()
		self.objects_to_add = set()
		self.lives = 3
		self.next_free_life = 5000
		self.score = 0
		self.difficulty = 1
		self.difficulty_factor = 0.1
		self.score_ticks = 0
		self.score_ticks_max = 500
			
	def handle_input(self):
		
		events = pygame.event.get()
		
		for e in events:
			if e.type == QUIT: self.main_loop_done = True
			elif e.type == KEYDOWN: self.handle_keypress(e.key)

		keys = pygame.key.get_pressed()
		
		self.player.moving_left = keys[K_LEFT]
		self.player.moving_right = keys[K_RIGHT]
		self.player.moving_up = keys[K_UP]
		self.player.moving_down = keys[K_DOWN]
		
		if keys[K_SPACE]: self.handle_space_key()
		
	def handle_keypress(self, key):
		
		if key == K_ESCAPE:
			option = TitleScreen(self, 255, False).run()
			if option == 'quit': self.main_loop_done = True
			
	def handle_space_key(self):	self.player.fire()

	def increase_difficulty(self):
		self.difficulty += self.difficulty_factor
		self.difficulty_factor += 0.1
		self.score_ticks_max -= self.difficulty
		self.score_ticks_max = max(50, self.score_ticks_max)

	def update(self):
		ticks = self.clock.tick(30)
		
		self.score_ticks += ticks
		if self.score_ticks > self.score_ticks_max:
			self.score_ticks = 0
			self.score += 1
	
		for obj in self.objects_to_add: self.objects.add(obj)
		self.objects_to_add = set()
		
		for obj in self.objects_to_remove: self.objects.remove(obj)
		self.objects_to_remove = set()
		
		self.starfield.update(ticks)
		
		found_mothership = False
		for object in self.objects: 
			object.update(ticks)
			if isinstance(object, Mothership): found_mothership = True
			
		if not found_mothership: self.add_object(Mothership(self))
		
	def add_object(self, object): self.objects_to_add.add(object)
	
	def remove_object(self, object):
		if object in self.objects: self.objects_to_remove.add(object)
	
	def render(self):
		
		self.starfield.render(self.screen)
		
		for object in self.objects: object.render(self.screen)
		
		fps = self.fps_font.render("fps: %.2f" % self.clock.get_fps(), True, (100,100,100))
		self.screen.blit(fps, (0,0))
		
		score = self.score_font.render("Score: %d" % self.score, True, (255,255,255))
		self.screen.blit(score, (self.screen.get_width()-score.get_width()-10, 10))
		
		lives = self.score_font.render("Lives: %d" % self.lives, True, (255,255,255))
		self.screen.blit(lives, (self.screen.get_width()-score.get_width()-10, 35))
		
		#speed = self.fps_font.render("Speed: %f" % self.player.x_speed, True, (100,100,100))
		#self.screen.blit(speed, (0, 20))
				
	def show_game_over(self):
		
		self.render()
		last_scene = pygame.Surface(RESOLUTION)
		last_scene.blit(self.screen, (0,0))
		
		fade_over_surface = pygame.Surface(RESOLUTION).convert_alpha()
		fade_over_surface.fill((0,0,0,100))
		
		game_over_text = self.score_font.render("Game Over", True, (255,255,255))
		game_over_box = pygame.Surface((game_over_text.get_width()+10, game_over_text.get_height()+10))
		game_over_box.fill((0,0,0))
		pygame.draw.rect(game_over_box, (255,90,0), (0, 0, game_over_box.get_width()-1, game_over_box.get_height()-1), 2)
		tx = (game_over_box.get_width() - game_over_text.get_width()) / 2
		ty = (game_over_box.get_height() - game_over_text.get_height()) / 2
		game_over_box.blit(game_over_text, (tx, ty))
		
		x = (RESOLUTION[0] - game_over_box.get_width()) / 2
		y = (RESOLUTION[1] - game_over_box.get_height()) / 2
		
		done = False
		while not done:
			events = pygame.event.get()
			for e in events:
				if e.type == KEYDOWN and e.key == K_ESCAPE: done = True
			
			self.screen.blit(last_scene, (0,0))
			self.screen.blit(fade_over_surface, (0,0))
			self.screen.blit(game_over_box, (x,y))
			
			pygame.display.flip()
			pygame.time.delay(50)
			
		if self.high_score_table.is_high_score(self.score): self.high_score_table.new_score_entry(self.screen, self.score)
		
		self.main_loop_done = True
		
	def music_update(self):
		if self.current_channel is None or not self.current_channel.get_busy():
			self.current_channel = self.current_song.play()
			self.current_channel.set_volume(0.5)
		
	def run(self):
		pygame.mouse.set_visible(False)
				
		all_done = False
		alpha = 0
		while not all_done:
			option = TitleScreen(self, alpha).run()	
			alpha = 255
			if option == 'highscores':
				done = False
				while not done:
					events = pygame.event.get()
					for e in events:
						if e.type == KEYDOWN and e.key == K_ESCAPE: done = True
					self.screen.fill((0,0,0))
					self.high_score_table.render(self.screen)
					pygame.display.flip()
					pygame.time.delay(50)
			elif option == 'quit': all_done = True
			elif option == 'play':				
				self.main_loop_done = False if option == 'play' else True
				self.setup_game()
				while not self.main_loop_done:
					self.handle_input()
					self.update()
					self.music_update()
					self.render()
					
					pygame.display.flip()
					self.screen.fill((0,0,0))
			
				self.high_score_table.save_high_scores()
				
		pygame.mouse.set_visible(True)

class Starfield(object):
	
	class Star(object):
		
		def __init__(self): self.randomize()			
			
		def randomize(self):
			self.x = random.randint(0, RESOLUTION[0])
			self.y = random.randint(0, RESOLUTION[1])
			self.accel = 1.0 + random.random()/32
			self.length = int(self.accel * 200)
			self.vel = random.random()
			self.color = random.randint(50, 200)
			self.size = random.randint(1,3)
		
		def render(self, surface):
			if self.size == 1: 
				surface.set_at((int(self.x), int(self.y)), (self.color, self.color, self.color))
			elif self.size == 2: 
				pygame.draw.rect(surface, (self.color,self.color,self.color), (int(self.x), int(self.y), self.size, self.size))
			elif self.size == 3:
				pygame.draw.circle(surface, (self.color,self.color,self.color), (int(self.x), int(self.y)), self.size)
			
		def update(self, ticks):
			self.y += self.vel
			self.vel *= self.accel
			
			if self.y > RESOLUTION[1]:
				self.randomize()
				self.y = 0
				
	def __init__(self, num_stars=100):
		self.num_stars = num_stars
		self.width, self.height = RESOLUTION
		self.stars = []
		
		for i in range(num_stars):
			s = self.Star()
			self.stars.append(s)
			
	def update(self, ticks):
		for s in self.stars: s.update(ticks)
		
	def render(self, surface):
		for s in self.stars: s.render(surface)	

class HighScoreTable(object):
	
	class Entry(object):
		
		def __init__(self, _score, _name):
			self.name = str(_name); self.score = int(_score)
			
		def __cmp__(self, obj):
			try: cmp = 0 if obj.score == self.score else -1 if obj.score > self.score else 1
			except Exception: return 0
			return cmp
	
	def __init__(self, high_score_file="resources/highscores.txt"):
		self.high_score_file = high_score_file
		self.high_scores = self.load_high_scores()
		self.score_font = pygame.font.Font('resources/century.ttf', 30)
		self.new_scores = False
		
	def is_high_score(self, score):
		return len(self.high_scores) < 10 or score > self.high_scores[-1].score
		
	def save_high_scores(self):
		if self.new_scores:		
			f = open(self.high_score_file, 'w')
			for entry in self.high_scores: f.write("%s,%s\n" % (entry.score, entry.name))				
			f.close()
		
	def load_high_scores(self):
		if not os.path.exists(self.high_score_file): return []
		
		high_scores = []
		
		f = open(self.high_score_file, 'r')
		for line in f:
			score, name = line.split(',')
			high_scores.append(self.Entry(score.strip(), name.strip()))
		f.close()
		
		high_scores.sort()
		high_scores.reverse()
		
		return high_scores
		
	def store_score(self, name, score):		
		self.high_scores.append(self.Entry(score, name))
		self.new_scores = True		
		self.high_scores.sort()
		self.high_scores.reverse()
		if len(self.high_scores) > 10: self.high_scores.pop()
		
	def new_score_entry(self, surface, score):
		sw, sh = surface.get_size()
		msg = self.score_font.render("Enter your name:", True, (255,255,255))
		msg_x = (sw - msg.get_width()) / 2
		msg_y = (sh - msg.get_height()) / 2
		name = ""
		
		done = False
		while not done:
			surface.fill((0,0,0))
		
			events = pygame.event.get()
			for e in events:
				if e.type == KEYDOWN:
					if e.key == K_RETURN: done = True
					elif e.key == K_BACKSPACE: name = name[0:-1]
					elif e.key == K_SPACE: name += " "
					else:
						key = e.key
						tmpbuf = ""
						if key >= K_a and key <= K_z:
							if e.mod & KMOD_SHIFT: key -= 32
							tmpbuf = chr(key)
						elif key >= K_EXCLAIM and key < K_a: tmpbuf = e.unicode

						name += tmpbuf
			
			txt = self.score_font.render(name, True, (255,255,255))
			txt_x = (sw - txt.get_width()) / 2
			txt_y = msg_y + 40
			
			surface.blit(msg, (msg_x, msg_y))
			surface.blit(txt, (txt_x, txt_y))
			
			pygame.display.flip()
			pygame.time.delay(50)
			
		self.store_score(name, score)
			
	def render(self, surface):
		
		num_scores = len(self.high_scores)
		
		if num_scores == 0:
			nhs = self.score_font.render("No High Scores!", True, (255,255,255))
			surface.blit(nhs, ((surface.get_width()-nhs.get_width())/2, (surface.get_height()-nhs.get_height())/2))
			return
		
		title = self.score_font.render("High Scores", True, (255, 90, 0))
		
		total_height = num_scores * (self.score_font.get_height() + 10)
		max_score_width = 0
		
		dy = (surface.get_height() - total_height) / 2
		surface.blit(title, ( (surface.get_width()-title.get_width())/2, (dy - 40)))
		
		for i in xrange(len(self.high_scores)):
			score = self.high_scores[i]
			c = (255,255,255) if i == 0 else (100,100,100)

			score_txt = self.score_font.render(str(score.score), True, c)
			max_score_width = max(max_score_width, score_txt.get_width())
			surface.blit(score_txt, (50, dy))
			dy += self.score_font.get_height() + 10

		dy = (surface.get_height() - total_height) / 2
		
		for i in xrange(len(self.high_scores)):
			score = self.high_scores[i]
			c = (255,255,255) if i == 0 else (100,100,100)

			name_txt = self.score_font.render(score.name, True, c)
			surface.blit(name_txt, (max_score_width+150, dy))			
			dy += self.score_font.get_height() + 10

			
if __name__ == '__main__':	Game().run()