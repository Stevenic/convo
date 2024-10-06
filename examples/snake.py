import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants for the game
CELL_SIZE = 20
GRID_SIZE = 20
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (255, 255, 255)
FPS = 6

# Directions for movement
directions = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0)
}

# Create game window
window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Snake Game")

# Snake setup
snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]
current_direction = "right"

# Place initial food item
food = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

# Clock to control game speed
clock = pygame.time.Clock()

# Function to place food randomly on the grid
def place_food():
    while True:
        new_food = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if new_food not in snake:
            return new_food

# Function to display the game over message and wait for key press
def game_over():
    font = pygame.font.SysFont("arial", 24)
    game_over_text_1 = font.render("Game Over!", True, (255, 255, 255))
    game_over_text_2 = font.render(f"Your score is {len(snake)}.", True, (255, 255, 255))
    game_over_text_3 = font.render("Press any key to restart.", True, (255, 255, 255))
    window.fill(BACKGROUND_COLOR)
    window.blit(game_over_text_1, (WINDOW_SIZE // 2 - game_over_text_1.get_width() // 2, WINDOW_SIZE // 2 - 60))
    window.blit(game_over_text_2, (WINDOW_SIZE // 2 - game_over_text_2.get_width() // 2, WINDOW_SIZE // 2 - 20))
    window.blit(game_over_text_3, (WINDOW_SIZE // 2 - game_over_text_3.get_width() // 2, WINDOW_SIZE // 2 + 20))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False

# Game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and current_direction != "down":
                current_direction = "up"
            elif event.key == pygame.K_DOWN and current_direction != "up":
                current_direction = "down"
            elif event.key == pygame.K_LEFT and current_direction != "right":
                current_direction = "left"
            elif event.key == pygame.K_RIGHT and current_direction != "left":
                current_direction = "right"

    # Calculate new head position
    head_x, head_y = snake[0]
    delta_x, delta_y = directions[current_direction]
    new_head = (head_x + delta_x, head_y + delta_y)

    # Check for collisions
    if (new_head in snake or
            new_head[0] < 0 or new_head[0] >= GRID_SIZE or
            new_head[1] < 0 or new_head[1] >= GRID_SIZE):
        game_over()
        snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]
        current_direction = "right"
        food = place_food()
        continue

    # Move the snake
    snake.insert(0, new_head)

    # Check if snake eats the food
    if new_head == food:
        food = place_food()
    else:
        snake.pop()

    # Draw everything
    window.fill(BACKGROUND_COLOR)
    pygame.draw.rect(window, BORDER_COLOR, (0, 0, WINDOW_SIZE, WINDOW_SIZE), 2)  # Draw the border
    for segment in snake:
        pygame.draw.rect(window, SNAKE_COLOR, (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(window, FOOD_COLOR, (food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Update the display
    pygame.display.flip()

    # Control the game speed
    clock.tick(FPS)