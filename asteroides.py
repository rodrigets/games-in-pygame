#! /usr/bin/env python
import os
from sys import exit
from random import randrange
import random
import platform
import pygame
import math
from math import sin, cos, pi, atan2

RES_FOLDER = 'resources'
SCREEN_WIDTH = 956
SCREEN_HEIGHT = 560
FONT_SIZE = 40
counter = 0
counter2 = 0


def create_ship():
    ship = {
        'surface': pygame.image.load(
            os.path.join(RES_FOLDER, 'ship.png')).convert_alpha(),
        'position': [randrange(-10, 918), randrange(-10, 520)],
        'speed': {
            'x': 0,
            'y': 0
        },
        'ticks_to_shot': 15,
        'collided': False,
        'collision_animation_counter': 0,
        'explosion_played': False,
        'dead': False,
        'player': ''
    }
    return ship


def create_exploded_ship():
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
    return exploded_ship


def create_shot(spaceship):
    # load image of bullet
    surf = pygame.image.load(os.path.join(RES_FOLDER, 'bullet.png'))
    # scale it to smaller size
    surf = pygame.transform.scale(surf, (10, 10))
    ship_rect = get_rect(spaceship)
    player = spaceship['player']
    return {
        'surface': surf.convert_alpha(),
        # create shot on tip of the ship
        'position': [(ship_rect[0] + 0.5 * ship_rect[2]) - 5,
                     ship_rect[1]],
        'speed': 8,
        'player': player,
    }


def create_alien_ship(ships):
    # choose one of the ships as target for fire
    fire_target = random.choice(ships)
 
    # load image of ship
    surf = pygame.image.load(os.path.join(RES_FOLDER, 'aliens.png'))
    
    # scale it to smaller size and make it quadratic
    surf = pygame.transform.scale(surf, (70, 70))
    return {
        'surface': surf.convert_alpha(),
        'position': [randrange(892), -64],
        'speed': 4,
        'fire_target': fire_target,
        'angle': 0,
        'ticks_to_laser': 25
    }


def get_alien_ship_rotation_angle(alien_ship):
    # get center of alien ship
    alien_center = tuple(map(sum, zip(alien_ship['surface'].get_rect().center, tuple(alien_ship['position']))))

    # get center of target ship
    fire_target = alien_ship['fire_target']
    target_center = tuple(map(sum, zip(fire_target['surface'].get_rect().center, tuple(fire_target['position']))))
    
    # calculate angle between alien ship and target center
    radiant_angle = math.atan2(target_center[0] - alien_center[0], target_center[1] - alien_center[1])

    # convert to degrees
    degree_angle = math.degrees(radiant_angle)
    
    # update angle on alien ship information
    alien_ship['angle'] = degree_angle

    return degree_angle


def alien_shoot_laser(alien_ship):
    # find current position of ship center
    alien_center = list(map(sum, zip(alien_ship['surface'].get_rect().center, tuple(alien_ship['position']))))
    
    # find position of the target center
    fire_target = alien_ship['fire_target']
    target_center = list(map(sum, zip(fire_target['surface'].get_rect().center, tuple(fire_target['position']))))

    # calculate angle to target
    x_dist = - alien_center[0] + target_center[0]
    y_dist = - alien_center[1] + target_center[1]
    angle_to_target = (atan2(-y_dist, x_dist) % (2 * pi))

    # load image of alien bullet
    surf = pygame.image.load(os.path.join(RES_FOLDER, 'alien_bullet.png'))
    
    # scale it
    surf = pygame.transform.scale(surf, (10, 10))

    return {
        'surface': surf.convert_alpha(),
        'position': alien_center,
        'angle': angle_to_target,
        'speed': 5
    }


def move_alien_shots(alien_shots):
    for alien_shot in alien_shots:
        alien_shot['position'][0] += cos(alien_shot['angle']) * alien_shot['speed']
        alien_shot['position'][1] -= sin(alien_shot['angle']) * alien_shot['speed']


def remove_alien_shots(alien_shots):
    for alien_shot in alien_shots:
        out_of_bounds = alien_shot['position'][1] > 560
        out_of_bounds = out_of_bounds or alien_shot['position'][1] < 0 
        out_of_bounds = out_of_bounds or alien_shot['position'][0] < 0
        out_of_bounds = out_of_bounds or alien_shot['position'][0] > 956
        if out_of_bounds:
            alien_shots.remove(alien_shot)


def move_alien_ships(alien_ships):
    for alien_ship in alien_ships:
        alien_ship['position'][1] += alien_ship['speed']


def remove_alien_ships(alien_ships):
    for alien_ship in alien_ships:
        if alien_ship['position'][1] > 560:
            alien_ships.remove(alien_ship)


def move_shots(shots):
    for shot in shots:
        shot['position'][1] -= shot['speed']


def remove_missed_shots(shots):
    """
    Remove shots from game that leave screen
    """
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
                if shot['player'] == '1':
                    global counter
                    counter += 5
                if shot['player'] == '2':
                    global counter2
                    counter2 += 5


