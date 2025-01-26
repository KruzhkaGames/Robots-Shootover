import pygame
import pymunk.pygame_util
import os, math, random

pygame.init()
size = w, h = 1200, 800
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Robots' Shootover 0.0.8")

pymunk.pygame_util.positive_y_is_up=False

draw_options = pymunk.pygame_util.DrawOptions(screen)
draw_options.flags = pymunk.SpaceDebugDrawOptions.DRAW_SHAPES
space = pymunk.Space()
space.gravity = 0, 2000


class Line:
    def __init__(self, type, *args):
        obj = None

        if type == 'static':
            x, y, width, elasticity, friction, color = args
            obj = [None, pymunk.Segment(space.static_body, x, y, width)]
            space.add(obj[1])
            obj[1].elasticity = elasticity
            obj[1].friction = friction
            obj[1].color = [color[0], color[1], color[2], 255]
        
        if type == 'dynamic':
            mass, rela, position, width, elasticity, friction, color = args
            moment = pymunk.moment_for_segment(mass, rela[0], rela[1], width)
            body = pymunk.Body(mass, moment)
            obj = [body, pymunk.Segment(body, rela[0], rela[1], width)]
            space.add(*obj)
            obj[0].position = position
            obj[1].elasticity = elasticity
            obj[1].friction = friction
            obj[1].color = [color[0], color[1], color[2], 255]
        
        self.object = obj


class Rect:
    def __init__(self, type, *args):
        obj = None

        if type == 'kinematic':
            mass, size, pos, elasticity, friction, color = args
            obj = [pymunk.Body(mass, size, body_type=pymunk.Body.KINEMATIC), None]
            obj[1] = pymunk.Poly.create_box(obj[0], size)
            obj[0].position = pos
            obj[1].elasticity = elasticity
            obj[1].friction = friction
            obj[1].color = [color[0], color[1], color[2], 255]
            space.add(*obj)

        elif type == 'dynamic':
            mass, size, pos, elasticity, friction, color = args
            moment = pymunk.moment_for_box(mass, size)
            obj = [pymunk.Body(mass, moment), None]
            obj[1] = pymunk.Poly.create_box(obj[0], size)
            obj[0].position = pos
            obj[1].elasticity = elasticity
            obj[1].friction = friction
            obj[1].color = [color[0], color[1], color[2], 255]
            space.add(*obj)

        self.object = obj


class Circle:
    def __init__(self, type, *args):
        obj = None

        if type == 'dynamic':
            mass, size, pos, elasticity, friction, color = args
            body = pymunk.Body(mass, size, body_type=pymunk.Body.DYNAMIC)
            shape = pymunk.Circle(body, size)
            obj = [body, shape]
            obj[0].position = pos
            obj[1].elasticity = elasticity
            obj[1].friction = friction
            obj[1].color = [color[0], color[1], color[2], 255]
            space.add(*obj)

        self.object = obj


class Polygon:
    def __init__(self, type, *args):
        obj = None

        if type == 'dynamic':
            mass, positions, position, elasticity, friction, color = args
            square_mass, square_size = mass, positions
            square_moment = pymunk.moment_for_poly(square_mass, square_size)
            obj = [pymunk.Body(square_mass, square_moment), None]
            obj[1] = pymunk.Poly(obj[0], square_size)
            obj[0].position = position
            obj[1].elasticity = elasticity
            obj[1].friction = friction
            obj[1].color = [color[0], color[1], color[2], 255]
            space.add(*obj)
        
        self.object = obj


class Connection:
    def __init__(self, type, *args):
        obj = None
        
        if type == 'groove':
            first, second, f_pos, s_pos, b_pos = args
            obj = pymunk.GrooveJoint(first, second, f_pos, s_pos, b_pos)
            space.add(obj)
        
        elif type == 'slide':
            first, second, f_pos, s_pos, min_slide, max_slide = args
            obj = pymunk.SlideJoint(first, second, f_pos, s_pos, min_slide, max_slide)
            space.add(obj)
        
        elif type == 'pin':
            first, second, f_pos, s_pos = args
            obj = pymunk.PinJoint(first, second, f_pos, s_pos)
            space.add(obj)
        
        elif type == 'pivot':
            first, second, f_pos, s_pos = args
            obj = pymunk.PivotJoint(first, second, f_pos, s_pos)
            space.add(obj)
        
        self.object = obj


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print('File not found')
        quit()
        return
    image = pygame.image.load(fullname)
    if colorkey is not None:
        color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def circle_collides_flat(x, y, blocks):
    for block in blocks:
        if y + 35 >= block[0].object[0].position[1] - block[2] / 2 and y + 35 <= block[0].object[0].position[1] + block[2] / 2 and x >= block[0].object[0].position[0] - block[1] / 2 and x <= block[0].object[0].position[0] + block[1] / 2:
            return True
    
    if y + 35 >= elevator_objects[0].object[0].position[1] - 10 and y + 35 <= elevator_objects[0].object[0].position[1] + 10 and x >= elevator_objects[0].object[0].position[0] - 150 and x <= elevator_objects[0].object[0].position[0] + 150:
        return True
    
    point = space.point_query_nearest((x, y + 35), 10000, pymunk.ShapeFilter(mask=0b000010))
    if point is not None:
        if point.shape in [enemy[0].object[1] for enemy in enemies] and point.distance < 0:
            return True
        
    return False

def create_block(x, y, sx, sy, color):
    global blocks
    blocks.append([Rect('kinematic', 10, (sx, sy), (x + sx / 2, y + sy / 2), 1, 1, color), sx, sy])
    blocks[-1][0].object[1].filter = pymunk.ShapeFilter(categories=0b010000, mask=0b101111)

def fix_to_bounds(fpos):
    pos = list(fpos)
    if pos[0] < 5:
        pos[0] = 5
    elif pos[0] > 1195:
        pos[0] = 1195
    if pos[1] < 5:
        pos[1] = 5
    elif pos[1] > 795:
        pos[1] = 795 
    return pos

