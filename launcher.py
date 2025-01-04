import pygame
import pymunk.pygame_util
import os, math

pygame.init()
size = w, h = 1200, 800
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Robots' Shootover")

pymunk.pygame_util.positive_y_is_up=False

draw_options = pymunk.pygame_util.DrawOptions(screen)
draw_options.flags = pymunk.SpaceDebugDrawOptions.DRAW_SHAPES
space = pymunk.Space()
space.gravity = 0, 3000


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
        
    return False

def create_block(x, y, sx, sy, color):
    global blocks
    blocks.append([Rect('kinematic', 10, (sx, sy), (x + sx / 2, y + sy / 2), 1, 1, color), sx, sy])


all_objects = []
player_objects = []
blocks = []

rope = False
del_rope = False
rope_length = 0
rope_pos = (0, 0)

bullets = []

blocks.append([Rect('kinematic', 10, (1200, 30), (600, 800), 1, 1, (0, 255, 0)), 1200, 30])
blocks.append([Rect('kinematic', 10, (30, 800), (0, 400), 1, 1, (0, 255, 0)), 30, 800])
blocks.append([Rect('kinematic', 10, (30, 800), (1200, 400), 1, 1, (0, 255, 0)), 30, 800])
blocks.append([Rect('kinematic', 10, (1200, 30), (600, 0), 1, 1, (0, 255, 0)), 1200, 30])
player_objects.append(Circle('dynamic', 5, 25, (100, 600), 0.2, 100, (0, 0, 255)))
player_objects.append(Rect('dynamic', 0.5, (50, 100), (100, 500), 0.1, 0.2, (0, 0, 255)))
player_objects.append(Connection('groove', player_objects[1].object[0], player_objects[0].object[0], (0, 50), (0, 100), (0, 0)))
player_objects.append(Rect('dynamic', 0.5, (10, 50), (100, 525), 0, 0, (0, 0, 0)))
player_objects.append(Connection('pivot', player_objects[1].object[0], player_objects[3].object[0], (0, 0), (0, -25)))
create_block(15, 685, 200, 100, (255, 0, 0))
create_block(985, 685, 200, 100, (0, 255, 0))
create_block(550, 50, 100, 100, (0, 0, 255))
create_block(15, 300, 200, 100, (0, 0, 255))

player_objects[0].object[1].filter = pymunk.ShapeFilter(group=1)
player_objects[1].object[1].filter = pymunk.ShapeFilter(group=1)
player_objects[3].object[1].filter = pymunk.ShapeFilter(group=1)

move = [False, False, False, False]

clock = pygame.time.Clock()
fps = 30

running = True

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
                move[3] = True
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_a, pygame.K_d):
                move[int(event.key == pygame.K_d)] = False
            elif event.key == pygame.K_SPACE:
                move[2] = False
            elif event.key == pygame.K_LSHIFT:
                move[3] = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not rope:
                    real_pos = event.pos
                    arm_pos = player_objects[3].object[0].position
                    max_s = max(abs(real_pos[0] - arm_pos[0]), abs(real_pos[1] - arm_pos[1]))
                    offset = ((real_pos[0] - arm_pos[0]) / max_s, (real_pos[1] - arm_pos[1]) / max_s)
                    pos = (0, 0)
                    go = True
                    s = -1
                    while go:
                        s += 1
                        for block in blocks:
                            block_pos = block[0].object[0].position
                            current_pos = (arm_pos[0] + offset[0] * s, arm_pos[1] + offset[1] * s)
                            if current_pos[0] >= block_pos[0] - block[1] / 2 and current_pos[0] <= block_pos[0] + block[1] / 2 and current_pos[1] >= block_pos[1] - block[2] / 2 and current_pos[1] <= block_pos[1] + block[2] / 2:
                                pos = current_pos
                                go = False
                                break
                    for block in blocks:
                        block_pos = block[0].object[0].position
                        if pos[0] >= block_pos[0] - block[1] / 2 and pos[0] <= block_pos[0] + block[1] / 2 and pos[1] >= block_pos[1] - block[2] / 2 and pos[1] <= block_pos[1] + block[2] / 2:
                            first_point = pos
                            second_point = player_objects[3].object[0].position
                            rope_length = int(math.sqrt((first_point[0] - second_point[0]) ** 2 + (first_point[1] - second_point[1]) ** 2))
                            rope_pos = pos
                            rope = Connection('slide', player_objects[3].object[0], block[0].object[0], (0, 0), (pos[0] - block_pos[0], pos[1] - block_pos[1]), 0, rope_length)
                            created = True
                            if not del_rope:
                                del_rope = True
                else:
                    if del_rope:
                        space.remove(rope.object)
                        rope = False
            elif event.button == 3:
                real_pos = event.pos
                arm_pos = player_objects[3].object[0].position
                max_s = max(abs(real_pos[0] - arm_pos[0]), abs(real_pos[1] - arm_pos[1]))
                offset = ((real_pos[0] - arm_pos[0]) / max_s, (real_pos[1] - arm_pos[1]) / max_s)
                bullets.append(Circle('dynamic', 5, 5, arm_pos, 0.2, 0.1, (255, 255, 0)))
                bullets[-1].object[0].velocity = (offset[0] * 1500, offset[1] * 1500)
                bullets[-1].object[1].filter = pymunk.ShapeFilter(group=1)
                player_objects[3].object[0].apply_impulse_at_local_point((0, -500), (0, 25))
            elif event.button == 4:
                if rope and rope_length > 0:
                    rope_length -= min(10, rope_length)
                    space.remove(rope.object)
                    rope = Connection('slide', player_objects[3].object[0], block[0].object[0], (0, 0), (pos[0] - block_pos[0], pos[1] - block_pos[1]), 0, rope_length)
            elif event.button == 5:
                if rope and rope_length < 1500:
                    rope_length += min(10, 1500 - rope_length)
                    space.remove(rope.object)
                    rope = Connection('slide', player_objects[3].object[0], block[0].object[0], (0, 0), (pos[0] - block_pos[0], pos[1] - block_pos[1]), 0, rope_length)
    screen.fill(pygame.Color('white'))
    space.step(1 / fps)
    
    # simulation
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

    space.debug_draw(draw_options)

    if rope:
        pygame.draw.line(screen, (100, 100, 100), player_objects[3].object[0].position, rope_pos, 10)
        pygame.draw.circle(screen, (150, 150, 150), player_objects[3].object[0].position, 5)
        pygame.draw.circle(screen, (150, 150, 150), rope_pos, 5)

    clock.tick(fps)
    pygame.display.flip()
pygame.quit()
