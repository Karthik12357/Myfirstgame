import pygame
import sys
import random



fps_clock = pygame.time.Clock()  # set up the clock
clock = pygame.time.Clock()

from pygame.locals import *  # import pygame modules

pygame.mixer.pre_init(44100, -16, 2, 512)#mixer 
pygame.init()  # initiate pygame
pygame.mixer.set_num_channels(64)

pygame.display.set_caption('Environmentio')  # set the window name





WINDOW_SIZE = (1200, 800)  # set up window size

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)  # initiate screen

display = pygame.Surface((300, 200))
cursor_scale_surface = pygame.Surface((5, 10))

player_image = pygame.image.load('Codingal_game-Environmentgame/files/player.png').convert_alpha()
player_image.set_colorkey((255, 255, 255))
coin = pygame.image.load("Codingal_game-Environmentgame/files/coin.png").convert_alpha()
coin.set_colorkey((255,255,255))

img = pygame.image.load("Codingal_game-Environmentgame/files/crosshair-2.png").convert_alpha()
mountain_bg = pygame.image.load(
    "Codingal_game-Environmentgame/files/glacial_mountains_lightened.png").convert_alpha()
clouds = pygame.image.load("Codingal_game-Environmentgame/files/clouds_bg.png").convert_alpha()
grass_sound = pygame.mixer.Sound("Codingal_game-Environmentgame/files/grass_1.wav")
jump_sound = pygame.mixer.Sound("Codingal_game-Environmentgame/files/jump.wav")
menu_music = pygame.mixer.Sound("Codingal_game-Environmentgame/files/menu_music.wav")
pygame.mixer.Sound.set_volume(jump_sound, 10)
grass_sounds = [pygame.mixer.Sound('Codingal_game-Environmentgame/files/grass_0.wav'),
                pygame.mixer.Sound('Codingal_game-Environmentgame/files/grass_1.wav')]
click_sound = pygame.mixer.Sound("Codingal_game-Environmentgame/files/click.wav")
coin_collect_sound = pygame.mixer.Sound("Codingal_game-Environmentgame/files/coin_collect_sound.wav")
grass_sounds[0].set_volume(0.5)
grass_sounds[1].set_volume(0.5)

jumpland_sound = pygame.mixer.Sound("Codingal_game-Environmentgame/files/jumpland.wav")
jumpland_sound.set_volume(1)
earth_bg = pygame.image.load("Codingal_game-Environmentgame/files/world-globe_icon.png")
jumps = 0
earth = pygame.transform.scale(pygame.image.load("Codingal_game-Environmentgame/files/earth.bmp"),
                               (384, 384)) 
pygame.display.set_icon(earth)
#images and music are loaded
jump_timer = 0
grass_sound_timer = 0
start_game = False
#variables

grass_image = pygame.image.load('Codingal_game-Environmentgame/files/grass.png')
TILE_SIZE = grass_image.get_width()

dirt_image = pygame.image.load('Codingal_game-Environmentgame/files/dirt.png')
#tiles

#path loading function
def load_map(path):
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    _game_map = []
    for row in data:
        _game_map.append(list(row))
    return _game_map

#path loading for collectables
def load_map_collectables(path):  
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    collectables_map_ = []
    for row in data:
        collectables_map_.append(list(row))
    return collectables_map_


animation_frames = {}