def add_enemy(x, y):
    global enemies
    enemy = []
    enemy.append(Rect('dynamic', 2, (100, 100), (x, y), 0.1, 0.1, (255, 0, 0)))
    enemy.append(Rect('dynamic', 1, (10, 50), (x + 50, y + 75), 0.1, 0.1, (0, 0, 0)))
    enemy.append(Connection('pivot', enemy[0].object[0], enemy[1].object[0], (0, 0), (0, -25)))
    enemy.append(Connection('slide', enemy[0].object[0], enemy[1].object[0], (0, 0), (0, 0), 0, 25))
    enemy[0].object[1].filter = pymunk.ShapeFilter(categories=0b000010, mask=0b011011)
    enemy[1].object[1].filter = pymunk.ShapeFilter(categories=0b001000, mask=0b010001)
    enemy.append([0, 0])
    enemy.append(180)
    enemies.append(enemy)

with open('data/levels.txt') as f:
    levels = eval(f.read())
room = 0
elevator_door = (0, 0)
elevator_door_opening = 0
switching = 0
is_elevator = False
elevator_door_closing = 0
closed_door = False
switching_to_level = 0
score = 1

def generate_level():
    global blocks, enemies, player_objects, room, elevator_door, levels, room, elevator_objects, score

    room = random.randint(0, len(levels) - 1)
    level = levels[room]
    elevator_door = level[2]
    blocks.append([Rect('kinematic', 10, (100, 800), (1245, -300 + elevator_door), 1, 1, (150, 150, 150)), 100, 800])
    blocks.append([Rect('kinematic', 10, (100, 800), (1245, 500 + elevator_door), 1, 1, (150, 150, 150)), 100, 800])

    blocks.append([Rect('kinematic', 10, (1200, 100), (600, 845), 1, 1, (150, 150, 150)), 1200, 100])
    blocks.append([Rect('kinematic', 10, (40, 800), (-15, 400), 1, 1, (150, 150, 150)), 40, 800])
    blocks.append([Rect('kinematic', 10, (1200, 100), (600, -45), 1, 1, (150, 150, 150)), 1200, 100])

    for block in level[0]:
        create_block(*block)
    for enemy in level[1]:
        add_enemy(*enemy)

    room += 1

    create_block(1200, -200, 95, 200, (150, 150, 150))
    create_block(1200, 750, 1200, 50, (150, 150, 150))
    create_block(1200, 0, 800, 50, (150, 150, 150))
    create_block(1200, -200, 1200, 50, (150, 150, 150))
    create_block(2335, 0, 65, 800, (150, 150, 150))
    create_block(1965, -300, 50, 800, (150, 150, 150))

    elevator_objects.append(Rect('dynamic', 10, (300, 20), (2175, 740), 0.1, 5, (200, 200, 200)))
    elevator_objects.append(Connection('slide', elevator_objects[0].object[0], blocks[-3][0].object[0], (-150, 0), (225, 0), 0, 1500))
    elevator_objects.append(Connection('slide', elevator_objects[0].object[0], blocks[-3][0].object[0], (150, 0), (525, 0), 0, 1500))



all_objects = []
player_objects = []
blocks = []
elevator_objects = []

player_objects.append(Circle('dynamic', 5, 25, (100, 180), 0.2, 100, (0, 0, 255)))
player_objects.append(Rect('dynamic', 0.5, (50, 100), (100, 130), 0.1, 0.2, (0, 0, 255)))
player_objects.append(Connection('groove', player_objects[1].object[0], player_objects[0].object[0], (0, 50), (0, 100), (0, 0)))
player_objects.append(Rect('dynamic', 0.5, (10, 50), (100, 130), 0, 0, (0, 0, 0)))
player_objects.append(Connection('pivot', player_objects[3].object[0], player_objects[1].object[0], (0, -25), (0, 0)))
player_objects.append(Connection('slide', player_objects[3].object[0], player_objects[1].object[0], (0, 0), (0, 0), 0, 25))
player_objects[0].object[1].filter = pymunk.ShapeFilter(categories=0b000001, mask=0b010010)
player_objects[1].object[1].filter = pymunk.ShapeFilter(categories=0b000001, mask=0b010010)
player_objects[3].object[1].filter = pymunk.ShapeFilter(categories=0b000001, mask=0b010010)

rope = False
del_rope = False
rope_length = 0
rope_pos = (0, 0)
targeting = (0, 0)
is_enemy = False
enemy_index = -1

bullets = []

weapon = 0
WEAPONS = ('Крюк', 'Пистолет', 'Дробовик')
opened_weapons = [0]
weapon_reload = 0
just_shooted = False
shoot_particles = []
show_weapons = 20

auto_slowmo = True
auto_slowmo_wait = 0
do_slowmo = False
slowmo = 1
current_slowmo = 1

camera_shaking = 0
last_body_vel = (0, 0)

enemies = []
enemy_bullets = []

move = [False, False, False, False]
player_health = 100
current_player_health = 100

stuffs = []

closing_elevator = 0
elevator = 0
launched_elevator = False

clock = pygame.time.Clock()
fps = 60
font = pygame.font.Font(None, 100)
font1 = pygame.font.Font(None, 50)

running = True

generate_level()

enemies_to_destroy = []


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image('robot.png'), (50, 100))
    
    def update(self):
        self.image = pygame.transform.rotate(pygame.transform.flip(pygame.transform.scale(load_image('robot.png'), (50, 100)), player_objects[1].object[0].velocity[0] < 0, False), -math.degrees(player_objects[1].object[0].angle))
        self.rect = self.image.get_rect(center=player_objects[1].object[0].position)


class Wheel(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image('wheel.png'), (50, 50))
    
    def update(self):
        self.image = pygame.transform.rotate(pygame.transform.scale(load_image('wheel.png'), (50, 50)), -math.degrees(player_objects[0].object[0].angle))
        self.rect = self.image.get_rect(center=player_objects[0].object[0].position)


