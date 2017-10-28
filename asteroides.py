#! /usr/bin/env python
import os
from sys import exit
from random import randrange
import platform
import pygame

RES_FOLDER = 'resources'
SCREEN_WIDTH = 956
SCREEN_HEIGHT = 560
FONT_SIZE = 40
counter = 0


def create_shot(spaceship):
    # load image of bullet
    surf = pygame.image.load(os.path.join(RES_FOLDER, 'bullet.png'))
    # scale it to smaller size
    surf = pygame.transform.scale(surf, (10, 10))
    ship_rect = get_rect(spaceship)

    return {
        'surface': surf.convert_alpha(),
        # create shot on tip of the ship
        'position': [(ship_rect[0] + 0.5 * ship_rect[2]) - 5,
                     ship_rect[1]],
        'speed': 8,
    }


def move_shots(shots):
    for shot in shots:
        shot['position'][1] -= shot['speed']


def remove_missed_shots(shots):
    # remove shots from game that leave screen
    for shot in shots:
        if shot['position'][1] < 0:
            shots.remove(shot)


def shoot_asteroids(shots, asteroids):
    for shot in shots:
        shot_rect = get_rect(shot)
        for asteroid in asteroids:
            if shot_rect.colliderect(get_rect(asteroid)):
                shots.remove(shot)
                asteroids.remove(asteroid)
                global counter
                counter += 5


# https://pygame.org/wiki/RotateCenter
def rotate_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


# Rotate asteroid with angular velocity and limiting it to 360 degrees.
def rotate_asteroid(asteroid):
    asteroid['angle'] = (asteroid['angle'] + asteroid['angular_velocity']) % 360


def move_asteroids(asteroids):
    for asteroid in asteroids:
        asteroid['position'][1] += asteroid['speed']
        rotate_asteroid(asteroid)


def remove_used_asteroids(asteroids):
    for asteroid in asteroids:
        if asteroid['position'][1] > 560:
            asteroids.remove(asteroid)


def get_rect(obj):
    return pygame.Rect(obj['position'][0],
                       obj['position'][1],
                       obj['surface'].get_width(),
                       obj['surface'].get_height())


def ship_collided(ship, asteroids):
    ship_rect = get_rect(ship)
    for asteroid in asteroids:
        if ship_rect.colliderect(get_rect(asteroid)):
            return True
    return False


def create_asteroid():
    return {
        'surface': pygame.image.load(
            os.path.join(RES_FOLDER, 'asteroid.png')).convert_alpha(),
        'position': [randrange(892), -64],
        'speed': randrange(3, 9),
        'angle': 0,
        'angular_velocity': randrange(1, 10)
    }

#setup music to play
#credit: Youtuber "The Music Element" - song: "Cool Space Music"
def play_music():
    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join(RES_FOLDER, "Cool Space Music.mp3"))
    pygame.mixer.music.play()

    if (pygame.mixer.music.get_busy()==False):
        pygame.mixer.music.load(os.path.join(RES_FOLDER, "Cool Space Music.mp3"))
        pygame.mixer.music.play()


