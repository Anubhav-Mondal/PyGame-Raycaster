import pygame as pg
import os
import math

FPS = 60
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 900
HALF_SCREEN_HEIGHT = SCREEN_HEIGHT/2
HALF_SCREEN_WIDTH = SCREEN_WIDTH/2

script_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(script_dir, '..', 'assets', 'icon.png')
icon = pg.image.load(icon_path)
pg.display.set_icon(icon)


# make sure that the whole map is covered by the wall(1)
world_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1],
    [1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

TILE_WIDTH = SCREEN_HEIGHT/(len(world_map))

px, py = TILE_WIDTH * 1.5, SCREEN_HEIGHT - TILE_WIDTH * 1.5
pa = math.pi / 2

p_speed =  4
rot_speed = 2
player_width = 10

MAP_WIDTH = len(world_map[0])
MAP_HEIGHT = len(world_map)

FOV = math.pi / 3
RAY_NUM = 500
WALL_WIDTH = math.ceil(SCREEN_WIDTH / RAY_NUM)
WALL_HEIGHT = SCREEN_HEIGHT/9

mini_map_scale = 0.2

pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH + SCREEN_WIDTH/10, SCREEN_HEIGHT))
clock = pg.time.Clock()
running = True
pg.mouse.set_cursor(pg.cursors.tri_left)

def mini_map():
    for row in range(len(world_map)):
        for col in range(len(world_map[row])):
            if world_map[row][col] == 1:
                pg.draw.rect(screen, (160, 160, 160), pg.Rect(col * TILE_WIDTH * mini_map_scale + 10, row * TILE_WIDTH * mini_map_scale+ 10, TILE_WIDTH * mini_map_scale, TILE_WIDTH * mini_map_scale))
            else:
                pass
            pg.draw.circle(screen, (200, 10, 0), [px * mini_map_scale + 10, py * mini_map_scale + 10], 4)
            pg.draw.line(screen, (200, 10, 0), [px * mini_map_scale + 10, py * mini_map_scale + 10], [px * mini_map_scale+10*math.cos(pa) + 10, py * mini_map_scale - 10 * math.sin(pa) + 10], 1)    

def world_render():
    for row in range(len(world_map)):
        for col in range(len(world_map[row])):
            if world_map[row][col] == 1:
                pg.draw.rect(screen, (160, 160, 160), pg.Rect(col * TILE_WIDTH , row * TILE_WIDTH , TILE_WIDTH , TILE_WIDTH ))
            else:
                pass
            pg.draw.circle(screen, (250, 10, 0), [px , py ], 4)
            pg.draw.line(screen, (250, 10, 0), [px , py ], [px +10*math.cos(pa), py  - 10 * math.sin(pa)], 1)    
            