class Gun(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image('grap.png'), (20, 100))
    
    def update(self):
        self.image = pygame.transform.rotate(pygame.transform.flip(pygame.transform.scale(load_image(('grap', 'gun', 'shotgun')[weapon] + '.png'), (20, 100)), math.degrees(player_objects[3].object[0].angle) % 360 < 180, False), -math.degrees(player_objects[3].object[0].angle))
        self.rect = self.image.get_rect(center=player_objects[3].object[0].position)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, shape):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image('enemy.png'), (100, 100))
        self.shape = shape
        self.index = [enemy[0].object[1] for enemy in enemies].index(self.shape)
    
    def update(self):
        if self.index in enemies_to_destroy:
            all_sprites.remove(self)
        else:
            self.index = [enemy[0].object[1] for enemy in enemies].index(self.shape)
            self.image = pygame.transform.rotate(pygame.transform.flip(pygame.transform.scale(load_image('enemy.png'), (100, 100)), player_objects[1].object[0].position[0] < enemies[self.index][0].object[0].position[0], False), -math.degrees(enemies[self.index][0].object[0].angle))
            self.rect = self.image.get_rect(center=enemies[self.index][0].object[0].position)


class Enemy_gun(pygame.sprite.Sprite):
    def __init__(self, shape):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image('gun.png'), (20, 100))
        self.shape = shape
        self.index = [enemy[1].object[1] for enemy in enemies].index(self.shape)
    
    def update(self):
        if self.index in enemies_to_destroy:
            all_sprites.remove(self)
            del enemies_to_destroy[enemies_to_destroy.index(self.index)]
        else:
            self.index = [enemy[1].object[1] for enemy in enemies].index(self.shape)
            self.image = pygame.transform.rotate(pygame.transform.flip(pygame.transform.scale(load_image('gun.png'), (20, 100)), math.degrees(enemies[self.index][1].object[0].angle) % 360 < 180, False), -math.degrees(enemies[self.index][1].object[0].angle))
            self.rect = self.image.get_rect(center=enemies[self.index][1].object[0].position)


class Slowmo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(slowmo_group)
        self.real_im = load_image('slowmo.png')
        self.image = pygame.transform.scale(self.real_im, (1200, 800))
    
    def update(self):
        self.image = pygame.transform.scale(self.real_im, (1200 * (3 - current_slowmo), 800 * (3 - current_slowmo)))
        self.rect = self.image.get_rect()
        self.rect.x = -600 * (2 - current_slowmo)
        self.rect.y = -400 * (2 - current_slowmo)


class Weapon_sprite(pygame.sprite.Sprite):
    def __init__(self, index):
        super().__init__(weapon_sprites)
        self.index = index
        self.real_im = pygame.Surface((50, 50))
        self.real_im.fill((220, 220, 220))
        pygame.draw.rect(self.real_im, (255, 255, 255), (3, 3, 44, 44))
        self.real_im.blit(pygame.transform.chop(pygame.transform.scale(load_image(('grap.png', 'gun.png', 'shotgun.png')[index]), (20, 100)), (0, 0, 0, 50)), (15, -3))
        self.real_im = pygame.transform.rotate(self.real_im, 90)
        self.image = self.real_im
    
    def update(self):
        if abs(weapon - self.index) == 1:
            self.image = pygame.transform.scale(self.real_im, (70, 70))
            self.rect = self.image.get_rect()
            self.rect.x = 25 + 200 * int(self.index > weapon)
            self.rect.y = 25
        elif abs(weapon - self.index) == len(WEAPONS) - 1:
            self.image = pygame.transform.scale(self.real_im, (70, 70))
            self.rect = self.image.get_rect()
            self.rect.x = 25 + 200 * int(self.index < weapon)
            self.rect.y = 25
        elif weapon == self.index:
            self.image = pygame.transform.scale(self.real_im, (100, 100))
            self.rect = self.image.get_rect()
            self.rect.x = 110
            self.rect.y = 10
        else:
            self.image = self.real_im
            self.rect = self.image.get_rect()
            self.rect.x = -100
            self.rect.y = 0
        
        if show_weapons > 40:
            self.rect.y = -100 + (self.rect.y - 10) + 110 * (1 - (show_weapons - 40) / 10)
        elif show_weapons < 10:
            self.rect.y = -100 + (self.rect.y - 10) + 11 * (show_weapons)


class Elevator(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image('elevator.png'), (300, 120))
    
    def update(self):
        self.image = pygame.transform.rotate(pygame.transform.scale(load_image('elevator.png'), (300, 150)), -math.degrees(elevator_objects[0].object[0].angle))
        self.rect = self.image.get_rect(center=elevator_objects[0].object[0].position)