def make_menu_button(text, width, height, text_color=(255, 0, 0), back_color=(100, 100, 100)):
    surface = pygame.Surface((width, height))
    surface.fill(back_color)
    pygame.draw.line(surface, (150, 150, 150), (0, 0), (width, 0))
    pygame.draw.line(surface, (150, 150, 150), (0, 0), (0, height))
    pygame.draw.line(surface, (50, 50, 50), (0, height-1), (width-1, height-1))
    pygame.draw.line(surface, (50, 50, 50), (width-1, 0), (width-1, height-1))
    font_name = pygame.font.get_default_font()
    font = pygame.font.SysFont(font_name, 72)
    text = font.render(text, 1, text_color)
    surface.blit(text, (width//2 - text.get_width()//2, height//2 - text.get_height()//2))
    return surface

def start_screen():
    START_GAME = "Start Game"
    QUIT_GAME = "Quit Game"

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((956, 560))
    menu_items = [START_GAME, QUIT_GAME]
    button_height = 75
    button_width = 360
    button_spacing = 15
    selection = 0

    show_start_screen = True

    while show_start_screen:
        buttons = []
        for i in range(len(menu_items)):
            text_color = (255, 80, 80) if i == selection else (192, 80, 80)
            back_color = (100, 100, 100) if i == selection else (80, 80, 80)
            text = menu_items[i]
            button_surface = make_menu_button(text, button_width, button_height - button_spacing, text_color, back_color)

            left = screen.get_width() // 2 - button_width // 2
            top = screen.get_height() // 2 - button_height * len(menu_items) // 2 + button_height * i
            button = screen.blit(button_surface, (left, top))
            buttons.append(button)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        pressed_keys = pygame.key.get_pressed()

        activated = None
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(menu_items)):
                if buttons[i].collidepoint(pygame.mouse.get_pos()):
                    if selection == i:
                        activated = i
                    else:
                        selection = i

        if pressed_keys[pygame.K_UP] and selection > 0:
                selection -= 1
        elif pressed_keys[pygame.K_DOWN] and selection < len(menu_items)-1:
                selection += 1
        elif pressed_keys[pygame.K_RETURN]:
            activated = selection
        elif pressed_keys[pygame.K_q]:
            show_start_screen = False

        if activated is not None:
            if menu_items[activated] == START_GAME:
                show_start_screen = False
                main()
            if menu_items[activated] == QUIT_GAME:
                show_start_screen = False

        pygame.display.update()
        clock.tick(60)

def main():
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()

    pygame.font.init()

    font_name = pygame.font.get_default_font()
    if platform.system().lower() == "darwin":
        game_font = pygame.font.Font(font_name, FONT_SIZE)
    else:
        game_font = pygame.font.SysFont(font_name, FONT_SIZE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # list to store multiple background images.
    background_images = [
        os.path.join(RES_FOLDER, 'seamless_space.png'),
        os.path.join(RES_FOLDER, 'bg_big.png'),
		os.path.join(RES_FOLDER, 'space3.jpg'),
    ]
    background_images_counter = 0
    background = pygame.image.load(
        background_images[background_images_counter]).convert()
    background_flag = 0

    ship = {
        'surface': pygame.image.load(
            os.path.join(RES_FOLDER, 'ship.png')).convert_alpha(),
        'position': [randrange(-10, 918), randrange(-10, 520)],
        'speed': {
            'x': 0,
            'y': 0
        }
    }

    exploded_ship = {
        'surface': pygame.image.load(
            os.path.join(RES_FOLDER, 'ship_exploded.png')).convert_alpha(),
        'position': [],
        'speed': {
            'x': 0,
            'y': 0
        },
        'rect': pygame.Rect(0, 0, 48, 48)
    }

    # sounds
    explosion_sound = pygame.mixer.Sound(os.path.join(RES_FOLDER, 'boom.wav'))
    explosion_played = False

    fire_sound = pygame.mixer.Sound(os.path.join(RES_FOLDER, 'shot.ogg'))

    pygame.display.set_caption('Asteroides')

    global counter

    asteroids_intensity = 0
    ticks_to_asteroid = 90
    asteroids = []

    # counter to prevent permanent fire
    ticks_to_shot = 15
    shots = []

    collided = False
    collision_animation_counter = 0

    background_position = 0

    angle = 0

    play_music()

    # Clock to control FPS
    clock = pygame.time.Clock()

    while True:

        if not ticks_to_asteroid:

            if (counter != 0) and ((counter % 40) == 0) and (counter <= 160):
                asteroids_intensity = (counter/40*15)

            ticks_to_asteroid = 90 - asteroids_intensity

            asteroids.append(create_asteroid())
        else:
            ticks_to_asteroid -= 1

        ship['speed'] = {
            'x': 0,
            'y': 0
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_UP]:
            ship['speed']['y'] = -5

        elif pressed_keys[pygame.K_DOWN]:
            ship['speed']['y'] = 5

        if pressed_keys[pygame.K_LEFT]:
            ship['speed']['x'] = -10

        elif pressed_keys[pygame.K_RIGHT]:
            ship['speed']['x'] = 10

        if pressed_keys[pygame.K_SPACE] and ticks_to_shot <= 0 and not collided:
            # play sound
            fire_sound.play()
            shots.append(create_shot(ship))
            # set timer for next possible shot
            ticks_to_shot = 15

        # moving the background to simulate space travel
        # blint background relative to position of prior iteration
        rel_pos = background_position % background.get_rect().height

        # positioning takes height of backdrop into account
        screen.blit(background, (0, rel_pos - background.get_rect().height))

        # end of backdrop is reached
        if rel_pos < 560:
            screen.blit(background, (0, rel_pos))

        # speed of movement of background
        background_position += 2

        move_asteroids(asteroids)
        move_shots(shots)

        shoot_asteroids(shots=shots, asteroids=asteroids)
        
        score_text = "Score : " + str(counter)
        score_text_size = game_font.size(score_text)
        t = game_font.render(score_text, True, (255, 0, 0))
        screen.blit(t, (SCREEN_WIDTH - score_text_size[0] - 5 , 5))


        for asteroid in asteroids:
            screen.blit(rotate_center(asteroid['surface'], asteroid['angle']), asteroid['position'])

        for shot in shots:
            screen.blit(shot['surface'], shot['position'])

        if not collided:
            collided = ship_collided(ship=ship, asteroids=asteroids)
            if ((ship['position'][0] + ship['speed']['x']) > -10) and (
                        (ship['position'][0] + ship['speed']['x']) < 918):
                ship['position'][0] += ship['speed']['x']

            if (ship['position'][1] + ship['speed']['y'] > -10) and (
                            ship['position'][1] + ship['speed']['y'] < 520):
                ship['position'][1] += ship['speed']['y']

            screen.blit(ship['surface'], ship['position'])
        else:
            if not explosion_played:
                explosion_played = True
                explosion_sound.play()
                ship['position'][0] += ship['speed']['x']
                ship['position'][1] += ship['speed']['y']

                screen.blit(ship['surface'], ship['position'])
            elif collision_animation_counter == 3:
                game_over_text = 'GAME OVER'
                game_over_text_size = game_font.size(game_over_text)
                text = game_font.render(game_over_text, True, (255, 0, 0))
                screen.blit(text, (SCREEN_WIDTH/2 - game_over_text_size[0]/2, 250))

                play_again_text = 'Press R to Play Again'
                play_again_text_size = game_font.size(play_again_text)
                playagain = game_font.render(play_again_text, True, (255, 0, 0))
                screen.blit(playagain, (SCREEN_WIDTH/2 - play_again_text_size[0]/2, 350))

                pressed_keys = pygame.key.get_pressed()

                if pressed_keys[pygame.K_r]:
                    counter = 0
                    main()

            else:
                exploded_ship['rect'].x = collision_animation_counter * 48
                exploded_ship['position'] = ship['position']
                screen.blit(exploded_ship['surface'],
                            exploded_ship['position'],
                            exploded_ship['rect'])
                collision_animation_counter += 1

        pygame.display.update()
        ticks_to_shot -= 1

        if counter % 40 == 0 and counter != 0 and background_flag == 0:
            background_images_counter += 1
            if len(background_images):
                aux = background_images[
                    background_images_counter % len(background_images)
                ]
                background = pygame.image.load(aux).convert()
                background_flag = 1

        elif counter % 40 != 0:
            background_flag = 0

        remove_used_asteroids(asteroids)
        remove_missed_shots(shots)

        # FPS control: 30 FPS
        clock.tick(60)


start_screen()
