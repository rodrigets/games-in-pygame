#! /usr/bin/env python
import pygame
from pygame.locals import *
from sys import exit
from random import randrange

counter=0
def main():

    pygame.init()
    pygame.mixer.pre_init(44100, 32, 2, 4096)
    pygame.font.init()


    font_name = pygame.font.get_default_font()
    game_font = pygame.font.SysFont(font_name, 72)

    screen = pygame.display.set_mode((956, 560))

    background_filename = 'seamless_space.png'
    background = pygame.image.load(background_filename).convert()

    ship = {
        'surface': pygame.image.load('ship.png').convert_alpha(),
        'position': [randrange(956), randrange(560)],
        'speed': {
            'x': 0,
            'y': 0
        }
    }

    exploded_ship = {
        'surface': pygame.image.load('ship_exploded.png').convert_alpha(),
        'position': [],
        'speed': {
            'x': 0,
            'y': 0
        },
        'rect': Rect(0, 0, 48, 48)
    }
	
	# sounds
    explosion_sound = pygame.mixer.Sound('boom.wav')
    explosion_played = False
    
    fire_sound = pygame.mixer.Sound('shot.ogg')
    fire_played = False
    
    pygame.display.set_caption('Asteroides')

    clock = pygame.time.Clock()

    global counter
    t=game_font.render("Score : "+str(counter),1,(255, 0, 0))
    screen.blit(t,(700,2))
    def create_asteroid():
        return {
            'surface': pygame.image.load('asteroid.png').convert_alpha(),
            'position': [randrange(892), -64],
            'speed': randrange(1, 11)
        }

    ticks_to_asteroid = 90
    asteroids = []
    
    # counter to prevent permanent fire
    ticks_to_shot = 15
    shots = []
    
    def create_shot(ship):
		# load image of bullet
	    surf = pygame.image.load('bullet.png')
	    # scale it to smaller size
	    surf = pygame.transform.scale(surf,(10,10))
	    ship_rect = get_rect(ship)
	    
	    return {
		    'surface': surf.convert_alpha(),
		    # create shot on tip of the ship
		    'position': [(ship_rect[0] + 0.5*ship_rect[2]) - 5,
		     ship_rect[1]],
		    'speed': 5
		}
	
    def move_shots():
	    for shot in shots:
		    shot['position'][1] -= shot['speed']
	
    def remove_missed_shots():
		# remove shots from game that leave screen
	    for shot in shots:
		    if shot['position'][1] < 0:
			        shots.remove(shot)
    
    def shoot_asteroids():
		# check for collisions between shots and asteroids
        for shot in shots:
            shot_rect = get_rect(shot)
            for asteroid in asteroids:
                if shot_rect.colliderect(get_rect(asteroid)):
                    shots.remove(shot)
                    asteroids.remove(asteroid)
                    global counter
                    counter+=5
				
    def move_asteroids():
        for asteroid in asteroids:
            asteroid['position'][1] += asteroid['speed']


    def remove_used_asteroids():
        for asteroid in asteroids:
            if asteroid['position'][1] > 560:
                asteroids.remove(asteroid)


    def get_rect(obj):
        return Rect(obj['position'][0],
                    obj['position'][1],
                    obj['surface'].get_width(),
                    obj['surface'].get_height())


    def ship_collided():
        ship_rect = get_rect(ship)
        for asteroid in asteroids:
            if ship_rect.colliderect(get_rect(asteroid)):
                return True
        return False

    collided = False
    collision_animation_counter = 0
    
    background_position = 0

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
            if event.type == QUIT:
                exit()

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_UP]:
            ship['speed']['y'] = -5
        elif pressed_keys[K_DOWN]:
            ship['speed']['y'] = 5

        if pressed_keys[K_LEFT]:
            ship['speed']['x'] = -5
        elif pressed_keys[K_RIGHT]:
            ship['speed']['x'] = 5
        
        if pressed_keys[K_SPACE] and ticks_to_shot <= 0:
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
		

		
        move_asteroids()
		
        #screen.blit(background, (0, 0))

        move_asteroids()
        move_shots()
        shoot_asteroids()
        t=game_font.render("Score : "+str(counter),True,(255, 0, 0))
        screen.blit(t,(700,2))
        for asteroid in asteroids:
            screen.blit(asteroid['surface'], asteroid['position'])
        
        for shot in shots:
            screen.blit(shot['surface'], shot['position'])
		
		
        if not collided:
            collided = ship_collided()
            ship['position'][0] += ship['speed']['x']
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

                playagain = game_font.render('Press R to Play Again', 13, (255, 0, 0))
                screen.blit(playagain,  (220, 350))

                pressed_keys = pygame.key.get_pressed()

                if pressed_keys[K_r]:
                    counter=0
                    main()

            else:
                exploded_ship['rect'].x = collision_animation_counter * 48
                exploded_ship['position'] = ship['position']
                screen.blit(exploded_ship['surface'], exploded_ship['position'],
                            exploded_ship['rect'])
                collision_animation_counter += 1

        pygame.display.update()
        time_passed = clock.tick(30)
        ticks_to_shot -= 1

        remove_used_asteroids()
        remove_missed_shots()

main()