class Door(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(slowmo_group)
        self.image = pygame.transform.scale(load_image('door.png'), (1200, 800))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = -800
    
    def update(self):
        self.image.fill((50, 50, 50), (0, 200, 1200, 400))
        text = font.render(str(score), True, (200, 200, 200))
        sz = text.get_size()
        self.image.blit(text, (600 - sz[0] / 2, 400 - sz[1] / 2))
        if switching_to_level > 0:
            self.rect.y = 0
            self.rect.x = switching_to_level
        elif switching_to_level < 0 and switching_to_level >= -25:
            self.rect.y = -32 * (25 - abs(switching_to_level))
            self.rect.x = 0
        elif switching_to_level < -25:
            self.rect.y = 0
            self.rect.x = 0
        else:
            self.rect.y = -800
            self.rect.x = 0


all_sprites = pygame.sprite.Group()
slowmo_group = pygame.sprite.Group()
weapon_sprites = pygame.sprite.Group()
Wheel()
Player()
Gun()

for enemy in enemies:
    Enemy(enemy[0].object[1])
    Enemy_gun(enemy[1].object[1])

Elevator()

Door()

for weap in range(3):
    Weapon_sprite(weap)

Slowmo()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_a, pygame.K_d):
                move[int(event.key == pygame.K_d)] = True
            elif event.key == pygame.K_SPACE:
                move[2] = True
            elif event.key == pygame.K_LSHIFT:
                do_slowmo = True
            elif event.key == pygame.K_LCTRL:
                move[3] = True
            elif event.key == pygame.K_q:
                if not rope:
                    if weapon > 0:
                        weapon -= 1
                    else:
                        weapon = len(WEAPONS) - 1
                if show_weapons < 10:
                    show_weapons = 50 - show_weapons
                elif show_weapons <= 40:
                    show_weapons = 40
            elif event.key == pygame.K_e:
                if not rope:
                    if weapon < len(WEAPONS) - 1:
                        weapon += 1
                    else:
                        weapon = 0
                if show_weapons < 10:
                    show_weapons = 50 - show_weapons
                elif show_weapons <= 40:
                    show_weapons = 40
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_a, pygame.K_d):
                move[int(event.key == pygame.K_d)] = False
            elif event.key == pygame.K_SPACE:
                move[2] = False
            elif event.key == pygame.K_LSHIFT:
                do_slowmo = False
            elif event.key == pygame.K_LCTRL:
                move[3] = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if len(enemies) > 0 and switching_to_level == 0:
                if event.button == 1:
                    if weapon == 0:
                        if not rope:
                            real_pos = event.pos
                            arm_pos = player_objects[3].object[0].position
                            max_s = max(abs(real_pos[0] - arm_pos[0]), abs(real_pos[1] - arm_pos[1]))
                            offset = ((real_pos[0] - arm_pos[0]) / max_s, (real_pos[1] - arm_pos[1]) / max_s)
                            pos = (0, 0)
                            go = True
                            s = -1
                            is_enemy = False
                            while go:
                                s += 1
                                current_pos = (arm_pos[0] + offset[0] * s, arm_pos[1] + offset[1] * s)
                                point = space.point_query_nearest(current_pos, 10000, pymunk.ShapeFilter(mask=0b000010))
                                if point is not None:
                                    if point.distance < 0 and point.shape in [enemy[0].object[1] for enemy in enemies]:
                                        pos = current_pos
                                        go = False
                                        is_enemy = True
                                for block in blocks:
                                    block_pos = block[0].object[0].position
                                    current_pos = (arm_pos[0] + offset[0] * s, arm_pos[1] + offset[1] * s)
                                    if current_pos[0] >= block_pos[0] - block[1] / 2 and current_pos[0] <= block_pos[0] + block[1] / 2 and current_pos[1] >= block_pos[1] - block[2] / 2 and current_pos[1] <= block_pos[1] + block[2] / 2:
                                        pos = current_pos
                                        go = False
                                        break
                            if is_enemy:
                                enemy = [enemy[0].object[1] for enemy in enemies].index(point.shape)
                                enemy_index = enemy
                                first_point = enemies[enemy][0].object[0].position
                                second_point = player_objects[3].object[0].position
                                rope_length = int(math.sqrt((first_point[0] - second_point[0]) ** 2 + (first_point[1] - second_point[1]) ** 2))
                                rope_pos = first_point
                                rope = Connection('slide', player_objects[3].object[0], enemies[enemy][0].object[0], (0, 25), (0, 0), 0, rope_length)
                                created = True
                                if not del_rope:
                                    del_rope = True
                            else:
                                for block in blocks:
                                    block_pos = block[0].object[0].position
                                    if pos[0] >= block_pos[0] - block[1] / 2 and pos[0] <= block_pos[0] + block[1] / 2 and pos[1] >= block_pos[1] - block[2] / 2 and pos[1] <= block_pos[1] + block[2] / 2:
                                        first_point = pos
                                        second_point = player_objects[3].object[0].position
                                        rope_length = int(math.sqrt((first_point[0] - second_point[0]) ** 2 + (first_point[1] - second_point[1]) ** 2))
                                        rope_pos = pos
                                        rope = Connection('slide', player_objects[3].object[0], block[0].object[0], (0, 25), (pos[0] - block_pos[0], pos[1] - block_pos[1]), 0, rope_length)
                                        created = True
                                        if not del_rope:
                                            del_rope = True
                    elif weapon == 1:
                        if weapon_reload == 0:
                            weapon_reload = 20
                            real_pos = event.pos
                            arm_pos = player_objects[3].object[0].position
                            max_s = max(abs(real_pos[0] - arm_pos[0]), abs(real_pos[1] - arm_pos[1]))
                            offset = ((real_pos[0] - arm_pos[0]) / max_s, (real_pos[1] - arm_pos[1]) / max_s)
                            bullets.append(Circle('dynamic', 5, 5, arm_pos, 0.2, 0.1, (255, 255, 0)))
                            bullets[-1].object[0].velocity = (offset[0] * 2500, offset[1] * 2500)
                            bullets[-1].object[1].filter = pymunk.ShapeFilter(categories=0b000100, mask=0b010000)
                            player_objects[3].object[0].apply_impulse_at_local_point((0, -750), (0, 25))
                            auto_slowmo_wait = 20
                            camera_shaking += 10
                            for _ in range(5):
                                shoot_particles.append([list(arm_pos), [offset[0] * 10 + random.randint(-5, 5), offset[1] * 10 + random.randint(-5, 5)], (255, random.randint(0, 255), 0), random.randint(0, 5), random.randint(0, 2), random.randint(2, 5)])
                    elif weapon == 2:
                        if weapon_reload == 0:
                            weapon_reload = 60
                            just_shooted = True
                            real_pos = event.pos
                            arm_pos = player_objects[3].object[0].position
                            max_s = max(abs(real_pos[0] - arm_pos[0]), abs(real_pos[1] - arm_pos[1]))
                            offset = ((real_pos[0] - arm_pos[0]) / max_s, (real_pos[1] - arm_pos[1]) / max_s)
                            for _ in range(5):
                                bullets.append(Circle('dynamic', 5, 5, arm_pos, 0.2, 0.1, (255, 255, 0)))
                                bullets[-1].object[0].velocity = (offset[0] * 1000 + random.randint(-200, 200), offset[1] * 1000 + random.randint(-200, 200))
                                bullets[-1].object[1].filter = pymunk.ShapeFilter(categories=0b000100, mask=0b010000)
                            player_objects[3].object[0].apply_impulse_at_local_point((0, -1000), (0, 25))
                            player_objects[1].object[0].velocity = player_objects[3].object[0].velocity
                            player_objects[0].object[0].velocity = player_objects[3].object[0].velocity
                            auto_slowmo_wait = 20
                            camera_shaking += 20
                            for _ in range(10):
                                shoot_particles.append([list(arm_pos), [offset[0] * 10 + random.randint(-5, 5), offset[1] * 10 + random.randint(-5, 5)], (255, random.randint(0, 255), 0), random.randint(0, 10), random.randint(0, 4), random.randint(4, 10)])
                elif event.button == 3:
                    if weapon == 0:
                        if weapon_reload == 0:
                            weapon_reload = 30
                            real_pos = event.pos
                            arm_pos = player_objects[3].object[0].position
                            max_s = max(abs(real_pos[0] - arm_pos[0]), abs(real_pos[1] - arm_pos[1]))
                            offset = ((real_pos[0] - arm_pos[0]) / max_s, (real_pos[1] - arm_pos[1]) / max_s)
                            bullets.append(Circle('dynamic', 5, 5, arm_pos, 0.2, 0.1, (255, 255, 0)))
                            bullets[-1].object[0].velocity = (offset[0] * 1500, offset[1] * 1500)
                            bullets[-1].object[1].filter = pymunk.ShapeFilter(categories=0b000100, mask=0b010000)
                            player_objects[3].object[0].apply_impulse_at_local_point((0, -500), (0, 25))
                            auto_slowmo_wait = 20
                            camera_shaking += 10
                            for _ in range(5):
                                shoot_particles.append([list(arm_pos), [offset[0] * 10 + random.randint(-5, 5), offset[1] * 10 + random.randint(-5, 5)], (255, random.randint(0, 255), 0), random.randint(0, 5), random.randint(0, 2), random.randint(2, 5)])
                elif event.button == 4:
                    if weapon == 0:
                        if rope and rope_length > 0:
                            rope_length -= min(20, rope_length)
                            space.remove(rope.object)
                            rope = Connection('slide', player_objects[3].object[0], block[0].object[0], (0, 25), (pos[0] - block_pos[0], pos[1] - block_pos[1]), 0, rope_length)
                elif event.button == 5:
                    if weapon == 0:
                        if rope and rope_length < 1500:
                            rope_length += min(20, 1500 - rope_length)
                            space.remove(rope.object)
                            rope = Connection('slide', player_objects[3].object[0], block[0].object[0], (0, 25), (pos[0] - block_pos[0], pos[1] - block_pos[1]), 0, rope_length)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if weapon == 0:
                    if rope:
                        if del_rope:
                            space.remove(rope.object)
                            rope = False
                elif weapon == 2:
                    if len(enemies) > 0 and switching_to_level == 0:
                        if just_shooted:
                            just_shooted = False
                            stuffs.append(Circle('dynamic', 5, 5, arm_pos, 0.2, 0.1, (255, 125, 0)))
                            stuffs[-1].object[0].velocity = (random.randint(-200, 200), random.randint(-1200, -800))
                            stuffs[-1].object[1].filter = pymunk.ShapeFilter(categories=0b001000, mask=0b010000)
    screen.fill(pygame.Color('white'))

    if switching_to_level == 0:
        space.step(1 / fps)

    if not is_elevator:
        elevator_objects[0].object[0].position = (2175, 740)
        elevator_objects[0].object[0].velocity = (0, 0)
        elevator_objects[0].object[0].angle = 0
        elevator_objects[0].object[0].angular_velocity = 0
        text = font.render(str(room), True, (100, 100, 100))
        text_size = text.get_size()
        screen.blit(text, (600 - text_size[0] / 2, 400 - text_size[1] / 2))

    all_sprites.update()
    all_sprites.draw(screen)

    pygame.draw.line(screen, (20, 20, 20), (blocks[-3][0].object[0].position[0] + 225, blocks[-3][0].object[0].position[1]), (elevator_objects[0].object[0].position[0] - 140, elevator_objects[0].object[0].position[1]), 10)
    pygame.draw.line(screen, (20, 20, 20), (blocks[-3][0].object[0].position[0] + 525, blocks[-3][0].object[0].position[1]), (elevator_objects[0].object[0].position[0] + 140, elevator_objects[0].object[0].position[1]), 10)

    for block in blocks:
        position = list(block[0].object[0].position)
        position[0] -= block[1] / 2
        position[1] -= block[2] / 2
        pygame.draw.rect(screen, block[0].object[1].color[:3], (position[0], position[1], block[1], block[2]))
    
    for bullet in bullets:
        pygame.draw.circle(screen, (255, 255, 0), bullet.object[0].position, 5)
    
    for bullet in enemy_bullets:
        pygame.draw.circle(screen, (255, 255, 0), bullet.object[0].position, 5)
    
    for stuff in stuffs:
        pygame.draw.circle(screen, stuff.object[1].color[:3], stuff.object[0].position, 5)
    
    for particle in shoot_particles:
        particle[5] -= 1
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[1][0] /= 1.2
        particle[1][1] /= 1.2
        if particle[5] >= 0:
            particle[3] += particle[4]
            pygame.draw.circle(screen, particle[2], particle[0], particle[3])
        else:
            pygame.draw.circle(screen, particle[2], particle[0], particle[3] * ((particle[5] + 50) / 50))
        if particle[5] == -50:
            del shoot_particles[shoot_particles.index(particle)]
    
    # simulation
    if is_enemy:
        if rope:
            rope_pos = enemies[enemy_index][0].object[0].position
    if move[0]:
        player_objects[0].object[0].apply_impulse_at_local_point((-30, 0), (0, -12.5))
        if (player_objects[0].object[0].velocity[0] > -200 and circle_collides_flat(player_objects[0].object[0].position[0], player_objects[0].object[0].position[1], blocks)) or (not circle_collides_flat(player_objects[0].object[0].position[0], player_objects[0].object[0].position[1], blocks)):
            player_objects[0].object[0].velocity = (player_objects[0].object[0].velocity[0] - 20, player_objects[0].object[0].velocity[1])
    if move[1]:
        player_objects[0].object[0].apply_impulse_at_local_point((30, 0), (0, -12.5))
        if (player_objects[0].object[0].velocity[0] < 200 and circle_collides_flat(player_objects[0].object[0].position[0], player_objects[0].object[0].position[1], blocks)) or (not circle_collides_flat(player_objects[0].object[0].position[0], player_objects[0].object[0].position[1], blocks)):
            player_objects[0].object[0].velocity = (player_objects[0].object[0].velocity[0] + 20, player_objects[0].object[0].velocity[1])
    if player_objects[0].object[0].angular_velocity > 30:
        player_objects[0].object[0].angular_velocity = 30
    if player_objects[0].object[0].angular_velocity < -30:
        player_objects[0].object[0].angular_velocity = -30
    if circle_collides_flat(player_objects[0].object[0].position[0], player_objects[0].object[0].position[1], blocks):
        if not move[3]:
            real_angle = math.degrees(player_objects[1].object[0].angle) - math.degrees(player_objects[1].object[0].angle) // 360 * 360
            if real_angle > 0 and real_angle <= 180:
                player_objects[1].object[0].apply_impulse_at_local_point((-math.radians(real_angle) * 100, 0), (0, -50))
            else:
                player_objects[1].object[0].apply_impulse_at_local_point((math.radians(360 - real_angle) * 100, 0), (0, -50))
        if move[2]:
            player_objects[0].object[0].velocity = (player_objects[0].object[0].velocity[0], player_objects[0].object[0].velocity[1] - 1000)
            player_objects[1].object[0].velocity = (player_objects[1].object[0].velocity[0], player_objects[1].object[0].velocity[1] - 1000)

    arm_pos = player_objects[3].object[0].position
    real_angle = math.degrees(player_objects[3].object[0].angle) - math.degrees(player_objects[3].object[0].angle) // 360 * 360
    y = (abs(75 - math.radians((real_angle * 2 - 180) / math.pi) * 25 - 50) - 25) * 2
    x = 50 - abs(y)
    if real_angle < 180:
        x = -x
    
    if rope:
        line_pos = (player_objects[3].object[0].position[0] + x / 2, player_objects[3].object[0].position[1] + y / 2)
        pygame.draw.line(screen, (100, 100, 100), line_pos, rope_pos, 10)
        pygame.draw.circle(screen, (150, 150, 150), line_pos, 5)
        pygame.draw.circle(screen, (150, 150, 150), rope_pos, 5)
    
    real_pos = pygame.mouse.get_pos()
    arm_pos = player_objects[3].object[0].position
    max_s = max(abs(real_pos[0] - arm_pos[0]), abs(real_pos[1] - arm_pos[1]))
    offset = ((real_pos[0] - arm_pos[0]) / max_s, (real_pos[1] - arm_pos[1]) / max_s)
    targeting = (0, 0)
    go = True
    s = -1
    if len(enemies) > 0 and switching_to_level == 0:
        while go:
            s += 1
            current_pos = (arm_pos[0] + offset[0] * s, arm_pos[1] + offset[1] * s)
            point = space.point_query_nearest(current_pos, 10000, pymunk.ShapeFilter(mask=0b000010))
            if point is not None:
                if point.distance < 0:
                    targeting = current_pos
                    go = False
            for block in blocks:
                block_pos = block[0].object[0].position
                if current_pos[0] >= block_pos[0] - block[1] / 2 and current_pos[0] <= block_pos[0] + block[1] / 2 and current_pos[1] >= block_pos[1] - block[2] / 2 and current_pos[1] <= block_pos[1] + block[2] / 2:
                    targeting = current_pos
                    go = False
                    break
    else:
        targeting = (-100, -100)
        
    if len(enemies) > 0 and switching_to_level == 0:
        player_objects[0].object[0].position = fix_to_bounds(player_objects[0].object[0].position)
        player_objects[1].object[0].position = fix_to_bounds(player_objects[1].object[0].position)
        player_objects[3].object[0].position = fix_to_bounds(player_objects[3].object[0].position)

    if len(enemies) > 0 and switching_to_level == 0:
        if not rope:
            arm_pos = player_objects[3].object[0].position
            max_s = max(abs(targeting[0] - arm_pos[0]), abs(targeting[1] - arm_pos[1]))
            if max_s != 0:
                offset = ((targeting[0] - arm_pos[0]) / max_s, (targeting[1] - arm_pos[1]) / max_s)
                root = math.sqrt(offset[0] ** 2 + offset[1] ** 2)
                if root != 0:
                    res = (math.degrees(offset[1] / root) * math.pi + 180) / 2
                    if offset[0] < 0:
                        res = 360 - res
                    player_objects[3].object[0].angle = math.radians(res + 180)
                    player_objects[3].object[0].angular_velocity = 0
    
    if weapon_reload > 0:
        weapon_reload -= 1
    
    for bullet in bullets[::-1]:
        bul_pos = bullet.object[0].position
        point = space.point_query_nearest(bul_pos, 10000, pymunk.ShapeFilter(mask=0b000010))
        try:
            if point is not None:
                if point.distance < 0 and point.shape in [enemy[0].object[1] for enemy in enemies]:
                    if abs(bullet.object[0].velocity[0]) + abs(bullet.object[0].velocity[1]) >= 1200:
                        enemy = [enemy[0].object[1] for enemy in enemies].index(point.shape)
                        posit = enemies[enemy][0].object[0].position
                        for i in range(2):
                            space.remove(*enemies[enemy][i].object)
                        if enemies[enemy][2] is not None:
                            space.remove(enemies[enemy][2].object)
                            space.remove(enemies[enemy][3].object)
                        del enemies[enemy]
                        enemies_to_destroy.append(enemy)
                        space.remove(*bullet.object)
                        del bullets[bullets.index(bullet)]
                        for _ in range(40):
                            stuffs.append(Circle('dynamic', 5, 5, (posit[0] + random.randint(-35, 35), posit[1] + random.randint(-35, 35)), 0.1, 0.1, (255, 0, 0)))
                            stuffs[-1].object[0].velocity = (random.randint(-400, 400), random.randint(-2000, -800))
                            stuffs[-1].object[1].filter = pymunk.ShapeFilter(categories=0b001000, mask=0b010000)
                        if rope:
                            if is_enemy:
                                if enemy_index == enemy:
                                    if del_rope:
                                        space.remove(rope.object)
                                        rope = False
                                        enemy_index = -1
        except AssertionError:
            pass
    
    if switching_to_level == 0:
        for enemy in enemies:
            enemies[enemies.index(enemy)][5] -= 1
            arm_pos1 = enemies[enemies.index(enemy)][1].object[0].position
            targeting1 = player_objects[3].object[0].position
            if enemies[enemies.index(enemy)][2] is not None:
                max_s1 = max(abs(targeting1[0] - arm_pos1[0]), abs(targeting1[1] - arm_pos1[1]))
                if max_s1 != 0:
                    offset1 = ((targeting1[0] - arm_pos1[0]) / max_s1, (targeting1[1] - arm_pos1[1]) / max_s1)
                    root1 = math.sqrt(offset[0] ** 2 + offset[1] ** 2)
                    if root1 != 0:
                        res1 = (math.degrees(offset1[1] / root1) * math.pi + 180) / 2
                        if offset1[0] < 0:
                            res1 = 360 - res1
                        enemies[enemies.index(enemy)][1].object[0].angle = math.radians(res1 + 180)
                        enemies[enemies.index(enemy)][1].object[0].angular_velocity = 0
                    if enemies[enemies.index(enemy)][5] == 0:
                        enemies[enemies.index(enemy)][5] = 180
                        enemy_bullets.append(Circle('dynamic', 5, 5, arm_pos1, 0.2, 0.1, (255, 255, 0)))
                        enemy_bullets[-1].object[0].velocity = (offset1[0] * 2500, offset1[1] * 2500)
                        enemy_bullets[-1].object[1].filter = pymunk.ShapeFilter(categories=0b100000, mask=0b010000)
            velocity = enemy[0].object[0].velocity
            last_vel = enemy[4]
            if enemy[2] is not None:
                if abs(last_vel[0] - velocity[0]) + abs(last_vel[1] - velocity[1]) >= 600:
                    space.remove(enemy[2].object)
                    space.remove(enemy[3].object)
                    enemies[enemies.index(enemy)][2] = None
            enemies[enemies.index(enemy)][4] = velocity
    
    for bullet in enemy_bullets:
        bul_pos = bullet.object[0].position
        point = space.point_query_nearest(bul_pos, 10000, pymunk.ShapeFilter(mask=0b000001))
        if point is not None:
            if point.distance < 0 and point.shape in [player_objects[i].object[1] for i in (0, 1, 3)]:
                if abs(bullet.object[0].velocity[0]) + abs(bullet.object[0].velocity[1]) >= 1200:
                    player = [player_objects[i].object[1] for i in (0, 1, 3)].index(point.shape)
                    if player == 2:
                        player = 3
                    posit = player_objects[player].object[0].position
                    player_health -= 20
                    camera_shaking += 20
                    player_objects[player].object[0].velocity = bullet.object[0].velocity
                    space.remove(*bullet.object)
                    del enemy_bullets[enemy_bullets.index(bullet)]
                    for _ in range(8):
                        stuffs.append(Circle('dynamic', 5, 5, (posit[0] + random.randint(-35, 35), posit[1] + random.randint(-35, 35)), 0.1, 0.1, (0, 0, 255)))
                        stuffs[-1].object[0].velocity = (random.randint(-400, 400), random.randint(-2000, -800))
                        stuffs[-1].object[1].filter = pymunk.ShapeFilter(categories=0b001000, mask=0b010000)
    
    pygame.draw.circle(screen, (255, 0, 0), targeting, 10, 4)

    if current_player_health > player_health:
        current_player_health -= (current_player_health - player_health) / 10
        current_player_health = round(current_player_health, 2)
    if current_player_health < 0:
        current_player_health = 0

    pygame.draw.rect(screen, (0, 0, 0), (800, 0, 400, 40))
    pygame.draw.rect(screen, (255, 0, 0), (805, 5, 390, 30))
    pygame.draw.rect(screen, (0, 255, 0), (805, 5, current_player_health * 3.9, 30))

    current_vel = player_objects[3].object[0].velocity
    if abs(current_vel[0] - last_body_vel[0]) + abs(current_vel[1] - last_body_vel[1]) > 500:
        camera_shaking += 1
    last_body_vel = current_vel

    if camera_shaking > 0:
        real_screen = pygame.Surface(size)
        real_screen.fill((150, 150, 150))
        real_screen.blit(screen, (random.randint(-camera_shaking, camera_shaking), random.randint(-camera_shaking, camera_shaking)))
        camera_shaking -= 1
        
        screen.blit(real_screen, (0, 0))

    if do_slowmo:
        slowmo = 2
    else:
        slowmo = 1
    
    if auto_slowmo:
        if not circle_collides_flat(player_objects[0].object[0].position[0], player_objects[0].object[0].position[1], blocks):
            slowmo = 2
        if auto_slowmo_wait > 0:
            slowmo = 2
            auto_slowmo_wait -= 1
    
    if len(enemies) == 0:
        slowmo = 1
    
    if switching_to_level != 0:
        slowmo = 2
    
    current_slowmo += (slowmo - current_slowmo) / 10
    if str(current_slowmo).split(".")[1][:3] in ("999", "000"):
        current_slowmo = slowmo
    
    weapon_sprites.update()
    weapon_sprites.draw(screen)

    text = font1.render(WEAPONS[weapon], True, (0, 0, 0))
    pos_y = 110
    if show_weapons > 40:
        pos_y = -100 + 210 * (1 - (show_weapons - 40) / 10)
    elif show_weapons < 10:
        pos_y = 110 - 210 * (1 - show_weapons / 10)
    screen.blit(text, (160 - text.get_size()[0] / 2, pos_y))
    
    if current_slowmo > 1:
        slowmo_group.update()
        slowmo_group.draw(screen)
    
    if show_weapons > 0:
        show_weapons -= 1
    
    if len(enemies) == 0:
        if elevator_door_opening < 200:
            elevator_door_opening += 10
            blocks[0][0].object[0].position = (blocks[0][0].object[0].position[0], blocks[0][0].object[0].position[1] - 10)
    
    if len(enemies) == 0 and player_objects[0].object[0].position[0] > 1200 and not is_elevator:
        switching = 1200
        is_elevator = True
    
    if is_elevator and switching == 0 and player_objects[0].object[0].position[0] > 100 and closed_door == False:
        elevator_door_closing = 200
        closed_door = True
    
    if elevator_door_closing > 0:
        elevator_door_closing -= 10
        blocks[0][0].object[0].position = (blocks[0][0].object[0].position[0], blocks[0][0].object[0].position[1] + 10)
    
    if player_objects[0].object[0].position[1] + 35 >= elevator_objects[0].object[0].position[1] - 10 and player_objects[0].object[0].position[1] + 35 <= elevator_objects[0].object[0].position[1] + 10 and player_objects[0].object[0].position[0] >= elevator_objects[0].object[0].position[0] - 50 and player_objects[0].object[0].position[0] <= elevator_objects[0].object[0].position[0] + 150 and not launched_elevator and is_elevator:
        launched_elevator = True
        closing_elevator = 300
        elevator = 1300
    
    if closing_elevator > 0:
        closing_elevator -= 10
        blocks[-1][0].object[0].position = (blocks[-1][0].object[0].position[0], blocks[-1][0].object[0].position[1] + 10)

    if elevator > 0:
        elevator -= 2
        space.remove(elevator_objects[1].object)
        space.remove(elevator_objects[2].object)
        del elevator_objects[2]
        del elevator_objects[1]
        elevator_objects.append(Connection('slide', elevator_objects[0].object[0], blocks[-3][0].object[0], (-150, 0), (225, 0), 0, elevator + 200))
        elevator_objects.append(Connection('slide', elevator_objects[0].object[0], blocks[-3][0].object[0], (150, 0), (525, 0), 0, elevator + 200))
    
    if switching > 0:
        switching -= 100
        for obj in [0, 1, 3]:
            player_objects[obj].object[0].position = (player_objects[obj].object[0].position[0] - 100, player_objects[obj].object[0].position[1])
        for block in range(len(blocks)):
            blocks[block][0].object[0].position = (blocks[block][0].object[0].position[0] - 100, blocks[block][0].object[0].position[1])
        elevator_objects[0].object[0].position = (elevator_objects[0].object[0].position[0] - 100, elevator_objects[0].object[0].position[1])
        space.remove(elevator_objects[1].object)
        space.remove(elevator_objects[2].object)
        del elevator_objects[2]
        del elevator_objects[1]
        elevator_objects.append(Connection('slide', elevator_objects[0].object[0], blocks[-3][0].object[0], (-150, 0), (225, 0), 0, 1500))
        elevator_objects.append(Connection('slide', elevator_objects[0].object[0], blocks[-3][0].object[0], (150, 0), (525, 0), 0, 1500))
        for object in stuffs:
            space.remove(*object.object)
        for object in bullets:
            space.remove(*object.object)
        for object in enemy_bullets:
            space.remove(*object.object)
        stuffs.clear()
        bullets.clear()
        enemy_bullets.clear()
    
    if elevator <= 500 and elevator > 450:
        for obj in [0, 1, 3]:
            player_objects[obj].object[0].position = (player_objects[obj].object[0].position[0], player_objects[obj].object[0].position[1] + 8)
        for block in range(len(blocks)):
            blocks[block][0].object[0].position = (blocks[block][0].object[0].position[0], blocks[block][0].object[0].position[1] + 8)
        elevator_objects[0].object[0].position = (elevator_objects[0].object[0].position[0], elevator_objects[0].object[0].position[1] + 8)

    if is_elevator and player_objects[0].object[0].position[0] > 1200 and switching_to_level == 0:
        switching_to_level = 1200
        score += 1
        for obj in [0, 1, 3]:
            player_objects[obj].object[0].position = (player_objects[obj].object[0].position[0] + 100, player_objects[obj].object[0].position[1])
    
    if switching_to_level > 0:
        switching_to_level -= 60
        for obj in [0, 1, 3]:
            player_objects[obj].object[0].position = (player_objects[obj].object[0].position[0] - 60, player_objects[obj].object[0].position[1])
        for block in range(len(blocks)):
            blocks[block][0].object[0].position = (blocks[block][0].object[0].position[0] - 60, blocks[block][0].object[0].position[1])
        elevator_objects[0].object[0].position = (elevator_objects[0].object[0].position[0] - 60, elevator_objects[0].object[0].position[1])
        if switching_to_level == 0:
            switching_to_level = -100
            for block in range(len(blocks)):
                space.remove(*blocks[block][0].object)
            blocks.clear()
            space.remove(*elevator_objects[0].object)
            space.remove(elevator_objects[1].object)
            space.remove(elevator_objects[2].object)
            del elevator_objects[2]
            del elevator_objects[1]
            del elevator_objects[0]
            generate_level()
            for enemy in enemies:
                Enemy(enemy[0].object[1])
                Enemy_gun(enemy[1].object[1])

    if switching_to_level < 0:
        switching_to_level += 2
        if switching_to_level == 0:
            elevator_door_opening = 0
            switching = 0
            is_elevator = False
            elevator_door_closing = 0
            closed_door = False
            closing_elevator = 0
            elevator = 0
            launched_elevator = False

    clock.tick(fps / current_slowmo)
    pygame.display.flip()
pygame.quit()