def shoot_alien_ships(shots, alien_ships):
    for shot in shots:
        shot_rect = get_rect(shot)
        for alien_ship in alien_ships:
            if shot_rect.colliderect(get_rect(alien_ship)):
                shots.remove(shot)
                alien_ships.remove(alien_ship)
                if shot['player'] == '1':
                    global counter
                    counter += 10
                if shot['player'] == '2':
                    global counter2
                    counter2 += 10


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


def ship_collided(ship, asteroids, alien_ships, alien_shots):
    ship_rect = get_rect(ship)
    for asteroid in asteroids:
        if ship_rect.colliderect(get_rect(asteroid)):
            return True
    for alien_ship in alien_ships:
        if ship_rect.colliderect(get_rect(alien_ship)):
            return True
    for alien_shot in alien_shots:
        if ship_rect.colliderect(get_rect(alien_shot)):
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


def play_music():
    """
    Setup music to play
    credit: Youtuber "The Music Element" - song: "Cool Space Music"
    """
    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join(RES_FOLDER, "Cool Space Music.mp3"))
    pygame.mixer.music.play()

    if pygame.mixer.music.get_busy() is False:
        pygame.mixer.music.load(os.path.join(RES_FOLDER, "Cool Space Music.mp3"))
        pygame.mixer.music.play()


def draw_button(screen, left, top, text):
    button_width = 310
    button_height = 65

    pygame.draw.line(screen, (150, 150, 150), [left, top], [left+button_width, top], 5)
    pygame.draw.line(screen, (150, 150, 150), [left, top-2], [left, top+button_height], 5)
    pygame.draw.line(screen, (50, 50, 50), [left, top+button_height], [left+button_width, top+button_height], 5)
    pygame.draw.line(screen, (50, 50, 50), [left+button_width, top+button_height], [left+button_width, top], 5)
    pygame.draw.rect(screen, (100, 100, 100), (left, top, button_width, button_height))

    font_name = pygame.font.get_default_font()
    start_screen_font = pygame.font.SysFont(font_name, 72)
    t = start_screen_font.render(text, 1, (255, 0, 0))
    return screen.blit(t, (left+20, top+10))


def start_screen():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((956, 560))

    show_start_screen = True

    while show_start_screen:
        one_player_button = draw_button(screen, 330, 190, "One Player")
        two_player_button = draw_button(screen, 330, 305, "Two Player")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            # noinspection PyUnusedLocal
            pressed_keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()

            singleplayer_selected = event.type == pygame.MOUSEBUTTONDOWN and one_player_button.collidepoint(mouse_pos)
            doubleplayer_selected = event.type == pygame.MOUSEBUTTONDOWN and two_player_button.collidepoint(mouse_pos)

            if singleplayer_selected:
                show_start_screen = main(is_two_player=False)
                screen.fill((0, 0, 0))
            elif doubleplayer_selected:
                show_start_screen = main(is_two_player=True)
                screen.fill((0, 0, 0))

        pygame.display.update()
        clock.tick(60)