def collision_check(nx, ny):
    col, row = int(nx // TILE_WIDTH), int(ny // TILE_WIDTH)
    if world_map[row][col] == 1:
        return True  # Collision 
    return False  # No collision

def has_wall(x, y):
    if world_map[int(y//TILE_WIDTH)][int(x//TILE_WIDTH)] == 1:
        return True
    else:
        return False

def distance_calc(x1, y1, x2, y2):
    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return distance

def normalize_angle(angle):
    angle = angle % (2 * math.pi)
    if (angle <= 0):
        angle = (2 * math.pi) + angle
    return angle

def cast_ray():
    start_ray = pa + FOV/2
    for ray in range(RAY_NUM):
        angle = 2*math.pi - normalize_angle(start_ray - ray * FOV / RAY_NUM)

        tan_a = math.tan(angle)

        facing_down = angle > 0 and angle < math.pi
        facing_up = not (facing_down)
        facing_right = angle < 0.5 * math.pi or angle > 1.5 * math.pi
        facing_left = not facing_right

        #Horizontal Line Check
        hz_wall_found = False
        hz_hit_x = 0
        hz_hit_y = 0
        ax, ay = None, None

        if facing_up:
            ay = (py // TILE_WIDTH) * TILE_WIDTH - 0.001
        elif facing_down:
            ay = (py // TILE_WIDTH) * TILE_WIDTH + TILE_WIDTH

        ax = (ay - py)/tan_a + px

        nxt_hz_x = ax
        nxt_hz_y = ay

        xa, ya = 0, 0

        if facing_up:
            ya = - TILE_WIDTH 
        elif facing_down:
            ya = TILE_WIDTH 

        xa = (ya / tan_a)

        while (nxt_hz_x <= SCREEN_WIDTH and nxt_hz_x >=0 and nxt_hz_y <= SCREEN_HEIGHT and nxt_hz_y >=0):
            if has_wall(nxt_hz_x, nxt_hz_y):
                hz_wall_found = True
                hz_hit_x, hz_hit_y = nxt_hz_x, nxt_hz_y
                break
            else:
                nxt_hz_x += xa
                nxt_hz_y += ya


        #Vertical Line Check
        vt_wall_found = False
        vt_hit_x = 0
        vt_hit_y = 0

        if facing_right:
            ax = (px//TILE_WIDTH)*TILE_WIDTH + TILE_WIDTH
        elif facing_left:
            ax = (px//TILE_WIDTH)*TILE_WIDTH - 0.001

        ay = py + (ax - px)*tan_a
        
        nxt_vt_x = ax
        nxt_vt_y = ay  

        if facing_right:
            xa = TILE_WIDTH 
        elif facing_left:
            xa = -TILE_WIDTH

        ya = xa*tan_a

        while (nxt_vt_x <= SCREEN_WIDTH and nxt_vt_x >=0 and nxt_vt_y <= SCREEN_HEIGHT and nxt_vt_y >=0):
            if has_wall(nxt_vt_x, nxt_vt_y):
                vt_wall_found = True
                vt_hit_x, vt_hit_y = nxt_vt_x, nxt_vt_y
                break
            else:
                nxt_vt_x += xa
                nxt_vt_y += ya

        hz_distance, vt_distance = 0, 0

        if hz_wall_found:
            hz_distance = distance_calc(px, py, hz_hit_x, hz_hit_y)
        else: 
            hz_distance = 969
        if vt_wall_found:
            vt_distance = distance_calc(px, py, vt_hit_x, vt_hit_y)
        else: 
            vt_distance = 969

        if hz_distance >= vt_distance:
            color=255
        else:
            color=160

        distance = min(vt_distance, hz_distance)*math.cos(pa + angle)

        proj_wall_height = WALL_HEIGHT/distance * (HALF_SCREEN_WIDTH/math.tan(FOV/2)) 

        color = (1/distance) * 25000
        if color > 255:
            color = 255
        elif color < 0:
            color = 0

        draw_top = HALF_SCREEN_HEIGHT - (proj_wall_height/2)

        pg.draw.rect(screen, (color, color, color), (WALL_WIDTH * ray, draw_top, WALL_WIDTH, proj_wall_height))


bg_path = os.path.join(script_dir, '..', 'assets', 'background.png')
bg = pg.image.load(bg_path)

bg = pg.transform.scale(bg, (SCREEN_WIDTH + SCREEN_WIDTH/10, SCREEN_HEIGHT))

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("#000000")
    screen.blit(bg, (0,0))

    # RENDER YOUR GAME HERE
    cast_ray()
    mini_map()

    # Player Movement
    nx, ny = px, py
    keys = pg.key.get_pressed()
    
    if keys[pg.K_w]:  # Move forward
        ny -= p_speed * math.sin(pa)
        nx += p_speed * math.cos(pa)
    if keys[pg.K_s]:  # Move backward
        ny += p_speed * math.sin(pa)
        nx -= p_speed * math.cos(pa)

    # Check if the next position is colliding with a wall
    if not collision_check(nx, ny):  # Only move if no collision
        px, py = nx, ny

    # Handle rotation
    if keys[pg.K_a]:  # Rotate left
        pa += 0.0174533 * rot_speed
    if keys[pg.K_d]:  # Rotate right
        pa -= 0.0174533 * rot_speed

    # Update Display
    fps = int(clock.get_fps())

    pg.display.set_caption(f"PyGame Raycaster - FPS: {fps}")
    pg.display.flip()
    clock.tick(FPS)  

pg.quit()