#loading animations for the palyer
def load_animation(path, frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc)
        animation_image.set_colorkey((255, 255, 255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

#changing the animation type for each player
def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


player_action = 'idle'
player_frame = 0
player_flip = False
animation_database = {'run': load_animation('Codingal_game-Environmentgame/files/player_animations/run', [7, 7]),
                      'idle': load_animation('Codingal_game-Environmentgame/files/player_animations/idle',
                                             [7, 40, 40])}#animations' file location 

game_map = load_map('Codingal_game-Environmentgame/files/map')

#maps for platforms

#checks for colision
def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list


def collectables_collision_test(rect, tiles):
    collectables_hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            collectables_hit_list.append(tile)
    return collectables_hit_list

#movement
def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types
#menu loop
def menu_loop():
    game_map = load_map('Codingal_game-Environmentgame/files/map')
    menu_music.play()
    pygame.font.init()
    event = 0
    font = pygame.font.SysFont("Arial", 50)
    start_text_shade = font.render("START", False, (0, 0, 0))
    start_text_shade.set_alpha(100)

    quit_text_shade = font.render("QUIT", False, (0, 0, 0))
    quit_text_shade.set_alpha(100)

    _start_text_x = 0
    _quit_text_x = 0
    delta = 1
    stars = []
    star_c = [(255, 255, 255), (211, 211, 211), (240, 240, 240)]
    rotation_angle = 0
    _earth = earth.copy()
    _earth.set_alpha(100)

    for _ in range(100):
        stars.append([[random.randint(0, 1280), random.randint(0, 800)],
                      random.randint(2, 6), random.choice(star_c), random.randint(1, 4)])

    while True:
        screen.fill((34,139,34))
        mx, my = pygame.mouse.get_pos()
        rotation_angle += 0.1 / delta
        for star in stars:
            pygame.draw.circle(screen, star[2], [star[0][0] - (mx / 20),
                                                 star[0][1] - (my / 20)],
                               star[1])
            star[0][0] -= star[3] / delta
            if star[0][0] < -16:
                stars.remove(star)
                stars.append([[1280, random.randint(0, 800)],
                              random.randint(2, 6), random.choice(star_c), random.randint(1, 4)])

        screen.blit(pygame.transform.rotate(earth, rotation_angle), (458 - rotation_angle, 128 - rotation_angle))

        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        black = (255, 255, 255)
        grey = (150, 150, 170)
        start_color = black
        quit_color = black

        pygame.mouse.set_visible(False)
        start_text_x = 520 - mx
        quit_text_x = 534 - mx
        start_text_y = 600 - my
        quit_text_y = 660 - my

        start_text_click = False
        if start_text_x > -130:
            if start_text_x < 32:
                if start_text_y > -45:
                    if start_text_y < 20:
                        start_color = grey
                        start_text_click = True
        quit_game = False
        start_music=True
        if quit_text_x > -88:
            if quit_text_x < 32:
                if quit_text_y > -45:
                    if quit_text_y < 20:
                        quit_color = grey
                        quit_game = True
        if start_text_click:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == BUTTON_LEFT:
                    click_sound.play()
                    menu_music.set_volume(0)
                    game_loop()

                    return
        if quit_game:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == BUTTON_LEFT:
                    click_sound.play()
                    
                    pygame.quit()
                    sys.exit()

        start_text = font.render("START", False, start_color)
        quit_text = font.render("QUIT", False, quit_color)
        start_text_ = font.render("START", False, start_color)
        quit_text_ = font.render("QUIT", False, quit_color)

        if 520 <= mx <= 520 + start_text.get_width() and 600 <= my <= 600 + start_text.get_height():
            if _start_text_x > -20:
                _start_text_x -= 2 / delta
        else:
            if _start_text_x < 0:
                _start_text_x += 2 / delta

        if 534 <= mx <= 534 + quit_text.get_width() and 660 <= my <= 660 + quit_text.get_height():
            if _quit_text_x > -20:
                _quit_text_x -= 2 / delta
        else:
            if _quit_text_x < 0:
                _quit_text_x += 2 / delta

        start_text_.set_alpha(150)
        quit_text_.set_alpha(150)
        screen.blit(start_text_shade, (_start_text_x + 520 + 3 + 6, 600 + 2 + 5))
        screen.blit(quit_text_shade, (_quit_text_x + 534 + 3 + 6, 660 + 2 + 5))
        screen.blit(start_text_, (_start_text_x + 520 + 3, 600 + 2))
        screen.blit(quit_text_, (_quit_text_x + 534 + 3, 660 + 2))
        screen.blit(start_text, (_start_text_x + 520, 600))
        screen.blit(quit_text, (_quit_text_x + 534, 660))
        screen.blit(img, (mx, my))

        pygame.display.flip()
        clock.tick()

        delta = clock.get_fps() / 90
        if delta == 0:
            delta = 1

def coin_move(rect, movement, tiles):
    coin_collision_test = {'coin_top': False, 'coin_bottom': False, 'coin_right': False, 'coin_left': False}
    coin_hit_list = collectables_collision_test(rect, tiles)
    for tile in coin_hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            coin_collision_test['coin_right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            coin_collision_test['coin_left'] = True
    hit_list = collectables_collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            coin_collision_test['coin_bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            coin_collision_test['coin_top'] = True
    return rect, coin_collision_test


moving_right = False
moving_left = False

player_y_momentum = 0
air_timer = 0
true_scroll_value = [0, 0]

player_rect = pygame.Rect(50, 50, player_image.get_width(), player_image.get_height())
test_rect = pygame.Rect(100, 100, 100, 50)

score = 0
bg_scroll, scroll_x = 0, 0
green_bg = "Codingal_game-Environmentgame/green_bg.jpg"

def game_loop():  # game loop
    global bg_scroll, scroll_x, player_rect, rain_timer, spawner_direction, moving_right, moving_left, \
        player_y_momentum, player_action, player_frame, air_timer, player_flip, particle_timer, \
        spawner_x, score, grass_sound_timer, jump_timer, jumps,story,story_time
    
    game_start_game = True
    jumps = 0
    pygame.mixer.music.load("Codingal_game-Environmentgame/files/music.wav")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)
    story=True
    story_time=0
    moving_left=False
    moving_right=False
    
    
        

    
    while game_start_game:

        if grass_sound_timer > 0:
            grass_sound_timer -= 1
        display.fill((135, 206, 235))
        bg_scroll = 0
        scroll_x = 0
        display.blit(mountain_bg, (0, 0))
        display.blit(clouds, (0, 60))

        true_scroll_value[0] += (player_rect.x - true_scroll_value[0] - 152) / 5
        true_scroll_value[1] += (player_rect.y - true_scroll_value[1] - 106) / 5
        scroll_value = true_scroll_value.copy()
        scroll_value[0] = int(scroll_value[0])
        scroll_value[1] = int(scroll_value[1])

        tile_rects = []
        y = 0
        for row in game_map:
            x = 0
            for tile in row:
                if tile == '1':
                    display.blit(dirt_image, (x * 16 - scroll_value[0], y * 16 - scroll_value[1]))
                if tile == '2':
                    display.blit(grass_image, (x * 16 - scroll_value[0], y * 16 - scroll_value[1]))
                if tile == '3':
                    display.blit(coin, (x * 16 - scroll_value[0], y * 16 - scroll_value[1]))
                    if pygame.Rect(x * 16, y * 16, 16, 16).colliderect(player_rect):
                        row[x] = 0
                        coin_collect_sound.play()
                        score += 1

                if tile == '1' or tile == '2':
                    tile_rects.append(pygame.Rect(x * 16, y * 16, 16, 16))
                x += 1
            y += 1

        player_movement = [0, 0]

        if moving_right:
            player_movement[0] += 2

        if moving_left:
            player_movement[0] -= 2

        player_movement[1] += player_y_momentum
        player_y_momentum += 0.2
        if player_y_momentum > 3:
            player_y_momentum = 3

        if player_movement[0] == 0:
            player_action, player_frame = change_action(player_action, player_frame, 'idle')
        if player_movement[0] > 0:
            player_flip = False
            player_action, player_frame = change_action(player_action, player_frame, 'run')
        if player_movement[0] < 0:
            player_flip = True
            player_action, player_frame = change_action(player_action, player_frame, 'run')

        player_rect, collisions = move(player_rect, player_movement, tile_rects)

        if collisions['bottom']:
            player_y_momentum = 0
            air_timer = 0
            jumps = 0
            jump_timer += 1
            if jump_timer < 2:
                jumpland_sound.play()

            if player_movement[0] != 0:
                if grass_sound_timer == 0:
                    grass_sound_timer = 30
                    random.choice(grass_sounds).play()

        else:
            air_timer += 1
        if collisions['top']:
            player_y_momentum = 0
            air_timer = 0
            jumps = 0

        if collisions['left']:
            jumps = 0
        if collisions['right']:
            jumps = 0

        else:
            air_timer += 1

        player_frame += 1
        if player_frame >= len(animation_database[player_action]):
            player_frame = 0
        player_img_id = animation_database[player_action][player_frame]
        player_img = animation_frames[player_img_id]
        display.blit(pygame.transform.flip(player_img, player_flip, False),
                     (player_rect.x - scroll_value[0], player_rect.y - scroll_value[1]))

        for event in pygame.event.get():  # event loop
            if event.type == QUIT:  # check for window quit
                pygame.quit()  # stop pygame
                sys.exit()  # stop script
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    moving_right = True

                if event.key == K_LEFT:
                    moving_left = True
                if event.key==K_ESCAPE:
                    restart_menu_loop()

                if event.key == K_UP:
                    jumps += 1
                    jump_timer = 0

                    if jumps < 3:
                        jump_sound.play()
                        player_y_momentum = -5
            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    moving_right = False
                if event.key == K_LEFT:
                    moving_left = False

        pygame.mouse.set_visible(False)
        mx, my = pygame.mouse.get_pos()
        screen.blit(img, (mx, my))
        font = pygame.font.SysFont('Arial', 24)
        x_font = pygame.font.SysFont('Arial', 40)
        color = (255, 255, 255)

        text_surface = font.render(f'FPS: {fps_clock.get_fps(): .1f}', True, color)
        screen.blit(text_surface, (1090, 0))
        coin_surface = font.render(f'SCORE: {score}', True, color)
        screen.blit(coin_surface, (1090, 30))
        story_time+=1
        story_surface = x_font.render('HELP THE ALIEN TO COLLECT THE TRASH AND SAVE THE PLANET!!', True, color)
        menu_surface = font.render('Press the escape key to pause', True, color)
        tutorial_surface = x_font.render('Use the arrow keys to move', True, color)
        if story_time < 500:
            screen.blit(story_surface,(70,300))
        
            screen.blit(tutorial_surface,(410,400))
        screen.blit(menu_surface,(10,0))

        pygame.display.flip()
        surf = pygame.transform.scale(display, WINDOW_SIZE)
        screen.blit(surf, (0, 0))

        # update display
        fps_clock.tick(60)  # maintain 60 fps
        if score > 19:
            jump_sound.set_volume(0)
            grass_sound.set_volume(0)

            pygame.mixer.music.set_volume(0)
            win_loop()
        if player_rect.y>600:
            die_loop()
#button class 
class Button:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.font = pygame.font.Font(None, 24)
        self.text_ = 'Button' + self.__str__()
        self.color_text = (255, 255, 255)
        self.text = self.font.render(self.text_, True, self.color_text)
        self.sprite = pygame.Surface((1, 1))
        self.collide_ = False
        self.text_reflection = False
        self.text__ = self.text.copy()
        self.text__.set_alpha(120)
        self.x_, self.y_ = (0, 0)
        self.animation_type = 'left'
        self.animation_mm = 15

    def draw(self):
        if self.text_reflection:
            screen.blit(self.text__, (self.x + 3 - self.x_, self.y + 2 - self.y_))

        screen.blit(self.text, (self.x - self.x_, self.y - self.y_))

    def update_data(self, typename):
        if typename == 'text':
            self.text = self.font.render(self.text_, True, self.color_text)
            self.text__ = self.text.copy()
            self.text__.set_alpha(120)

    def collide(self, mx, my):
        if pygame.Rect(self.x, self.y, self.sprite.get_width(), self.sprite.get_height()).collidepoint(mx, my):
            return True
        return False

    def animate(self, delta):
        if self.animation_type == 'left':
            if self.collide_:
                self.x_ += (((self.x - self.x_) - (self.x - self.animation_mm)) / 5) / delta
            else:
                self.x_ += (((self.x - self.x_) - self.x) / 10) / delta

        if self.animation_type == 'right':
            if self.collide_:
                self.x_ += (((self.x - self.x_) - (self.x + self.animation_mm)) / 50) / delta
            else:
                self.x_ += (((self.x - self.x_) - self.x) / 10) / delta

        if self.animation_type == 'down':
            if self.collide_:
                self.y_ += (((self.y - self.y_) - (self.y + self.animation_mm)) / 5) / delta
            else:
                self.y_ += (((self.y - self.y_) - self.y) / 10) / delta

        if self.animation_type == 'up':
            if self.collide_:
                self.y_ += (((self.y - self.y_) - (self.y - self.animation_mm)) / 5) / delta
            else:
                self.y_ += (((self.y - self.y_) - self.y) / 10) / delta


def win_loop():
    
    global score,moving_left,moving_right,game_map,player_rect,score
    game_map = load_map('Codingal_game-Environmentgame/files/map')
    score=0
    menu_music.set_volume(1)
    done = False
    delta = 1
    ticks = 0
    font72 = pygame.font.SysFont('Arial', 72)
    win_text = font72.render('You Win!', True, (10, 10, 0))
    win_text_shade = win_text.copy()
    win_text_shade.set_alpha(120)
    win_text_x = -win_text.get_width()*2
    win_text_y = 96
    buttons = [Button(screen.get_width() // 2 - 128, 0)]
    buttons[0].font = font72
    buttons[0].text_ = 'Back To Menu'
    buttons[0].update_data('text')
    buttons[0].sprite = buttons[0].text
    buttons[0].text_reflection = True
    
    buttons[0].color_text = (0, 0, 10)
    buttons[0].animation_mm = 45
    buttons[0].y = screen.get_height() - 128
    buttons[0].x = ((screen.get_width() - buttons[0].text.get_width()) // 2) + 256
    dots = []
    mbut = []

    for _ in range(50):
        dots.append([[random.randint(0, screen.get_width()), random.randint(0, screen.get_height())],
                     random.randint(5, 10), random.randint(2, 3)])

    while not done:
        ticks += 1 / delta
        screen.fill((34,139,34))
        mx, my = pygame.mouse.get_pos()
        shader_cof = ((screen.get_width() - mx) // 10) // 5
        shader_cof_ = ((screen.get_height() - my) // 10) // 5

        for dot in dots:
            pygame.draw.circle(screen, (255,255,255), [dot[0][0] - shader_cof, dot[0][1] - shader_cof_], dot[1])
            if dot[0][1] > screen.get_height():
                dots.remove(dot)
                dots.append([[random.randint(0, screen.get_width()), -16],
                             random.randint(3, 8), random.randint(2, 3)])

            dot[0][1] += dot[2] / delta

        for button in buttons:
            button.draw()
            if button.collide(mx, my):
                button.collide_ = True
                if button.text_ == 'Back To Menu' and 1 in mbut:
                    player_rect.x = 25
                    player_rect.y = 50
                    score=0
                    menu_loop()
            else:
                button.collide_ = False
            button.animate(delta)

        screen.blit(win_text, (win_text_x, win_text_y))
        screen.blit(win_text_shade, (win_text_x + (10 - (shader_cof // 20)), win_text_y + (6 - (shader_cof_ // 20))))
        win_text_x -= ((win_text_x - ((screen.get_width() // 2 - win_text.get_width() // 2) - 96)) / 25) / delta

        for i in pygame.event.get():
            if i.type == QUIT:
                quit(0)

            if i.type == MOUSEBUTTONDOWN:
                click_sound.play()
                mbut.append(i.button)
            

        
        clock.tick()

        delta = clock.get_fps() / 90
        if delta == 0:
            delta = 1
        pygame.mouse.set_visible(False)
        mx, my = pygame.mouse.get_pos()
        screen.blit(img, (mx, my))
        pygame.display.update()
        moving_right = False
        moving_left = False 
death=0
def die_loop():
    global death,game_map,player_rect,score
    game_map = load_map('Codingal_game-Environmentgame/files/map')
    pygame.mixer.music.set_volume(0)
    
    
    
    done = False
    delta = 1
    ticks = 0
    font72 = pygame.font.SysFont('Arial', 72)
    win_text = font72.render('You Died!', True, (10, 10, 0))
    win_text_shade = win_text.copy()
    win_text_shade.set_alpha(120)
    win_text_x = -win_text.get_width()*2
    win_text_y = 96
    buttons = [Button(screen.get_width() // 2 - 128, 0)]
    buttons[0].font = font72
    buttons[0].text_ = 'Back To Menu'
    buttons[0].update_data('text')
    buttons[0].sprite = buttons[0].text
    buttons[0].text_reflection = True
    buttons[0].animation_type = 'right'
    buttons[0].color_text = (0, 0, 10)
    buttons[0].animation_mm = 45
    buttons[0].y = screen.get_height() - 128
    buttons[0].x = ((screen.get_width() - buttons[0].text.get_width()) // 2) + 256
    dots = []
    mbut = []
    

    for _ in range(50):
        dots.append([[random.randint(0, screen.get_width()), random.randint(0, screen.get_height())],
                     random.randint(5, 10), random.randint(2, 3)])

    while not done:
        ticks += 1 / delta
        screen.fill((255,0,0))
        mx, my = pygame.mouse.get_pos()
        shader_cof = ((screen.get_width() - mx) // 10) // 5
        shader_cof_ = ((screen.get_height() - my) // 10) // 5

        for dot in dots:
            pygame.draw.circle(screen, (255,255,255), [dot[0][0] - shader_cof, dot[0][1] - shader_cof_], dot[1])
            if dot[0][1] > screen.get_height():
                dots.remove(dot)
                dots.append([[random.randint(0, screen.get_width()), -16],
                             random.randint(3, 8), random.randint(2, 3)])

            dot[0][1] += dot[2] / delta

        for button in buttons:
            button.draw()
            if button.collide(mx, my):
                button.collide_ = True
                if button.text_ == 'Back To Menu' and 1 in mbut:
                    player_rect.x = 25
                    player_rect.y = 50
                    score=0
                    menu_loop()
            else:
                button.collide_ = False
            button.animate(delta)

        screen.blit(win_text, (win_text_x, win_text_y))
        screen.blit(win_text_shade, (win_text_x + (10 - (shader_cof // 20)), win_text_y + (6 - (shader_cof_ // 20))))
        win_text_x -= ((win_text_x - ((screen.get_width() // 2 - win_text.get_width() // 2) - 96)) / 25) / delta

        for i in pygame.event.get():
            if i.type == QUIT:
                quit(0)

            if i.type == MOUSEBUTTONDOWN:
                mbut.append(i.button)
                click_sound.play()
            

        
        clock.tick()

        delta = clock.get_fps() / 90
        if delta == 0:
            delta = 1
        pygame.mouse.set_visible(False)
        mx, my = pygame.mouse.get_pos()
        screen.blit(img, (mx, my))
        pygame.display.update()
def restart_menu_loop():
    global player_rect,moving_left,moving_right,score,game_map     
    done = False
    delta = 1
    ticks = 0
    font72 = pygame.font.SysFont('Arial', 72)
    win_text = font72.render('Pause Menu', True, (10, 10, 0))
    win_text_shade = win_text.copy()
    win_text_shade.set_alpha(120)
    win_text_x = -win_text.get_width()*2
    win_text_y = 96
    buttons = [Button(screen.get_width() // 2 -190, 0),Button(screen.get_width() // 2 - 150, 0),Button(screen.get_width() // 2 - 110, 0)]
    buttons[0].font = font72
    buttons[0].text_ = 'Resume'
    buttons[0].update_data('text')
    buttons[0].sprite = buttons[0].text
    buttons[0].text_reflection = True
    buttons[0].animation_type = 'right'
    buttons[0].color_text = (0, 0, 10)
    buttons[0].animation_mm = 45
    buttons[0].y = screen.get_height() - 220
    buttons[0].x = ((screen.get_width() - buttons[0].text.get_width()) // 2) + 256
    buttons[1].font = font72
    buttons[1].text_ = 'Quit'
    buttons[1].update_data('text')
    buttons[1].sprite = buttons[0].text
    buttons[1].text_reflection = True
    buttons[1].animation_type = 'right'
    buttons[1].color_text = (0, 0, 10)
    buttons[1].animation_mm = 45
    buttons[1].y = screen.get_height() - 150
    buttons[1].x = ((screen.get_width() - buttons[0].text.get_width()) // 2) + 256
    buttons[2].font = font72
    buttons[2].text_ = 'Main Menu'
    buttons[2].update_data('text')
    buttons[2].sprite = buttons[0].text
    buttons[2].text_reflection = True
    buttons[2].animation_type = 'right'
    buttons[2].color_text = (0, 0, 10)
    buttons[2].animation_mm = 45
    buttons[2].y = screen.get_height() - 80
    buttons[2].x = ((screen.get_width() - buttons[0].text.get_width()) // 2) + 256
    dots = []
    mbut = []
    

    for _ in range(50):
        dots.append([[random.randint(0, screen.get_width()), random.randint(0, screen.get_height())],
                     random.randint(5, 10), random.randint(2, 3)])

    while not done:
        ticks += 1 / delta
        screen.fill((255,0,0))
        mx, my = pygame.mouse.get_pos()
        shader_cof = ((screen.get_width() - mx) // 10) // 5
        shader_cof_ = ((screen.get_height() - my) // 10) // 5

        for dot in dots:
            pygame.draw.circle(screen, (255,255,255), [dot[0][0] - shader_cof, dot[0][1] - shader_cof_], dot[1])
            if dot[0][1] > screen.get_height():
                dots.remove(dot)
                dots.append([[random.randint(0, screen.get_width()), -16],
                             random.randint(3, 8), random.randint(2, 3)])

            dot[0][1] += dot[2] / delta

        for button in buttons:
            button.draw()
            if button.collide(mx, my):
                button.collide_ = True
                if button.text_ == 'Resume' and 1 in mbut:
                    moving_right=False
                    moving_left=False
                    
                    game_loop()
                if button.text_=='Quit' :
                    for i in pygame.event.get():           
                        if i.type == MOUSEBUTTONDOWN:
                            pygame.quit()
                            sys.exit()
                if button.text_=='Main Menu' and 1 in mbut :
                    player_rect.x = 25
                    player_rect.y = 50
                    score=0
                    game_map = load_map('Codingal_game-Environmentgame/files/map')
                    menu_loop()
                
            else:
                button.collide_ = False
            button.animate(delta)

        screen.blit(win_text, (win_text_x, win_text_y))
        screen.blit(win_text_shade, (win_text_x + (10 - (shader_cof // 20)), win_text_y + (6 - (shader_cof_ // 20))))
        win_text_x -= ((win_text_x - ((screen.get_width() // 2 - win_text.get_width() // 2) - 96)) / 25) / delta

        for i in pygame.event.get():           
            if i.type == MOUSEBUTTONDOWN:
                mbut.append(i.button)
                click_sound.play()
            

        
        clock.tick()

        delta = clock.get_fps() / 90
        if delta == 0:
            delta = 1
        pygame.mouse.set_visible(False)
        mx, my = pygame.mouse.get_pos()
        screen.blit(img, (mx, my))
        pygame.display.update()



menu_loop()
