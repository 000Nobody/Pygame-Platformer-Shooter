import pygame, math, os, random, sys, time
from operator import sub
from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
clock = pygame.time.Clock()

pygame.display.set_caption('Shooter Platformer')

info_object = pygame.display.Info()
WINDOW_SIZE = (info_object.current_w, info_object.current_h)

screen = pygame.display.set_mode(WINDOW_SIZE, FULLSCREEN)

display = pygame.Surface((1920, 1080))

pygame.mouse.set_visible(False)

# Create variables
FPS = 60
last_time = time.time()
save_number = 0
main_menu = True
load_game_menu = False
game_running = False
escape_menu = False
win_screen = False
fade_out = False
fade_in = False
fade_alpha = 0
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

instruction_img = pygame.image.load('data/images/instructions.png').convert_alpha()
title_img = pygame.image.load('data/images/title_image.png').convert_alpha()
health_bar_img = pygame.image.load('data/images/health_bar.png').convert_alpha()
overlay_img = pygame.transform.scale(pygame.image.load('data/images/black_overlay.png').convert(), WINDOW_SIZE)
overlay_img.set_alpha(150)

grass = pygame.image.load('data/images/tiles/grass.png').convert()
dirt = pygame.image.load('data/images/tiles/dirt.png').convert()
middle_platform = pygame.image.load('data/images/tiles/platform_middle.png').convert_alpha()
left_edge_platform = pygame.image.load('data/images/tiles/platform_edge.png').convert_alpha()
right_edge_platform = pygame.transform.flip(pygame.image.load('data/images/tiles/platform_edge.png').convert_alpha(), True, False)
left_transition_dirt = pygame.image.load('data/images/tiles/transition_dirt.png').convert()
right_transition_dirt = pygame.transform.flip(pygame.image.load('data/images/tiles/transition_dirt.png').convert(), True, False)
left_transition_grass = pygame.image.load('data/images/tiles/transition_grass.png').convert()
right_transition_grass = pygame.transform.flip(pygame.image.load('data/images/tiles/transition_grass.png').convert(), True, False)
left_edge_dirt = pygame.image.load('data/images/tiles/edge_dirt.png').convert_alpha()
right_edge_dirt = pygame.transform.flip(pygame.image.load('data/images/tiles/edge_dirt.png').convert_alpha(), True, False)
left_edge_grass = pygame.image.load('data/images/tiles/edge_grass.png').convert_alpha()
right_edge_grass = pygame.transform.flip(pygame.image.load('data/images/tiles/edge_grass.png').convert_alpha(), True, False)
left_side_grass_transition = pygame.image.load('data/images/tiles/side_grass_transition.png').convert_alpha()
right_side_grass_transition = pygame.transform.flip(pygame.image.load('data/images/tiles/side_grass_transition.png').convert_alpha(), True, False)
left_bottom_corner_dirt = pygame.image.load('data/images/tiles/bottom_corner_dirt.png').convert_alpha()
right_bottom_corner_dirt = pygame.transform.flip(pygame.image.load('data/images/tiles/bottom_corner_dirt.png').convert_alpha(), True, False)
bottom_dirt = pygame.image.load('data/images/tiles/bottom_dirt.png').convert_alpha()

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

player_animations = load_animations(['Running', 'Idle', 'Walking'], 'player_images')
enemy_animations = load_animations(['Idle', 'Walking'], 'enemy_images')

# Load sounds
death_sound = pygame.mixer.Sound('data/sounds/death.wav')
jump_sound = pygame.mixer.Sound('data/sounds/jump.wav')
shoot_sound = pygame.mixer.Sound('data/sounds/shoot.wav')
explosion_sound = pygame.mixer.Sound('data/sounds/explosion.wav')
enemy_hit_sound = pygame.mixer.Sound('data/sounds/enemy_hit.wav')
enemy_death_sound = pygame.mixer.Sound('data/sounds/enemy_death.wav')
player_hit_sound = pygame.mixer.Sound('data/sounds/player_hit.wav')
select_sound = pygame.mixer.Sound('data/sounds/select.wav')
jump_sound.set_volume(0.8)
shoot_sound.set_volume(0.5)
explosion_sound.set_volume(0.7)
enemy_hit_sound.set_volume(0.7)
select_sound.set_volume(0.6)

# Load Fonts
pixel_font = pygame.font.Font('data/fonts/pixel_font.ttf', 30)
pixel_font_large = pygame.font.Font('data/fonts/pixel_font.ttf', 300)
title_font = pygame.font.Font('data/fonts/title_font.ttf', 75)
title_font_large = pygame.font.Font('data/fonts/title_font.ttf', 100)

