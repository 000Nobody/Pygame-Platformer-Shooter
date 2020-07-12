import pygame, math, sys, os, random
from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
clock = pygame.time.Clock()

pygame.display.set_caption('Shooter Platformer')

WINDOW_SIZE = (1920, 1080)

screen = pygame.display.set_mode(WINDOW_SIZE, FULLSCREEN | DOUBLEBUF)

display = pygame.Surface(WINDOW_SIZE)

pygame.mouse.set_visible(False)

# Create variables
scroll = [0,0]
gravity_strength = 1.8
bullets = []
enemy_bullets = []
tile_rects = []
particles = []
enemies = []

# Load Images
cursor = pygame.transform.scale(pygame.image.load('data/images/cursor.png'), (32, 32)).convert()
cursor.set_colorkey((255, 255, 255))

bgback = pygame.image.load('data/images/backgrounds/BGBack.png').convert_alpha()
bgfront = pygame.image.load('data/images/backgrounds/BGFront.png').convert_alpha()
cloudsback = pygame.image.load('data/images/backgrounds/CloudsBack.png').convert_alpha()
cloudsfront = pygame.image.load('data/images/backgrounds/CloudsFront.png').convert_alpha()

grass = pygame.image.load('data/images/grass.png').convert()
ground1 = pygame.image.load('data/images/ground1.png').convert()
ground2 = pygame.image.load('data/images/ground2.png').convert()
ground3 = pygame.image.load('data/images/ground3.png').convert()
ground4 = pygame.image.load('data/images/ground4.png').convert()

gun_img = pygame.image.load('data/images/gun.png').convert_alpha()

projectile_img = pygame.image.load('data/images/projectile.png').convert()
projectile_img.set_colorkey((0, 0, 0))

enemy_projectile_img = pygame.image.load('data/images/enemy_projectile.png').convert()
enemy_projectile_img.set_colorkey((0, 0, 0))

def load_animations(actions, folder_name): #(['Running', 'Idle'], 'player_images')
	animation_database = {}
	for action in actions:
		image_path = 'data/' + folder_name + '/' + action
		animation_database.update({action:[]})
		for image in os.listdir(image_path):
			image_id = pygame.image.load(image_path + '/' + image).convert_alpha()
			animation_database[action].append(pygame.transform.scale(image_id, (200, 200)))
	return animation_database

# Load sounds
death_sound = pygame.mixer.Sound('data/sounds/death.wav')
jump_sound = pygame.mixer.Sound('data/sounds/jump.wav')
shoot_sound = pygame.mixer.Sound('data/sounds/shoot.wav')
explosion_sound = pygame.mixer.Sound('data/sounds/explosion.wav')
enemy_hit_sound = pygame.mixer.Sound('data/sounds/enemy_hit.wav')
enemy_death_sound = pygame.mixer.Sound('data/sounds/enemy_death.wav')
player_hit_sound = pygame.mixer.Sound('data/sounds/player_hit.wav')
jump_sound.set_volume(0.8)
shoot_sound.set_volume(0.5)
explosion_sound.set_volume(0.7)
enemy_hit_sound.set_volume(0.7)

pygame.mixer.music.load('data/sounds/bgmusic.wav')
pygame.mixer.music.set_volume(0.6)

#Classes
class Level():
	def __init__(self, id, player_pos, enemy_pos):
		self.player_pos = player_pos
		self.enemy_pos = enemy_pos
		self.tile_size = (64, 64)
		self.id = id
		self.path = 'data/maps/map{0}.txt'.format(self.id)

	def load_map(self):
		self.map = []
		with open(self.path, 'r') as f:
			data = f.read()
			f.close()
			data = data.split('\n')
			for row in data:
				self.map.append(list(row))

	def draw(self):
		global tile_rects
		tile_rects = []
		y = 0
		for layer in self.map:
			x = 0
			for tile in layer:
				if tile == '1':
					display.blit(grass, (x*self.tile_size[0] - scroll[0], y*self.tile_size[1] - scroll[1]))
				if tile == '2':
					display.blit(ground1, (x*self.tile_size[0] - scroll[0], y*self.tile_size[1] - scroll[1]))
				if tile == '3':
					display.blit(ground2, (x*self.tile_size[0] - scroll[0], y*self.tile_size[1] - scroll[1]))
				if tile == '4':
					display.blit(ground3, (x*self.tile_size[0] - scroll[0], y*self.tile_size[1] - scroll[1]))
				if tile == '5':
					display.blit(ground4, (x*self.tile_size[0] - scroll[0], y*self.tile_size[1] - scroll[1]))	
				if tile != '0':
					tile_rects.append(pygame.Rect(int(x*self.tile_size[0]), int(y*self.tile_size[1]), self.tile_size[0], self.tile_size[1]))
				x += 1
			y += 1

