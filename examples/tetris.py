import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
GRID_SIZE = 30
COLUMNS = 10
ROWS = 20

# Colors
COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (160, 32, 240),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0)
}

# Tetromino shapes
TETROMINOES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]]
}

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()

# Grid setup
def create_grid():
    return [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLUMNS):
            if grid[y][x] != 0:
                pygame.draw.rect(surface, COLORS[grid[y][x]], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, (0, 0, 0), (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
            else:
                pygame.draw.rect(surface, (40, 40, 40), (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.color = random.choice(list(COLORS.keys()))
        self.blocks = TETROMINOES[self.color]
        self.x = COLUMNS // 2 - len(self.blocks[0]) // 2
        self.y = 0

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotate(self):
        self.blocks = [list(row) for row in zip(*self.blocks[::-1])]

def valid_move(tetromino, grid, dx, dy):
    for y, row in enumerate(tetromino.blocks):
        for x, cell in enumerate(row):
            if cell:
                new_x = tetromino.x + x + dx
                new_y = tetromino.y + y + dy
                if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS:
                    return False
                if new_y >= 0 and grid[new_y][new_x] != 0:
                    return False
    return True

def lock_tetromino(grid, tetromino):
    for y, row in enumerate(tetromino.blocks):
        for x, cell in enumerate(row):
            if cell and tetromino.y + y >= 0:
                grid[tetromino.y + y][tetromino.x + x] = tetromino.color

def clear_rows(grid):
    cleared_rows = 0
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    cleared_rows = ROWS - len(new_grid)
    for _ in range(cleared_rows):
        new_grid.insert(0, [0 for _ in range(COLUMNS)])
    return new_grid, cleared_rows

def draw_score(surface, score):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', 1, (255, 255, 255))
    surface.blit(label, (10, 10))

def main():
    grid = create_grid()
    running = True
    current_tetromino = Tetromino(random.choice(list(TETROMINOES.keys())))
    fall_time = 0
    score = 0

    while running:
        screen.fill((0, 0, 0))
        fall_time += clock.get_rawtime()
        clock.tick()

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and valid_move(current_tetromino, grid, -1, 0):
                    current_tetromino.move(-1, 0)
                elif event.key == pygame.K_RIGHT and valid_move(current_tetromino, grid, 1, 0):
                    current_tetromino.move(1, 0)
                elif event.key == pygame.K_UP:
                    current_tetromino.rotate()
                    if not valid_move(current_tetromino, grid, 0, 0):
                        current_tetromino.rotate()  # Revert rotation if invalid
                elif event.key == pygame.K_DOWN and valid_move(current_tetromino, grid, 0, 1):
                    current_tetromino.move(0, 1)
                elif event.key == pygame.K_SPACE:
                    while valid_move(current_tetromino, grid, 0, 1):
                        current_tetromino.move(0, 1)

        # Move tetromino down
        if fall_time > 1000:
            if valid_move(current_tetromino, grid, 0, 1):
                current_tetromino.move(0, 1)
            else:
                lock_tetromino(grid, current_tetromino)
                grid, cleared_rows = clear_rows(grid)
                score += 100 * cleared_rows
                current_tetromino = Tetromino(random.choice(list(TETROMINOES.keys())))
                if not valid_move(current_tetromino, grid, 0, 0):
                    running = False
            fall_time = 0

        draw_grid(screen, grid)
        draw_score(screen, score)
        # Draw current tetromino
        for y, row in enumerate(current_tetromino.blocks):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, COLORS[current_tetromino.color],
                                     ((current_tetromino.x + x) * GRID_SIZE, (current_tetromino.y + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(screen, (0, 0, 0),
                                     ((current_tetromino.x + x) * GRID_SIZE, (current_tetromino.y + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

        pygame.display.flip()

    print(f"Game Over! Your final score is {score}")
    font = pygame.font.SysFont('comicsans', 60)
    game_over_label = font.render('Game Over', 1, (255, 0, 0))
    screen.blit(game_over_label, (SCREEN_WIDTH // 2 - game_over_label.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_label.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(2000)
    pygame.quit()

if __name__ == "__main__":
    main()