import pygame
import random
import math

pygame.init()

#Change Speed of game
FPS = 90

# Initial score
score = 2

# Initialize screen settings
WIDTH, HEIGHT = 800, 800
ROWS = 4
COLS = 4

RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("Arial", 60, bold=True)
MOVE_VEL = 20

# Create the screen / window
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")


# Drawing starting screen with all the text
def draw_starting_screen(window):
    window.fill(BACKGROUND_COLOR)
    title_font = pygame.font.SysFont("Arial", 80, bold=True)
    button_font = pygame.font.SysFont("Arial", 50, bold=True)
    
    title_text = title_font.render("2048", 1, FONT_COLOR)
    easy_text = button_font.render("Easy", 1, FONT_COLOR)
    hard_text = button_font.render("Hard", 1, FONT_COLOR)
    
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    easy_rect = easy_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    hard_rect = hard_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    
    window.blit(title_text, title_rect)
    window.blit(easy_text, easy_rect)
    window.blit(hard_text, hard_rect)
    
    pygame.display.update()
    
    return easy_rect, hard_rect


# Display the selection of difficulty + detect user input
def select_difficulty():
    while True:
        easy_rect, hard_rect = draw_starting_screen(WINDOW)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_rect.collidepoint(event.pos):
                    return "easy"
                elif hard_rect.collidepoint(event.pos):
                    return "hard"


class Tile:

    # colors of tiles
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
        (232, 232, 88),
        (250, 0, 0),
        (214, 36, 13),
        (237, 14, 167),
        (196, 90, 219)
    ]


    # Initialize tiles
    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    # Set colors of the tiles
    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color
    
    # Draw the tiles
    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text,
            (
                self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                self.y + (RECT_HEIGHT / 2 - text.get_height() / 2),
            ),
        )

    # Set position of the tiles
    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    # Move the tiles
    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]

# Set up grid of the game
def draw_grid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)

# Display the tiles and score
def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window)

    score_text = FONT.render(f"Top Score: {score}", 1, FONT_COLOR)
    window.blit(score_text, (5, 5))

    pygame.display.update()

# Get a random position for the tiles to spawn
def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row}{col}" not in tiles:
            break

    return row, col

# All the movement of the tiles
def move_tiles(window, tiles, clock, direction, difficulty):
    global score
    updated = True
    blocks = set()

    if direction == "left":
        sort_func = lambda x: x.col
        reverse = False
        delta = (-MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col - 1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        )
        ceil = True
    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x
        )
        ceil = False
    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
        )
        ceil = True
    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
        )
        ceil = False

    # Check conditions and update max score and update tiles
    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif (
                tile.value == next_tile.value
                and tile not in blocks
                and next_tile not in blocks
            ):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    score = max(score, next_tile.value)
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        update_tiles(window, tiles, sorted_tiles)

    return end_move(tiles, difficulty, window, score)


# Detect if there are no moves left
def end_move(tiles, difficulty, window, score):
    if len(tiles) == 16:
        end_screen(window, score)
        return "lost"

    num_new_tiles = 1 if difficulty == "easy" else 2
    if len(tiles) == 15:
        num_new_tiles = 1

    # New tiles range of numberes
    for _ in range(num_new_tiles):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(random.choice([2, 4, 8, 16, 32]), row, col)
    
    return "continue"


# Update tiles
def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile

    draw(window, tiles)

# Generate a random tile everytime the user moves
def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)

    return tiles

# Draw and create end score, including all the text
def end_screen(window, score):
    window.fill(BACKGROUND_COLOR)
    end_font = pygame.font.SysFont("Arial", 80, bold=True)
    score_font = pygame.font.SysFont("Arial", 60, bold=True)
    again_font = pygame.font.SysFont("Arial", 60, bold=True)
    
    end_text = end_font.render("Game Over", 1, FONT_COLOR)
    score_text = score_font.render(f"Top Score: {score}", 1, FONT_COLOR)
    again_text = again_font.render("To play again, press R", 1, FONT_COLOR)
    
    end_rect = end_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    again_rect = again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0
                    return
            
        window.blit(end_text, end_rect)
        window.blit(score_text, score_rect)
        window.blit(again_text, again_rect)
    
        pygame.display.update()    


# Make the game runable and detect controls
def main(window):
    clock = pygame.time.Clock()
    
    while True:
        run = True

        difficulty = select_difficulty()
        if not difficulty:
            return

        tiles = generate_tiles()

        while run:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        game_state = move_tiles(window, tiles, clock, "left", difficulty)
                    if event.key == pygame.K_RIGHT:
                        game_state = move_tiles(window, tiles, clock, "right", difficulty)
                    if event.key == pygame.K_UP:
                        game_state = move_tiles(window, tiles, clock, "up", difficulty)
                    if event.key == pygame.K_DOWN:
                        game_state = move_tiles(window, tiles, clock, "down", difficulty)

                    if game_state == "lost":
                        end_screen(window, score)
                        run = False  # Stop the current game loop

                    if event.key == pygame.K_r:
                        run = False  # Stop the current game loop to restart

            draw(window, tiles)

    pygame.quit()




# Run the program
if __name__ == "__main__":
    main(WINDOW)