def main(is_two_player):
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

    ships = [create_ship()]
    ships[0]['player'] = '1'
    exploded_ships = [create_exploded_ship()]

    if is_two_player:
        ships.append(create_ship())
        ships[1]['player'] = '2'
        exploded_ships.append(create_exploded_ship())

    death_ct = 0

    # sounds
    explosion_sound = pygame.mixer.Sound(os.path.join(RES_FOLDER, 'boom.wav'))

    fire_sound = pygame.mixer.Sound(os.path.join(RES_FOLDER, 'shot.ogg'))

    pygame.display.set_caption('Asteroides')

    global counter
    global counter2

    counter = 0
    counter2 = 0

    asteroids_intensity = 0
    ticks_to_asteroid = 90

    alien_ships_intensity = 0
    ticks_to_alien_ship = 200

    alien_ships = []
    asteroids = []
    shots = []
    alien_shots = []

    background_position = 0

    # angle = 0

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
        
        if not ticks_to_alien_ship:
            if (counter != 0) and ((counter % 50) == 0) and (counter <= 200):
                alien_ships_intensity = (counter/50*15)
            ticks_to_alien_ship = 200 - alien_ships_intensity

            alien_ships.append(create_alien_ship(ships))
        else:
            ticks_to_alien_ship -= 1

        # shooting of alien ships
        for alien_ship in alien_ships:
            # check if ship can shoot again
            if alien_ship['ticks_to_laser'] > 0:
                alien_ship['ticks_to_laser'] -= 1
            else:
                alien_shots.append(alien_shoot_laser(alien_ship))
                alien_ship['ticks_to_laser'] = 25

        for ship in ships:
            ship['speed'] = {
                'x': 0,
                'y': 0
            }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        pressed_keys = pygame.key.get_pressed()

        # First player
        if pressed_keys[pygame.K_UP]:
            ships[0]['speed']['y'] = -5
        elif pressed_keys[pygame.K_DOWN]:
            ships[0]['speed']['y'] = 5
        if pressed_keys[pygame.K_LEFT]:
            ships[0]['speed']['x'] = -10
        elif pressed_keys[pygame.K_RIGHT]:
            ships[0]['speed']['x'] = 10
        if pressed_keys[pygame.K_SPACE] and ships[0]['ticks_to_shot'] <= 0 and not ships[0]['collided']:
            # play sound
            fire_sound.play()
            shots.append(create_shot(ships[0]))
            # set timer for next possible shot
            ships[0]['ticks_to_shot'] = 15

        # Second player
        if is_two_player:
            if pressed_keys[pygame.K_w]:
                ships[1]['speed']['y'] = -5
            elif pressed_keys[pygame.K_s]:
                ships[1]['speed']['y'] = 5
            if pressed_keys[pygame.K_a]:
                ships[1]['speed']['x'] = -10
            elif pressed_keys[pygame.K_d]:
                ships[1]['speed']['x'] = 10
            if pressed_keys[pygame.K_x] and ships[1]['ticks_to_shot'] <= 0 and not ships[1]['collided']:
                # play sound
                fire_sound.play()
                shots.append(create_shot(ships[1]))
                # set timer for next possible shot
                ships[1]['ticks_to_shot'] = 15

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
        move_alien_ships(alien_ships)
        move_alien_shots(alien_shots)

        shoot_asteroids(shots=shots, asteroids=asteroids)
        shoot_alien_ships(shots, alien_ships)

        score_text = "Score Player 1: " + str(counter)
        t = game_font.render(score_text, True, (0, 0, 255))
        screen.blit(t, (0, 5))

        if is_two_player:
            score_text2 = "Score Player 2: " + str(counter2)
            score_text_size2 = game_font.size(score_text2)
            t2 = game_font.render(score_text2, True, (255, 0, 0))
            screen.blit(t2, (SCREEN_WIDTH - score_text_size2[0] - 16, 5))

        for asteroid in asteroids:
            screen.blit(rotate_center(asteroid['surface'], asteroid['angle']), asteroid['position'])
        
        for alien_ship in alien_ships:
            alient_ship_rotation = get_alien_ship_rotation_angle(alien_ship)
            screen.blit(rotate_center(alien_ship['surface'], alient_ship_rotation), alien_ship['position'])

        for shot in shots:
            screen.blit(shot['surface'], shot['position'])

        for alien_shot in alien_shots:
            screen.blit(alien_shot['surface'], alien_shot['position'])

        if death_ct == len(ships):
            game_over_text = 'GAME OVER'
            game_over_text_size = game_font.size(game_over_text)
            text = game_font.render(game_over_text, True, (255, 0, 0))
            screen.blit(text, (SCREEN_WIDTH/2 - game_over_text_size[0]/2, 250))

            play_again_text = 'Press R to restart, Esc for the main menu, or Q to quit'
            play_again_text_size = game_font.size(play_again_text)
            playagain = game_font.render(play_again_text, True, (255, 0, 0))
            screen.blit(playagain, (SCREEN_WIDTH/2 - play_again_text_size[0]/2, 350))

            pressed_keys = pygame.key.get_pressed()

            if pressed_keys[pygame.K_r]:
                return main(is_two_player)

            if pressed_keys[pygame.K_ESCAPE]:
                return True

            if pressed_keys[pygame.K_q]:
                return False

        else:
            for ship, exploded_ship in zip(ships, exploded_ships):
                if not ship['collided']:
                    ship['collided'] = ship_collided(ship, asteroids, alien_ships, alien_shots)
                    if ((ship['position'][0] + ship['speed']['x']) > -10) and (
                                (ship['position'][0] + ship['speed']['x']) < 918):
                        ship['position'][0] += ship['speed']['x']

                    if (ship['position'][1] + ship['speed']['y'] > -10) and (
                                    ship['position'][1] + ship['speed']['y'] < 520):
                        ship['position'][1] += ship['speed']['y']

                    screen.blit(ship['surface'], ship['position'])
                elif not ship['dead']:
                    if not ship['explosion_played']:
                        ship['explosion_played'] = True
                        explosion_sound.play()
                        ship['position'][0] += ship['speed']['x']
                        ship['position'][1] += ship['speed']['y']

                        screen.blit(ship['surface'], ship['position'])
                    elif ship['collision_animation_counter'] == 3:
                        death_ct += 1
                        ship['dead'] = True
                    else:
                        exploded_ship['rect'].x = ship['collision_animation_counter'] * 48
                        exploded_ship['position'] = ship['position']
                        screen.blit(exploded_ship['surface'],
                                    exploded_ship['position'],
                                    exploded_ship['rect'])
                        ship['collision_animation_counter'] += 1

        pygame.display.update()

        for ship in ships:
            ship['ticks_to_shot'] -= 1

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
        remove_alien_shots(alien_shots)

        # FPS control: 30 FPS
        clock.tick(60)


start_screen()
