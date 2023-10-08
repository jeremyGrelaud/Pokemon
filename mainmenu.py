#Just a starting screen menu for now 

import pygame

# Initialize Pygame
pygame.init()

# Set up the Pygame window
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Game")

# Load any images or fonts that you will use in the menu screen
bg_image = pygame.image.load("menu_bg.png").convert()
font = pygame.font.Font(None, 32)

# Define a variable to store the start button rect
start_button_rect = None

# Create a function to draw the menu screen
def draw_menu():
  global start_button_rect
  
  # Draw the background image
  screen.blit(bg_image, (0, 0))

  # Draw a start game button
  start_button_text = font.render("Start Game", True, (220, 36, 36))
  start_button_rect = start_button_text.get_rect()
  start_button_rect.center = (420, 450)
  screen.blit(start_button_text, start_button_rect)



# Create a function to start the game
def start_game():
  # Initialize the game state
  game_running = True
  print("The journey begins")
  # Game loop
  while game_running:
    # Check for input events
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        game_running = False
      # Handle other input events here

    # Update the game state

    # Draw the game screen

  # Quit the game
  pygame.quit()


# Main game loop
running = True
while running:
  # Check for input events
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.MOUSEBUTTONDOWN:
      # Check if the player clicked on the start game button
      mouse_pos = pygame.mouse.get_pos()
      #print(mouse_pos)
      if start_button_rect.collidepoint(mouse_pos):
        # Start the game
        start_game()

  # Draw the menu screen
  draw_menu()

  # Update the display
  pygame.display.flip()

# Quit Pygame
pygame.quit()