class Player():
	def __init__(self, width, height, vel, jump_height, health):
		self.vel = vel
		self.width = width
		self.height = height
		self.jump_height = jump_height
		self.health = health
		self.jumping = False
		self.moving_right = False
		self.moving_left = False
		self.flip = False
		self.sprinting = False
		self.vertical_momentum = 0
		self.movement = [0, 0]
		self.frame = 0
		self.action = 'Idle'
		self.animation_speed = 0
		self.level = 'tutorial'
		self.times_jumped = 0
		self.animation_database = load_animations(['Running', 'Idle', 'Walking'], 'player_images')
		self.rect = pygame.Rect(int(levels[self.level].player_pos[0]), int(levels[self.level].player_pos[1]), self.width, self.height)

	def update(self):
		self.move()
		self.looking(pygame.mouse.get_pos())

	def move(self):
		if self.sprinting:
			self.vel = 15
		if self.moving_right:
			self.movement[0] = self.vel
		if self.moving_left:
			self.movement[0] = -self.vel
		if self.jumping:
			self.vertical_momentum = -self.jump_height
			self.times_jumped += 1
			jump_sound.play()
			for i in range(5):
				particles.append(Particle(player.rect.midbottom[0], player.rect.midbottom[1], [(150, 150, 150), (255, 255, 255), (200, 200, 200)], -40, 40, -5, 0, 2, 10, 0.8, 0.2))
			self.jumping = False

		if not self.moving_left and not self.moving_right:
			self.movement = [0, 0]
		self.movement[1] = self.vertical_momentum

		self.rect, self.collision_types = move(self.rect, tile_rects, self.movement)

		self.vertical_momentum += gravity_strength
		if self.vertical_momentum > 50:
			 self.vertical_momentum = 50

		if self.collision_types['bottom']:
			self.vertical_momentum = 0
			self.times_jumped = 0
		if self.collision_types['top']:
			self.vertical_momentum = 0

	def die(self):
		pygame.mixer.music.fadeout(1000)
		death_sound.play()
		self.rect.x = levels[self.level].player_pos[0]
		self.rect.y = levels[self.level].player_pos[0]
		enemies.clear()
		bullets.clear()
		particles.clear()
		enemy_bullets.clear()
		for enemy_pos in levels[self.level].enemy_pos:
			enemies.append(Enemy(enemy_id_counter, enemy_pos, 75, 125, 100, 1000, 1000))
		pygame.mixer.music.play(-1)
		self.health = 100
		self.living = True

	def draw(self):
		if self.moving_right or self.moving_left:
			if self.sprinting:
				self.change_action(self.action, 'Running', self.frame)
			else:
				self.change_action(self.action, 'Walking', self.frame)
		if self.movement[0] == 0:
			self.change_action(self.action, 'Idle', self.frame)

		if self.action == 'Idle':
			self.animation_speed = 6
		if self.action == 'Running':
			self.animation_speed = 4
		if self.action == 'Walking':
			self.animation_speed = 2

		self.frame += 1
		if self.frame >= len(self.animation_database[self.action]) * self.animation_speed:
			self.frame = 0

		current_image = self.animation_database[self.action][self.frame//self.animation_speed]

		display.blit(pygame.transform.flip(current_image, self.flip, False), (int(self.rect.x - 60 - scroll[0]), int(self.rect.y - 40 - scroll[1])))
		# pygame.draw.rect(display, (0, 0, 0), self.rect, 1)

	def change_level(self, new_level):
		enemies.clear()
		particles.clear()
		bullets.clear()
		enemy_bullets.clear()
		self.level = new_level
		self.rect.topleft = levels[new_level].player_pos
		for enemy_pos in levels[new_level].enemy_pos:
			enemies.append(Enemy(enemy_id_counter, enemy_pos, 75, 125, 100, 1000, 1000))

	def looking(self, mousepos):
		if mousepos[0] <= self.rect.centerx - scroll[0]:
			self.flip = True
		else:
			self.flip = False

	def change_action(self, current_action, new_action, frame):
		if current_action != new_action:
			current_action = new_action
			frame = 0
		self.action = current_action
		self.frame = frame

class Enemy():
	def __init__(self, id, start_pos, width, height, health, pathfind_range, attack_range):
		self.id = id
		self.start_pos = start_pos
		self.width = width
		self.height = height
		self.health = health
		self.vel = 5
		self.jump_height = 20
		self.pathfind_range = pathfind_range
		self.attack_range = attack_range
		self.shoot_timer = 0
		self.movement = [0, 0]
		self.moving_right = False
		self.moving_left = False
		self.jumping = False 
		self.vertical_momentum = 0
		self.flip = False
		self.animation_speed = 0
		self.frame = 0
		self.action = 'Idle'
		self.animation_database = load_animations(['Running', 'Idle', 'Walking'], 'enemy_images')
		self.rect = pygame.Rect(int(self.start_pos[0]), int(self.start_pos[1]), self.width, self.height)

	def update(self):
		self.move()
		self.pathfind()
		self.attack()
		self.looking()

	def move(self):
		if self.moving_right:
			self.movement[0] = self.vel
		if self.moving_left:
			self.movement[0] = -self.vel
		if self.jumping:
			self.vertical_momentum = -self.jump_height
			self.jumping = False
		self.movement[1] = self.vertical_momentum

		self.rect, self.collision_types = move(self.rect, tile_rects + [enemy.rect for enemy in enemies if enemy.id != self.id], self.movement)

		self.vertical_momentum += gravity_strength
		if self.vertical_momentum > 50:
			 self.vertical_momentum = 50

		if self.collision_types['bottom']:
			self.vertical_momentum = 0
			self.times_jumped = 0
		if self.collision_types['top']:
			self.vertical_momentum = 0

	def draw(self):
		if self.moving_right or self.moving_left:
				self.change_action(self.action, 'Walking', self.frame)
		if self.movement[0] == 0:
			self.change_action(self.action, 'Idle', self.frame)

		if self.action == 'Idle':
			self.animation_speed = 6
		if self.action == 'Walking':
			self.animation_speed = 2

		self.frame += 1
		if self.frame >= len(self.animation_database[self.action]) * self.animation_speed:
			self.frame = 0

		current_image = self.animation_database[self.action][self.frame//self.animation_speed]

		display.blit(pygame.transform.flip(current_image, self.flip, False), (int(self.rect.x - 60 - scroll[0]), int(self.rect.y - 40 - scroll[1])))

	def change_action(self, current_action, new_action, frame):
		if current_action != new_action:
			current_action = new_action
			frame = 0
		self.action = current_action
		self.frame = frame

	def attack(self):
		self.shoot_timer += 1
		if math.sqrt(abs((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2)) <= self.attack_range:
			if self.shoot_timer >= 60:
				self.slopex = (player.rect.centerx - scroll[0]) - (self.rect.centerx - scroll[0] + 5)
				self.slopey = (player.rect.centery - scroll[1]) - (self.rect.centery - scroll[1] + 35)
				enemy_bullets.append(Projectile(self.rect.centerx + 5, self.rect.centery + 35, 15, 17, 50, math.atan2(self.slopey, self.slopex), enemy_projectile_img))
				self.shoot_timer = 0
		if self.rect.colliderect(player.rect):
			player.die()

	def pathfind(self):
		if math.sqrt(abs((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2)) <= self.pathfind_range:
			if 10 > abs(self.rect.x - player.rect.x) > 0:
				self.vel = 0
			else:
				self.vel = 5
				if self.rect.centerx > player.rect.centerx:
					self.moving_left = True
					self.moving_right = False
				if self.rect.centerx < player.rect.centerx:
					self.moving_right = True
					self.moving_left = False
		if self.collision_types['left'] or self.collision_types['right']:
			for enemy in enemies:
				if not self.rect.colliderect(enemy.rect):
					self.jumping = True

	def looking(self):
		if self.moving_right:
			self.flip = False
		if self.moving_left:
			self.flip = True

class Gun():
	global x_offset, y_offset
	x_offset, y_offset = 5, 43

	def __init__(self, image):
		self.image = image
		self.x = player.rect.centerx + x_offset - scroll[0]
		self.y = player.rect.centery + y_offset - scroll[1]

	def update(self):
		self.x = player.rect.centerx + x_offset - scroll[0]
		self.y = player.rect.centery + y_offset - scroll[1]

	def get_angle(self, mousepos):
		angle = -math.degrees(math.atan2(self.y - 10 - mousepos[1], self.x - mousepos[0]))
		return angle

	def draw(self, angle):
		if player.flip:
			rotated_gun = pygame.transform.rotate(self.image, angle)
			rect = rotated_gun.get_rect()
			display.blit(pygame.transform.flip(rotated_gun, False, False), (self.x - (rect.width/2), self.y - (rect.height/2)))
		if not player.flip:
			rotated_gun = pygame.transform.rotate(self.image, -angle)
			rect = rotated_gun.get_rect()
			display.blit(pygame.transform.flip(rotated_gun, False, True), (self.x - (rect.width/2), self.y - (rect.height/2)))

		self.gun_rect = pygame.Rect(self.x - (rect.width/2), self.y - (rect.height/2), self.image.get_width(), self.image.get_height())
		# pygame.draw.rect(display, (0, 0, 0), self.gun_rect, 1)

class Projectile():
	def __init__(self, x, y, radius, vel, damage, angle, image):
		self.x = x
		self.y = y
		self.radius = radius
		self.vel = vel
		self.damage = damage
		self.angle = angle
		self.image = image
		self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

	def update(self):
		self.trajectory()
		self.collision_check(self.rect, tile_rects)

	def trajectory(self):
		self.x += math.cos(self.angle) * self.vel
		self.y += math.sin(self.angle) * self.vel

	def draw(self):
		self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
		self.image = pygame.transform.scale(self.image, (self.radius * 2, self.radius * 2))
		display.blit(self.image, (int(self.x - scroll[0] - self.radius), int(self.y - scroll[1] - self.radius)))
		# pygame.draw.rect(display, (0, 0, 0), self.rect)

	def collision_check(self, rects, tiles):
		self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}

		hit_list = collision_check(rects, tiles)

		for rect in hit_list:
			y_difference = (rect.centery - self.rect.centery)
			x_difference = (rect.centerx - self.rect.centerx)
			angle = math.atan2(y_difference, x_difference)
			angle = math.degrees(angle)

			if 45 < angle < 135:
				self.collision_types['bottom'] = True
			if -135 < angle < -45:
				self.collision_types['top'] = True
			if -45 < angle < 45:
				self.collision_types['right'] = True
			if 135 < angle < 180 or -180 < angle < -135:
				self.collision_types['left'] = True

class Particle():
	def __init__(self, x, y, colors, min_xvel, max_xvel, min_yvel, max_yvel, min_radius, max_radius, shrink_rate, gravity):
		self.x = x
		self.y = y
		self.color = random.choice(colors)
		self.xvel = random.randint(min_xvel, max_xvel) / 10
		self.yvel = random.randint(min_yvel, max_yvel) / 10
		self.radius = random.randint(min_radius, max_radius)
		self.shrink_rate = shrink_rate
		self.gravity = gravity

	def update(self):
		self.x += self.xvel
		self.y += self.yvel
		self.radius -= self.shrink_rate
		self.yvel += self.gravity

	def draw(self):
		pygame.draw.circle(display, self.color, (int(self.x - scroll[0]), int(self.y - scroll[1])), int(self.radius))

# Create classes
levels = {'tutorial':Level(0, [600, 600], [(1600, 300), (2000, 400)]), 'level1':Level(1, [600, 600], [800, 300])}
for level in levels:
	levels[level].load_map()

player = Player(75, 125, 10, 28, 100)

enemy_id_counter = 0
for enemy_pos in levels[player.level].enemy_pos:
	enemy_id_counter += 1
	enemies.append(Enemy(enemy_id_counter, enemy_pos, 75, 125, 100, 1000, 1000))

gun = Gun(gun_img)

#Functions
def collision_check(rect, tiles):
	hit_list = []
	for tile in tiles:
		if tile not in hit_list:
			if rect.colliderect(tile):
				hit_list.append(tile)
	return hit_list

def move(rect, tiles, movement):
	collision_types = {'top':False,'bottom':False,'right':False,'left':False}
	rect.x += movement[0]
	hit_list = collision_check(rect, tile_rects)
	for tile in hit_list:
		if movement[0] > 0:
			rect.right = tile.left
			collision_types['right'] = True
		elif movement[0] < 0:
			rect.left = tile.right
			collision_types['left'] = True
	rect.y += movement[1]
	hit_list = collision_check(rect, tile_rects)
	for tile in hit_list:
		if movement[1] > 0:
			rect.bottom = tile.top
			collision_types['bottom'] = True
		elif movement[1] < 0:
			rect.top = tile.bottom
			collision_types['top'] = True

	return rect, collision_types

def update_cursor(mousepos):
	cursor_rect = cursor.get_rect()
	cursor_rect.center = mousepos
	display.blit(cursor, cursor_rect)

def draw():
	display.fill((200,255,255))

	# display.blit(cloudsback, (0 - scroll[0]*0.8 - 500, 0 - scroll[1]*0.8 - 200))
	# display.blit(cloudsfront, (0 - scroll[0]*0.6 - 500, 0 - scroll[1]*0.6 - 200))
	# display.blit(bgback, (0 - scroll[0]*0.4 - 500, 0 - scroll[1]*0.4 - 200))
	# display.blit(bgfront, (0 - scroll[0]*0.2 - 500, 0 - scroll[1]*0.2 - 200))

	levels[player.level].draw()

	for enemy in enemies:
		enemy.draw()

	player.draw()

	for particle in particles:
		particle.draw()

	for bullet in enemy_bullets:
		bullet.draw()

	for bullet in bullets:
		bullet.draw()

	gun.draw(gun.get_angle(pygame.mouse.get_pos()))

	update_cursor(pygame.mouse.get_pos())

	screen.blit(display, (0, 0))

	pygame.display.update()

pygame.mixer.music.play(-1)

# Main Loop
while True:
	clock.tick(60)

	scroll[0] += int((player.rect.x - scroll[0] - (WINDOW_SIZE[0]/2 + player.width/2))/20)
	scroll[1] += int((player.rect.y - scroll[1] - (WINDOW_SIZE[1]/2 + player.height/2))/20)

# Events
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()

		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and len(bullets) <= 20:
			mx, my = event.pos
			slopex = mx - (player.rect.centerx - scroll[0] + 5)
			slopey = my - (player.rect.centery - scroll[1] + 35)
			bullets.append(Projectile(player.rect.centerx + 5, player.rect.centery + 35, 10, 14, 15, math.atan2(slopey, slopex), projectile_img))
			shoot_sound.play()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_d:
				player.moving_right = True
			if event.key == pygame.K_a:
				player.moving_left = True
			if event.key == pygame.K_LSHIFT:
				player.sprinting = True
			if event.key == pygame.K_SPACE or event.key == pygame.K_w:
				if player.times_jumped < 2:
					player.jumping = True
			if event.key == pygame.K_f:
				screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
			if event.key == pygame.K_ESCAPE:
				screen = pygame.display.set_mode(WINDOW_SIZE)

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_d:
				player.moving_right = False
			if event.key == pygame.K_a:
				player.moving_left = False
			if event.key == pygame.K_LSHIFT:
				player.sprinting = False
				player.vel = 10

# die conditions
	if player.rect.y >= WINDOW_SIZE[1] + 300:
		player.die()
	if player.health <= 0:
		player.die()

# player bullets
	for bullet in bullets:
		if len(bullets) <= 30:
			bullet.update()
			for enemy in enemies:
				if bullet.rect.colliderect(enemy.rect):
					if bullet in bullets:
						bullets.remove(bullet)
					enemy.health -= bullet.damage
					enemy_hit_sound.play()
					for i in range(8):
						particles.append(Particle(bullet.x, bullet.y, [(50, 50, 50), (180, 30, 30), (180, 30, 30), (150, 150, 150), (100, 0, 0)], -25, 25, -50, 0, 3, 10, 0.4, 0.2))
			if bullet.collision_types['top'] or bullet.collision_types['bottom'] or bullet.collision_types['right'] or bullet.collision_types['left']:
				if bullet in bullets:
					bullets.remove(bullet)
				explosion_sound.play()
				if bullet.collision_types['top']:
					for i in range(20):
						particles.append(Particle(bullet.x, bullet.y, [(140, 140, 140), (200, 200, 200), (100, 100, 100), (123, 54, 0)], -25, 25, 10, 60, 4, 15, 0.4, 0.2))
				if bullet.collision_types['bottom']:
					for i in range(20):
						particles.append(Particle(bullet.x, bullet.y, [(140, 140, 140), (200, 200, 200), (100, 100, 100), (123, 54, 0)], -25, 25, -60, -10, 4, 15, 0.4, 0.2))
				if bullet.collision_types['right']:
					for i in range(20):
						particles.append(Particle(bullet.x, bullet.y, [(140, 140, 140), (200, 200, 200), (100, 100, 100), (123, 54, 0)], -60, -10, -25, 25, 4, 15, 0.4, 0.2))
				if bullet.collision_types['left']:
					for i in range(20):
						particles.append(Particle(bullet.x, bullet.y, [(140, 140, 140), (200, 200, 200), (100, 100, 100), (123, 54, 0)], 10, 60, -25, 25, 4, 15, 0.4, 0.2))
		else:
			bullets.remove(bullet)

# enemy bullets
	for bullet in enemy_bullets:
		if len(enemy_bullets) <= 30:
			bullet.update()
			if bullet.rect.colliderect(player.rect):
				if bullet in enemy_bullets:
					enemy_bullets.remove(bullet)
				player.health -= bullet.damage
				player_hit_sound.play()
				for i in range(20):
					particles.append(Particle(bullet.x, bullet.y, [(50, 50, 50), (180, 30, 30), (150, 150, 150), (94, 49, 91)], -25, 25, -50, 0, 4, 15, 0.4, 0.2))
			if bullet.collision_types['top'] or bullet.collision_types['bottom'] or bullet.collision_types['right'] or bullet.collision_types['left'] and not bullet.rect.colliderect(player.rect):
				if bullet in enemy_bullets:
					enemy_bullets.remove(bullet)
				explosion_sound.play()
				if bullet.collision_types['top']:
					for i in range(23):
						particles.append(Particle(bullet.x, bullet.y, [(140, 140, 140), (100, 100, 100), (150, 54, 54)], -25, 25, 10, 60, 4, 15, 0.4, 0.2))
				if bullet.collision_types['bottom']:
					for i in range(23):
						particles.append(Particle(bullet.x, bullet.y, [(140, 140, 140), (100, 100, 100), (150, 54, 54)], -25, 25, -60, -10, 4, 15, 0.4, 0.2))
				if bullet.collision_types['right']:
					for i in range(23):
						particles.append(Particle(bullet.x, bullet.y, [(140, 140, 140), (100, 100, 100), (150, 54, 54)], -60, -10, -25, 25, 4, 15, 0.4, 0.2))
				if bullet.collision_types['left']:
					for i in range(23):
						particles.append(Particle(bullet.x, bullet.y, [(140, 140, 140), (100, 100, 100), (150, 54, 54)], 10, 60, -25, 25, 4, 15, 0.4, 0.2))
		else:
			enemy_bullets.remove(bullet)

	if player.moving_right and player.collision_types['bottom']:
		particles.append(Particle(player.rect.midbottom[0], player.rect.midbottom[1], [(60, 163, 112), (61, 111, 112), (50, 62, 79), (94, 49, 91), (140, 63, 93), (186, 97, 86)], -50, 0, 0, 5, 2, 8, 0.4, 0.2))
	if player.moving_left and player.collision_types['bottom']:
		particles.append(Particle(player.rect.midbottom[0], player.rect.midbottom[1], [(60, 163, 112), (61, 111, 112), (50, 62, 79), (94, 49, 91), (140, 63, 93), (186, 97, 86)], 0, 50, 0, 5, 2, 8, 0.4, 0.2))
	
	for particle in particles:
		particle.update()
		if particle.radius <= 0:
			particles.remove(particle)

# enemy die conditions
	for enemy in enemies:
		if enemy.health <= 0 or enemy.rect.y >= 1080:
			enemies.remove(enemy)
			enemy_death_sound.play()
			for i in range(50):
				particles.append(Particle(enemy.rect.centerx, enemy.rect.centery, [(140, 140, 140), (255, 50, 50), (255, 50, 50), (255, 50, 50), (50, 50, 50), (100, 0, 0)], -40, 40, -80, 0, 4, 15, 0.4, 0.2))
		else:
			enemy.update()

	player.update()
	gun.update()
	draw()

	# print(clock.get_fps())
