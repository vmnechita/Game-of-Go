import pygame
import sys

pygame.init()

# Constants
Board_Size = 721
Border_Size = 50
Right_Empty_Space_Size = 200
WIDTH, HEIGHT = Board_Size + 2 * Border_Size + Right_Empty_Space_Size, Board_Size + 2 * Border_Size
GRID_SIZE = 13
CELL_SIZE = Board_Size // (GRID_SIZE - 1)
PASS_BUTTON_WIDTH = 100
PASS_BUTTON_HEIGHT = 40
PASS_BUTTON_COLOR = (200, 200, 200)
PASS_BUTTON_TEXT_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)

BACKGROUND_COLOR = (240, 214, 159)
GRID_COLOR = (0, 0, 0)
LINE_COLOR = (0, 0, 0)
STONE_BLACK = (0, 0, 0)
STONE_WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Go Board')

board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]  # 0: empty, 1: black, 2: white
current_player = 1  # Start with black
move_counter = 1  # Initialize move counter

def draw_board():
    screen.fill(BACKGROUND_COLOR)

    for i in range(GRID_SIZE - 1):
        pygame.draw.line(screen, GRID_COLOR, (Border_Size + i * CELL_SIZE, Border_Size), (Border_Size + i * CELL_SIZE, Border_Size + Board_Size), 1)
        pygame.draw.line(screen, GRID_COLOR, (Border_Size, Border_Size + i * CELL_SIZE), (Border_Size + Board_Size, Border_Size + i * CELL_SIZE), 1)

    pygame.draw.rect(screen, LINE_COLOR, (Border_Size, Border_Size, Board_Size, Board_Size), 1)

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] == 1:
                pygame.draw.circle(screen, STONE_BLACK, (Border_Size + col * CELL_SIZE, Border_Size + row * CELL_SIZE), CELL_SIZE // 2 - 5)
            elif board[row][col] == 2:
                pygame.draw.circle(screen, STONE_WHITE, (Border_Size + col * CELL_SIZE, Border_Size + row * CELL_SIZE), CELL_SIZE // 2 - 5)

    # Draw PASS button
    pass_button_rect = pygame.Rect(WIDTH - Right_Empty_Space_Size + (Right_Empty_Space_Size - PASS_BUTTON_WIDTH) // 2,
                                   (HEIGHT - PASS_BUTTON_HEIGHT) // 2,
                                   PASS_BUTTON_WIDTH, PASS_BUTTON_HEIGHT)
    pygame.draw.rect(screen, PASS_BUTTON_COLOR, pass_button_rect)
    font = pygame.font.Font(None, 36)
    text = font.render("PASS", True, PASS_BUTTON_TEXT_COLOR)
    text_rect = text.get_rect(center=pass_button_rect.center)
    screen.blit(text, text_rect)

    # Draw move counter
    font = pygame.font.Font(None, 24)
    move_text = font.render("Move: {}".format(move_counter), True, TEXT_COLOR)
    move_text_rect = move_text.get_rect(x=WIDTH - Right_Empty_Space_Size + 20, y=20)
    screen.blit(move_text, move_text_rect)

def show_confirmation_dialog():
    dialog_width = 300
    dialog_height = 150

    dialog_rect = pygame.Rect((WIDTH - dialog_width) // 2, (HEIGHT - dialog_height) // 2, dialog_width, dialog_height)
    pygame.draw.rect(screen, (255, 255, 255), dialog_rect)
    pygame.draw.rect(screen, (0, 0, 0), dialog_rect, 2)

    font = pygame.font.Font(None, 30)
    message = font.render("Two consecutive PASS moves.", True, (0, 0, 0))
    message_rect = message.get_rect(center=(dialog_rect.centerx, dialog_rect.centery - 20))
    screen.blit(message, message_rect)

    button_rect = pygame.Rect((WIDTH - dialog_width) // 2 + 50, (HEIGHT - dialog_height) // 2 + 80, 200, 50)
    pygame.draw.rect(screen, (200, 200, 200), button_rect)
    button_text = font.render("Restart Game", True, (0, 0, 0))
    button_text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                return True  # Restart the game

precedent_pass = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            col = (mouse_x - Border_Size + CELL_SIZE // 2) // CELL_SIZE
            row = (mouse_y - Border_Size + CELL_SIZE // 2) // CELL_SIZE

            if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and board[row][col] == 0:
                board[row][col] = current_player
                current_player = 3 - current_player
                move_counter += 1
                precedent_pass = False
            elif WIDTH - Right_Empty_Space_Size < mouse_x < WIDTH and (HEIGHT - PASS_BUTTON_HEIGHT) // 2 < mouse_y < (HEIGHT + PASS_BUTTON_HEIGHT) // 2:
                if precedent_pass:
                    result = show_confirmation_dialog()
                    if result:
                        board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
                        current_player = 1
                        move_counter = 1
                        precedent_pass = False
                else:
                    move_counter += 1
                    precedent_pass = True

    draw_board()
    pygame.display.flip()
    pygame.time.Clock().tick(60)
