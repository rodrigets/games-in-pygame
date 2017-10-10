#! /usr/bin/env python
import os
from sys import exit
from random import randrange

import pygame

RES_FOLDER = 'resources'

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


def move_asteroids(asteroids):
    for asteroid in asteroids:
        asteroid['position'][1] += asteroid['speed']


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
        'speed': randrange(3, 9)
    }


def main():
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()

    pygame.font.init()

    font_name = pygame.font.get_default_font()
    game_font = pygame.font.SysFont(font_name, 72)

    screen = pygame.display.set_mode((956, 560))

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
    t = game_font.render("Score : " + str(counter), 1, (255, 0, 0))
    screen.blit(t, (700, 2))

    ticks_to_asteroid = 90
    asteroids = []

    # counter to prevent permanent fire
    ticks_to_shot = 15
    shots = []

    collided = False
    collision_animation_counter = 0

    background_position = 0

    # Clock to control FPS
    clock = pygame.time.Clock()

    while True:

        if not ticks_to_asteroid:
            ticks_to_asteroid = 90
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

        if pressed_keys[pygame.K_SPACE] and ticks_to_shot <= 0:
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
        t = game_font.render("Score : " + str(counter), True, (255, 0, 0))
        screen.blit(t, (700, 2))

        for asteroid in asteroids:
            screen.blit(asteroid['surface'], asteroid['position'])

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
                text = game_font.render('GAME OVER', 1, (255, 0, 0))
                screen.blit(text, (335, 250))

                playagain = game_font.render('Press R to Play Again', 13,
                                             (255, 0, 0))
                screen.blit(playagain, (220, 350))

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


main()