# Create save file
if not os.path.isfile('saves.txt'):
    save_file = open('saves.txt', 'w+')

#Classes
class Level():
    def __init__(self, map_name, player_pos, enemy_pos, die_height):
        self.player_pos = player_pos
        self.enemy_pos = enemy_pos
        self.tile_size = (64, 64)
        self.map_name = map_name
        self.die_height = die_height
        self.path = 'data/maps/{}.txt'.format(self.map_name)
        self.timer = 0

    def load_map(self):
        self.map = []
        with open(self.path, 'r') as f:
            data = f.read()
            data = data.split('\n')
            for row in data:
                self.map.append(list(row))

    def create_map_hitbox(self):
        global tile_rects
        tile_rects = []
        y = 0
        for layer in self.map:
            x = 0
            for tile in layer:
                if tile != '0':
                    tile_rects.append(pygame.Rect(int(x), int(y), self.tile_size[0], self.tile_size[1]))
                x += self.tile_size[0]
            y += self.tile_size[1]

    def draw(self):
        y = 0
        for layer in self.map:
            x = 0
            for tile in layer:
                if tile == '1':
                    display.blit(pygame.transform.scale(grass, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == '2':
                    display.blit(pygame.transform.scale(dirt, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == '3':
                    display.blit(pygame.transform.scale(left_edge_dirt, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == '4':
                    display.blit(pygame.transform.scale(right_edge_dirt, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == '5':
                    display.blit(pygame.transform.scale(left_edge_grass, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == '6':
                    display.blit(pygame.transform.scale(right_edge_grass, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == '7':
                    display.blit(pygame.transform.scale(left_edge_platform, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == '8':
                    display.blit(pygame.transform.scale(middle_platform, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == '9':
                    display.blit(pygame.transform.scale(right_edge_platform, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == 'a':
                    display.blit(pygame.transform.scale(left_transition_dirt, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == 'b':
                    display.blit(pygame.transform.scale(right_transition_dirt, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))    
                elif tile == 'c':
                    display.blit(pygame.transform.scale(left_transition_grass, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))            
                elif tile == 'd':
                    display.blit(pygame.transform.scale(right_transition_grass, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == 'e':
                    display.blit(pygame.transform.scale(left_side_grass_transition, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == 'f':
                    display.blit(pygame.transform.scale(right_side_grass_transition, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == 'g':
                    display.blit(pygame.transform.scale(left_bottom_corner_dirt, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == 'h':
                    display.blit(pygame.transform.scale(right_bottom_corner_dirt, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                elif tile == 'i':
                    display.blit(pygame.transform.scale(bottom_dirt, (self.tile_size[0], self.tile_size[1])), (x - scroll[0], y - scroll[1]))
                x += self.tile_size[0]
            y += self.tile_size[1]

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
        self.level = 'Tutorial'
        self.times_jumped = 0
        self.animation_database = player_animations
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
                particles.append(Particle(player.rect.midbottom[0], player.rect.midbottom[1], [(150, 150, 150), (225, 225, 225), (200, 200, 200)], -40, 40, -5, 0, 4, 10, 0.8, 0.2))
            self.jumping = False

        if not self.moving_left and not self.moving_right:
            self.movement = [0, 0]
        self.movement[1] = self.vertical_momentum

        self.rect, self.collision_types, self.hit_list = move(self.rect, tile_rects, self.movement)

        self.vertical_momentum += gravity_strength * dt
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
        self.rect.topleft = levels[self.level].player_pos
        enemies.clear()
        bullets.clear()
        particles.clear()
        enemy_bullets.clear()
        enemy_id_counter = 0
        for enemy_pos in levels[self.level].enemy_pos:
            enemies.append(Enemy(enemy_id_counter, enemy_pos, 75, 125, 100, 900, 900))
            enemy_id_counter += 1
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
        #update save file
        save_data = get_saves()
        save_data[save_number] = new_level
        save_data_string = ''
        for i in save_data:
            save_data_string += i + ','

        with open('saves.txt', 'w') as f:
            f.write(save_data_string)
            f.close()

        #reset everything
        enemies.clear()
        particles.clear()
        bullets.clear()
        enemy_bullets.clear()
        levels[new_level].create_map_hitbox()
        timer = 0
        self.health = 100
        self.level = new_level
        self.rect.topleft = levels[new_level].player_pos
        for enemy_pos in levels[new_level].enemy_pos:
            enemies.append(Enemy(enemy_id_counter, enemy_pos, 75, 125, 100, 900, 900))

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
        self.animation_database = enemy_animations
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

        self.rect, self.collision_types, self.hit_list = move(self.rect, tile_rects
                                                              + [enemy.rect for enemy in enemies if enemy.id != self.id], self.movement)

        self.vertical_momentum += gravity_strength * dt
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
        self.shoot_timer += 1 * dt
        if math.sqrt(abs((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2)) <= self.attack_range:
            if self.shoot_timer >= 60:
                self.slopex = (player.rect.centerx - scroll[0]) - (self.rect.centerx - scroll[0] + 5)
                self.slopey = (player.rect.centery - scroll[1]) - (self.rect.centery - scroll[1] + 35)
                enemy_bullets.append(Projectile(self.rect.centerx + 5, self.rect.centery + 35, 15, 17, 35,
                                     math.atan2(self.slopey, self.slopex), enemy_projectile_img))
                self.shoot_timer = 0
        if self.rect.colliderect(player.rect):
            player.health -= 2

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

        if not [enemy for enemy in enemies if enemy.id != self.id and enemy.rect in self.hit_list]:
            if self.collision_types['left'] or self.collision_types['right']:
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
        self.x += math.cos(self.angle) * self.vel * dt
        self.y += math.sin(self.angle) * self.vel * dt

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
    def __init__(self, x, y, colors, min_xvel, max_xvel, min_yvel,
                 max_yvel, min_radius, max_radius, shrink_rate, gravity):
        self.x = x
        self.y = y
        self.color = random.choice(colors)
        self.xvel = random.randint(min_xvel, max_xvel) / 10
        self.yvel = random.randint(min_yvel, max_yvel) / 10
        self.radius = random.randint(min_radius, max_radius)
        self.shrink_rate = shrink_rate
        self.gravity = gravity

    def update(self):
        self.x += self.xvel * dt
        self.y += self.yvel * dt
        self.radius -= self.shrink_rate * dt
        self.yvel += self.gravity * dt

    def draw(self):
        pygame.draw.circle(display, self.color, (int(self.x - scroll[0]), int(self.y - scroll[1])), int(self.radius))

class Button():
    def __init__(self, x, y, width, height, color, text, text_color, font):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.pressed_color = tuple(map(sub, self.color, (50, 50, 50)))
        self.text = text
        self.text_color = text_color
        self.font = font

    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.rendered_text = pixel_font.render(self.text, 1, self.text_color)
        self.text_rect = self.rendered_text.get_rect()
        self.text_rect.center = self.rect.center

    def is_over(self):
        mx, my = pygame.mouse.get_pos()
        if self.x < mx < self.x + self.width and self.y < my < self.y + self.height:
            return True
        else:
            return False

    def draw(self):
        mx, my = pygame.mouse.get_pos()
        if self.is_over():
            pygame.draw.rect(display, self.pressed_color, self.rect)
        else:
            pygame.draw.rect(display, self.color, self.rect)
        pygame.draw.rect(display, self.text_color, self.rect, 5)
        display.blit(self.rendered_text, (self.text_rect.x, self.text_rect.y))

# Create classes
levels = {'Tutorial':Level('map0', (600, 490), [(2940, 250)], 1400),
          'Level 1':Level('map1', (830, -100), [(140, -145), (5375, 280), (7215, 345)], 800),
          'Level 2':Level('map2', (600, 800), [(255, 445), (1695, -130), (3925, 380), (3915, 0)], 1900),
          'Level 3':Level('map3', (50, 400), [(1790, 400), (3125, 100)], 1000),
          'Level 4':Level('map4', (295, 100), [(1105, 480), (1855, 600), (3935, 675), (4385, 925), (5045, 850)], 1500),
          'Level 5':Level('map5', (165, -200), [(4865, 350), (5720, 550), (8205, 350), (10690, 550)], 1500)} 
for level in levels:
    levels[level].load_map()

player = Player(75, 125, 10, 28, 100)

enemy_id_counter = 0
for enemy_pos in levels[player.level].enemy_pos:
    enemies.append(Enemy(enemy_id_counter, enemy_pos, 75, 125, 100, 900, 900))
    enemy_id_counter += 1

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
    rect.x += movement[0] * dt
    hit_list = collision_check(rect, tiles)
    for tile in hit_list:
        if movement[0] * dt > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] * dt < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1] * dt
    hit_list = collision_check(rect, tiles)
    for tile in hit_list:
        if movement[1] * dt > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] * dt < 0:
            rect.top = tile.bottom
            collision_types['top'] = True

    return rect, collision_types, hit_list

def get_saves():
    with open('saves.txt', 'r') as f:
        save_data = f.read()
        f.close()
    save_data = save_data.split(',')
    save_data = save_data[:-1]
    return save_data

def update_cursor(mousepos):
    cursor_rect = cursor.get_rect()
    mx, my = mousepos
    mx *= (WINDOW_SIZE[0]/1920)
    my *= (WINDOW_SIZE[1]/1080)
    cursor_rect.center = (mx, my)
    screen.blit(cursor, cursor_rect)

def play_bgmusic():
    pygame.mixer.music.load('data/sounds/bgmusic.wav')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.6)

def play_menu_music():
    pygame.mixer.music.load('data/sounds/menu_music.wav')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)

def play_win_music():
    pygame.mixer.music.load('data/sounds/win_music.wav')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.4)

def draw_main_menu():
    display.fill((180, 235, 235))

    new_game_button.draw()
    load_game_button.draw()
    exit_button.draw()
    display.blit(title_img, (250, 0))

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))

    update_cursor(pygame.mouse.get_pos())

    pygame.display.update()

def draw_load_game_menu():
    display.fill((180, 235, 235))

    for button in save_buttons:
        button.draw()

    for button in delete_save_buttons:
        button.draw()

    back_button.draw()

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))

    update_cursor(pygame.mouse.get_pos())

    pygame.display.update()

def draw_win_screen():
    display.fill((180, 235, 235))

    congrats_text = title_font_large.render("Congratulations!", 1, (0, 0, 0))
    you_win_text = title_font.render("You have beaten the game!", 1, (0, 0, 0))
    display.blit(congrats_text, (190, 150))
    display.blit(you_win_text, (40, 300))

    win_main_menu_button.draw()
    win_exit_button.draw()

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))

    update_cursor(pygame.mouse.get_pos())

    pygame.display.update()

def draw():
    global fade_out, fade_in, fade_alpha
    display.fill((180, 235, 235))

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

    if player.level == 'Tutorial':
        display.blit(instruction_img, (380 - scroll[0], 380 - scroll[1]))

    health_bar_rect = pygame.Rect(94, 1028, player.health*2, 19)
    pygame.draw.rect(display, (255, 0, 0), health_bar_rect)
    display.blit(health_bar_img, (30, 1000))

    level_text = pixel_font.render(player.level, 1, (0, 0, 0))
    time_text = pixel_font.render(str(round(levels[player.level].timer, 2)), 1, (0, 0, 0))
    display.blit(level_text, (30, 30))
    display.blit(time_text, (30, 60))

    def draw_escape_menu():
        resume_button = Button(710, 265, 500, 150, (50, 200, 50), "Resume Game", (0, 0, 0), pixel_font_large)
        main_menu_button = Button(710, 465, 500, 150, (75, 160, 173), "Go to Main Menu", (0, 0, 0), pixel_font_large)
        exit_fullscreen_button = Button(710, 665, 500, 150, (255, 50, 50), "Exit Fullscreen", (0, 0, 0), pixel_font_large)

        resume_button.update()
        main_menu_button.update()
        exit_fullscreen_button.update()

        display.blit(overlay_img, (0, 0))

        resume_button.draw()
        main_menu_button.draw()
        exit_fullscreen_button.draw()

    if escape_menu:
        draw_escape_menu()

    if fade_out:
        fade_alpha += 7
        fade_surface = pygame.Surface(WINDOW_SIZE)
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(fade_alpha)
        display.blit(fade_surface, (0, 0))
        if fade_alpha >= 300:
            fade_out = False

    if fade_in:
        fade_alpha -= 7
        fade_surface = pygame.Surface(WINDOW_SIZE)
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(fade_alpha)
        display.blit(fade_surface, (0, 0))
        if fade_alpha <= 0:
            fade_in = False

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))

    update_cursor(pygame.mouse.get_pos())

    pygame.display.update()

# Main Loop
play_menu_music()
while True:
    clock.tick()
    dt = time.time() - last_time
    dt *= FPS
    last_time = time.time()

    if main_menu:
        new_game_button = Button(560, 550, 800, 200, (75, 173, 89), "New Game", (0, 0, 0), pixel_font_large)
        exit_button = Button(1500, 900, 300, 100, (255, 50, 50), "Exit to desktop", (0, 0, 0), pixel_font_large)
        load_game_button = Button(560, 800, 800, 200, (75, 160, 173), "Load Game ({}/9)".format(len(get_saves())), (0, 0, 0), pixel_font_large)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == pygame.K_f:
                    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
                if event.key == pygame.K_ESCAPE:
                    screen = pygame.display.set_mode(WINDOW_SIZE)

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if exit_button.is_over():
                        select_sound.play()
                        sys.exit()
                        pygame.quit()
                    if new_game_button.is_over():
                        with open('saves.txt', 'r+') as f:
                            save_data = f.read()
                            save_data = save_data.split(',')
                            if len(save_data) < 9:
                                f.write('Tutorial,')
                                f.close()
                                save_number = len(save_data) - 1
                                player.change_level('Tutorial')
                                game_running = True
                                main_menu = False
                                select_sound.play()
                                play_bgmusic()
                    if load_game_button.is_over():
                        load_game_menu = True
                        main_menu = False
                        select_sound.play()

        new_game_button.update()
        load_game_button.update()
        exit_button.update()
        draw_main_menu()

    if load_game_menu:
        save_buttons = []
        delete_save_buttons = []
        game_counter = 1
        save_button_y = 50
        for save in get_saves():
            save_buttons.append(Button(612, save_button_y, 400, 90, (255, 255, 255), "Game {}: {}".format(game_counter, save), (0, 0, 0), pixel_font_large))
            delete_save_buttons.append(Button(1032, save_button_y, 275, 90, (255, 50, 50), "Delete Game {}".format(game_counter), (0, 0, 0), pixel_font_large))
            game_counter += 1
            save_button_y += 110

        back_button = Button(1500, 930, 200, 90, (255, 50, 50), "Back", (0, 0, 0), pixel_font_large)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == pygame.K_f:
                    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
                if event.key == pygame.K_ESCAPE:
                    screen = pygame.display.set_mode(WINDOW_SIZE)

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if back_button.is_over():
                        load_game_menu = False
                        main_menu = True
                        select_sound.play()
                    for i, button in enumerate(save_buttons):
                        if button.is_over():
                            save_number = i
                            save_data = get_saves()
                            player.change_level(save_data[save_number])
                            load_game_menu = False
                            game_running = True
                            select_sound.play()
                            play_bgmusic()
                    for i, button in enumerate(delete_save_buttons):
                        if button.is_over():
                            select_sound.play()
                            save_data = get_saves()
                            save_data.pop(i)
                            save_data_string = ''
                            for save in save_data:
                                save_data_string += save + ','

                            with open('saves.txt', 'w') as f:
                                f.write(save_data_string)
                                f.close()

        for button in save_buttons:
            button.update()
        for button in delete_save_buttons:
            button.update()
        back_button.update()
        draw_load_game_menu()

    if escape_menu:
        resume_button = Button(710, 265, 500, 150, (50, 200, 50), "Resume Game", (0, 0, 0), pixel_font_large)
        main_menu_button = Button(710, 465, 500, 150, (75, 160, 173), "Go to Main Menu", (0, 0, 0), pixel_font_large)
        exit_fullscreen_button = Button(710, 665, 500, 150, (255, 50, 50), "Exit Fullscreen", (0, 0, 0), pixel_font_large)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    escape_menu = False
                if event.key == pygame.K_f:
                    screen = pygame.display.set_mode(WINDOW_SIZE, FULLSCREEN)

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if resume_button.is_over():
                        escape_menu = False
                        select_sound.play()
                    if main_menu_button.is_over():
                        escape_menu = False
                        game_running = False
                        main_menu = True
                        select_sound.play()
                        play_menu_music()
                    if exit_fullscreen_button.is_over():
                        screen = pygame.display.set_mode(WINDOW_SIZE)
                        select_sound.play()

    if win_screen:
        win_main_menu_button = Button(560, 550, 800, 200, (75, 173, 89), "Return to Main Menu", (0, 0, 0), pixel_font_large)
        win_exit_button = Button(560, 800, 800, 200, (255, 50, 50), "Exit to desktop", (0, 0, 0), pixel_font_large)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == pygame.K_f:
                    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
                if event.key == pygame.K_ESCAPE:
                    screen = pygame.display.set_mode(WINDOW_SIZE)

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if win_main_menu_button.is_over():
                        win_screen = False
                        main_menu = True
                        select_sound.play()
                        play_menu_music()
                    if win_exit_button.is_over():
                        select_sound.play()
                        pygame.quit()
                        sys.exit()

        win_main_menu_button.update()
        win_exit_button.update()
        draw_win_screen()

    levels[player.level].create_map_hitbox()
    if game_running:
        levels[player.level].timer += round((FPS/clock.get_fps())/100, 2)

        scroll[0] += int((player.rect.x - scroll[0] - (WINDOW_SIZE[0]/2 + player.width/2))/18) * dt
        scroll[1] += int((player.rect.y - scroll[1] - (WINDOW_SIZE[1]/2 + player.height/2))/18) * dt

    # Events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and len(bullets) <= 20:
                    mx, my = event.pos
                    slopex = mx - (player.rect.centerx - scroll[0] + 5)
                    slopey = my - (player.rect.centery - scroll[1] + 35)
                    bullets.append(Projectile(player.rect.centerx + 5, player.rect.centery + 35, 10, 14, 15, math.atan2(slopey, slopex), projectile_img))
                    shoot_sound.play()

            if event.type == KEYDOWN:
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
                    escape_menu = True

            if event.type == KEYUP:
                if event.key == pygame.K_d:
                    player.moving_right = False
                if event.key == pygame.K_a:
                    player.moving_left = False
                if event.key == pygame.K_LSHIFT:
                    player.sprinting = False
                    player.vel = 10

    # die conditions
        if player.rect.y >= levels[player.level].die_height:
            player.die()
        if player.health <= 0:
            player.die()

    # level-change conditions
        if player.level == 'Tutorial':
            if enemies == []:
                fade_out = True
                pygame.mixer.music.fadeout(1000)
                if fade_alpha >= 300:
                    fade_in = True
                    play_bgmusic()
                    player.change_level('Level 1')
        elif player.level == 'Level 1':
            if enemies == []:
                fade_out = True
                pygame.mixer.music.fadeout(1000)
                if fade_alpha >= 300:
                    fade_in = True
                    play_bgmusic()
                    player.change_level('Level 2')
        elif player.level == 'Level 2':
            if enemies == []:
                fade_out = True
                pygame.mixer.music.fadeout(1000)
                if fade_alpha >= 300:
                    fade_in = True
                    play_bgmusic()
                    player.change_level('Level 3')
        elif player.level == 'Level 3':
            if enemies == []:
                fade_out = True
                pygame.mixer.music.fadeout(1000)
                if fade_alpha >= 300:
                    fade_in = True
                    play_bgmusic()
                    player.change_level('Level 4')
        elif player.level == 'Level 4':
            if enemies == []:
                fade_out = True
                pygame.mixer.music.fadeout(1000)
                if fade_alpha >= 300:
                    fade_in = True
                    play_bgmusic()
                    player.change_level('Level 5')
        elif player.level == 'Level 5':
            if enemies == []:
                pygame.mixer.music.fadeout(1000)
                game_running = False
                win_screen = True
                play_win_music()

    # player bullets
        for bullet in bullets:
            if len(bullets) <= 20:
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
            if len(enemy_bullets) <= 40:
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
            particles.append(Particle(player.rect.midbottom[0], player.rect.midbottom[1], [(199, 222, 90), (180, 207, 42), (110, 162, 38), (144, 88, 51), (123, 71, 32), (98, 57, 27)], -50, 0, 0, 5, 2, 8, 0.4, 0.2))
        if player.moving_left and player.collision_types['bottom']:
            particles.append(Particle(player.rect.midbottom[0], player.rect.midbottom[1], [(199, 222, 90), (180, 207, 42), (110, 162, 38), (144, 88, 51), (123, 71, 32), (98, 57, 27)], 0, 50, 0, 5, 2, 8, 0.4, 0.2))
        
        for particle in particles:
            particle.update()
            if particle.radius <= 0:
                particles.remove(particle)

    # enemy die conditions
        for enemy in enemies:
            if enemy.health <= 0 or enemy.rect.y >= levels[player.level].die_height:
                enemies.remove(enemy)
                enemy_death_sound.play()
                for i in range(50):
                    particles.append(Particle(enemy.rect.centerx, enemy.rect.centery, [(140, 140, 140), (255, 50, 50), (255, 50, 50), (255, 50, 50), (50, 50, 50), (100, 0, 0)], -40, 40, -80, 0, 4, 15, 0.4, 0.2))
            else:
                enemy.update()

        player.update()
        gun.update()
        draw()
