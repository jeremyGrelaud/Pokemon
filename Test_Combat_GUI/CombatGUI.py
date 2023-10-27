import os
import pygame
import sys

# Add the directory containing 'pokemon.py' to sys.path
sys.path.append('../')
# Now we can import the 'pokemon' module and the others
from pokemon import *
from trainer import *
from random_encounters import generate_random_wild_pokemon

def GUI_encounter(player, wild_pokemon):

    # initialize pygame
    pygame.init()

    # set up the window
    WIDTH = 640
    HEIGHT = 480
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Pokemon Combat')

    # set up the colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)

    # load the images
    #specify the path
    image_path = os.getcwd()+"/sprites_gen1/"
    

    pokemon_image = pygame.image.load(image_path+player.pokemon_list[0].name+".png")
    enemy_pokemon_image = pygame.image.load(image_path+wild_pokemon.name+".png")

    # Load the background image
    background_image = pygame.image.load("background.png")

    # Resize the image to fit the window
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))


    # set up the fonts
    font = pygame.font.Font('freesansbold.ttf', 16)

    # set up the initial values
    current_pokemon = player.pokemon_list[0]

    pokemon_name = current_pokemon.name
    pokemon_level = current_pokemon.level
    pokemon_health = current_pokemon.hp
    pokemon_max_health = current_pokemon.max_hp


    enemy_pokemon_name = wild_pokemon.name
    enemy_pokemon_level = wild_pokemon.level
    enemy_pokemon_health = wild_pokemon.hp
    enemy_pokemon_max_health = wild_pokemon.max_hp


    # set up the rects
    # Symétrie verticale
    pokemon_image = pygame.transform.flip(pokemon_image, True, False)
    pokemon_image_rect = pokemon_image.get_rect()
    enemy_pokemon_image_rect = enemy_pokemon_image.get_rect()

    # Center the images vertically
    pokemon_image_rect.centery = (HEIGHT // 2) * 1.55
    enemy_pokemon_image_rect.centery = HEIGHT // 2.3

    # Calculate the horizontal positions to center the images
    pokemon_image_rect.centerx = WIDTH // 4 
    enemy_pokemon_image_rect.centerx = WIDTH * 3 // 4


    # Create a clock to control the framerate
    clock = pygame.time.Clock()

    # main game loop
    running = True
    while running:

        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the background
        window.fill(WHITE)
        # Draw the background image
        window.blit(background_image, (0, 0))

        # draw the sprites
        window.blit(pokemon_image, pokemon_image_rect)
        window.blit(enemy_pokemon_image, enemy_pokemon_image_rect)




        # Draw player Pokemon health bar
        pokemon_health_bar_rect = pygame.Rect(350, 400, 250, 30)
        pygame.draw.rect(window, WHITE, pokemon_health_bar_rect)
        pygame.draw.rect(window, GREEN, (pokemon_health_bar_rect.left + 2, pokemon_health_bar_rect.top + 2, (pokemon_health / pokemon_max_health) * (pokemon_health_bar_rect.width - 4), pokemon_health_bar_rect.height - 4))
        pygame.draw.rect(window, BLACK, pokemon_health_bar_rect, 2)

        # Draw enemy Pokemon health bar
        enemy_pokemon_health_bar_rect = pygame.Rect(30, 100, 250, 30)
        pygame.draw.rect(window, WHITE, enemy_pokemon_health_bar_rect)
        pygame.draw.rect(window, GREEN, (enemy_pokemon_health_bar_rect.left + 2, enemy_pokemon_health_bar_rect.top + 2, (enemy_pokemon_health / enemy_pokemon_max_health) * (enemy_pokemon_health_bar_rect.width - 4), enemy_pokemon_health_bar_rect.height - 4))
        pygame.draw.rect(window, BLACK, enemy_pokemon_health_bar_rect, 2)

        # Draw player Pokemon health text
        pokemon_health_text = font.render('HP: {}/{}'.format(pokemon_health, pokemon_max_health), True, BLACK)
        pokemon_health_text_rect = pokemon_health_text.get_rect()
        pokemon_health_text_rect.left = pokemon_health_bar_rect.left
        pokemon_health_text_rect.bottom = pokemon_health_bar_rect.top - 5
        window.blit(pokemon_health_text, pokemon_health_text_rect)

        # Draw enemy Pokemon health text
        enemy_pokemon_health_text = font.render('HP: {}/{}'.format(enemy_pokemon_health, enemy_pokemon_max_health), True, BLACK)
        enemy_pokemon_health_text_rect = enemy_pokemon_health_text.get_rect()
        enemy_pokemon_health_text_rect.right = enemy_pokemon_health_bar_rect.right
        enemy_pokemon_health_text_rect.bottom = enemy_pokemon_health_bar_rect.top - 5
        window.blit(enemy_pokemon_health_text, enemy_pokemon_health_text_rect)



        # draw the ally pokemon name and level
        pokemon_name_and_level_text = font.render(pokemon_name + ' Lv. {}'.format(pokemon_level), True, BLACK)
        pokemon_name_and_level_text_rect = pokemon_name_and_level_text.get_rect()
        pokemon_name_and_level_text_rect.left = pokemon_health_bar_rect.right - pokemon_name_and_level_text.get_width()
        pokemon_name_and_level_text_rect.bottom = pokemon_health_bar_rect.top - 5
        window.blit(pokemon_name_and_level_text, pokemon_name_and_level_text_rect)


        # Draw enemy Pokemon name and level
        enemy_pokemon_name_and_level_text = font.render(enemy_pokemon_name + ' Lv. {}'.format(enemy_pokemon_level), True, BLACK)
        enemy_pokemon_name_and_level_text_rect = enemy_pokemon_name_and_level_text.get_rect()
        enemy_pokemon_name_and_level_text_rect.right = enemy_pokemon_health_bar_rect.left + enemy_pokemon_name_and_level_text.get_width()
        enemy_pokemon_name_and_level_text_rect.bottom = enemy_pokemon_health_bar_rect.top - 5
        window.blit(enemy_pokemon_name_and_level_text, enemy_pokemon_name_and_level_text_rect)



        # Update the display
        pygame.display.update()

        # Control the framerate
        clock.tick(60)



###############################TESTS MAIN###########################################
pokemon_list = All_Pokemons().pokemon_list

pikachu = find_pokemon_by_name("Pikachu", pokemon_list)
pikachu1 = create_copy_pokemon(pikachu)
squirtle = find_pokemon_by_name("Squirtle", pokemon_list)
squirtle1 = create_copy_pokemon(squirtle)

squirtle1.go_to_lvl(38)
squirtle1.check_evolution()
squirtle1.check_evolution()
pikachu1.go_to_lvl(10)

player = Trainer("Ash", [pikachu1, squirtle1])


random_pokemon = generate_random_wild_pokemon()


GUI_encounter(player, random_pokemon)
