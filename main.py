import random
from collections import deque

import pygame
import sys

pygame.init()

# Constants
GRID_SIZE = 9
BOARD_SIZE = 721
BORDER_SIZE = 50
RIGHT_EMPTY_SPACE_SIZE = 200
WIDTH, HEIGHT = BOARD_SIZE + 2 * BORDER_SIZE + RIGHT_EMPTY_SPACE_SIZE, BOARD_SIZE + 2 * BORDER_SIZE
CELL_SIZE = BOARD_SIZE // (GRID_SIZE - 1)
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
pygame.display.set_caption('GO Board')

board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]  # 0: empty, 1: black, 2: white
current_player = 1  # 1: black to move, 2: white to move
move_counter = 1


def draw_board():
    screen.fill(BACKGROUND_COLOR)

    for i in range(GRID_SIZE - 1):
        pygame.draw.line(screen, GRID_COLOR, (BORDER_SIZE + i * CELL_SIZE, BORDER_SIZE),
                         (BORDER_SIZE + i * CELL_SIZE, BORDER_SIZE + BOARD_SIZE), 1)
        pygame.draw.line(screen, GRID_COLOR, (BORDER_SIZE, BORDER_SIZE + i * CELL_SIZE),
                         (BORDER_SIZE + BOARD_SIZE, BORDER_SIZE + i * CELL_SIZE), 1)

    pygame.draw.rect(screen, LINE_COLOR, (BORDER_SIZE, BORDER_SIZE, BOARD_SIZE, BOARD_SIZE), 1)

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] == 1:
                pygame.draw.circle(screen, STONE_BLACK, (BORDER_SIZE + col * CELL_SIZE, BORDER_SIZE + row * CELL_SIZE),
                                   CELL_SIZE // 2 - 5)
            elif board[row][col] == 2:
                pygame.draw.circle(screen, STONE_WHITE, (BORDER_SIZE + col * CELL_SIZE, BORDER_SIZE + row * CELL_SIZE),
                                   CELL_SIZE // 2 - 5)

    pass_button_rect = pygame.Rect(WIDTH - RIGHT_EMPTY_SPACE_SIZE + (RIGHT_EMPTY_SPACE_SIZE - PASS_BUTTON_WIDTH) // 2,
                                   (HEIGHT - PASS_BUTTON_HEIGHT) // 2,
                                   PASS_BUTTON_WIDTH, PASS_BUTTON_HEIGHT)
    pygame.draw.rect(screen, PASS_BUTTON_COLOR, pass_button_rect)
    font = pygame.font.Font(None, 36)
    text = font.render("PASS", True, PASS_BUTTON_TEXT_COLOR)
    text_rect = text.get_rect(center=pass_button_rect.center)
    screen.blit(text, text_rect)

    player_color = "Black" if move_counter % 2 == 1 else "White"
    font = pygame.font.Font(None, 24)
    move_text = font.render("Move: {}, {}".format(move_counter, player_color), True, TEXT_COLOR)
    move_text_rect = move_text.get_rect(x=WIDTH - RIGHT_EMPTY_SPACE_SIZE + 20, y=20)
    screen.blit(move_text, move_text_rect)


def show_endgame_dialog(winner):
    dialog_width = 300
    dialog_height = 150

    dialog_rect = pygame.Rect((WIDTH - dialog_width) // 2, (HEIGHT - dialog_height) // 2, dialog_width, dialog_height)
    pygame.draw.rect(screen, (255, 255, 255), dialog_rect)
    pygame.draw.rect(screen, (0, 0, 0), dialog_rect, 2)

    font = pygame.font.Font(None, 30)
    message_text = "{} wins".format(winner)
    message = font.render(message_text, True, (0, 0, 0))
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


def bfs_endgame(go_board, row, col, black_score, white_score, visited):
    visited[row][col] = True
    queue = deque([(row, col)])
    territory_size = 0
    controlled_by_black = controlled_by_white = False
    while queue:
        current_row, current_col = queue.popleft()
        territory_size += 1

        neighbors = [(current_row - 1, current_col), (current_row + 1, current_col), (current_row, current_col - 1),
                     (current_row, current_col + 1)]
        for neighbor_row, neighbor_col in neighbors:
            if 0 <= neighbor_row < GRID_SIZE and 0 <= neighbor_col < GRID_SIZE and not visited[neighbor_row][
                neighbor_col]:
                if go_board[neighbor_row][neighbor_col] == 0:
                    visited[neighbor_row][neighbor_col] = True
                    queue.append((neighbor_row, neighbor_col))
                elif go_board[neighbor_row][neighbor_col] == 1:
                    controlled_by_black = True
                else:
                    controlled_by_white = True

    if controlled_by_black and not controlled_by_white:
        black_score += territory_size
    elif not controlled_by_black and controlled_by_white:
        white_score += territory_size

    return [black_score, white_score]


def calculate_winner(go_board, black_captured, white_captured, komi):
    black_score = black_captured
    white_score = white_captured + komi

    visited = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if not visited[row][col] and go_board[row][col] == 0:
                [black_score, white_score] = bfs_endgame(go_board, row, col, black_score, white_score, visited)

    if black_score > white_score:
        return "Black"
    else:
        return "White"


def bfs_atari(go_board, row, col, visited, color):
    visited[row][col] = True
    queue = deque([(row, col)])
    group = []
    liberties = set()
    while queue:
        current_row, current_col = queue.popleft()
        group.append([current_row, current_col])

        neighbors = [(current_row - 1, current_col), (current_row + 1, current_col), (current_row, current_col - 1),
                     (current_row, current_col + 1)]
        for neighbor_row, neighbor_col in neighbors:
            if 0 <= neighbor_row < GRID_SIZE and 0 <= neighbor_col < GRID_SIZE and not visited[neighbor_row][neighbor_col]:
                if go_board[neighbor_row][neighbor_col] == color:
                    visited[neighbor_row][neighbor_col] = True
                    queue.append((neighbor_row, neighbor_col))
                elif go_board[neighbor_row][neighbor_col] == 0:
                    liberties.add((neighbor_row, neighbor_col))
    if len(liberties) == 1:
        return [group, liberties.pop()]
    else:
        return [[], ()]


def calculate_all_atari_groups(go_board, color):  # 1: black, 2: white
    atari = []
    visited = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if not visited[row][col] and go_board[row][col] == color:
                answer = bfs_atari(go_board, row, col, visited, color)
                if len(answer[0]) != 0:
                    atari.append(answer)
    return atari


def calculate_possible_moves(go_board, color):
    answer = []
    atari_list = calculate_all_atari_groups(go_board, 3 - color)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if go_board[row][col] == 0:
                is_atari = False
                for item in atari_list:
                    if item[1] == (row, col):
                        answer.append((row, col))
                        is_atari = True
                        break
                if not is_atari:
                    visited = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
                    queue = deque([(row, col)])
                    visited[row][col] = True
                    while queue:
                        current_row, current_col = queue.popleft()

                        neighbors = [(current_row - 1, current_col), (current_row + 1, current_col), (current_row, current_col - 1), (current_row, current_col + 1)]
                        for neighbor_row, neighbor_col in neighbors:
                            if 0 <= neighbor_row < GRID_SIZE and 0 <= neighbor_col < GRID_SIZE and not visited[neighbor_row][neighbor_col]:
                                if go_board[neighbor_row][neighbor_col] == color:
                                    visited[neighbor_row][neighbor_col] = True
                                    queue.append((neighbor_row, neighbor_col))
                                elif go_board[neighbor_row][neighbor_col] == 0:
                                    answer.append((row, col))
                                    queue.clear()
                                    break
    return answer


def play_against_human():
    global board, current_player, move_counter
    precedent_pass = False
    black_captured = white_captured = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = (mouse_x - BORDER_SIZE + CELL_SIZE // 2) // CELL_SIZE
                row = (mouse_y - BORDER_SIZE + CELL_SIZE // 2) // CELL_SIZE
                moves = calculate_possible_moves(board, current_player)

                if WIDTH - RIGHT_EMPTY_SPACE_SIZE < mouse_x < WIDTH and (HEIGHT - PASS_BUTTON_HEIGHT) // 2 < mouse_y < (HEIGHT + PASS_BUTTON_HEIGHT) // 2:
                    if precedent_pass:
                        result = show_endgame_dialog(calculate_winner(board, black_captured, white_captured, 6.5))
                        if result:
                            board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
                            current_player = 1
                            move_counter = 1
                            precedent_pass = False
                    else:
                        current_player = 3 - current_player
                        move_counter += 1
                        precedent_pass = True

                elif (row, col) in moves:
                    atari_list = calculate_all_atari_groups(board, 3 - current_player)
                    for item in atari_list:
                        if item[1] == (row, col):
                            for piece in item[0]:
                                board[piece[0]][piece[1]] = 0
                            if current_player == 1:
                                black_captured += len(item[0])
                            else:
                                white_captured += len(item[0])

                    board[row][col] = current_player
                    current_player = 3 - current_player
                    move_counter += 1
                    precedent_pass = False

                #print("Black atari: ", calculate_all_atari_groups(board, 1))
                #print("White atari: ", calculate_all_atari_groups(board, 2))
                #print("Black captured: ", black_captured)
                #print("White captured: ", white_captured)

        draw_board()
        pygame.display.flip()
        pygame.time.Clock().tick(60)


def play_against_computer():
    global board, current_player, move_counter
    precedent_pass = False
    black_captured = white_captured = 0
    computer_player = random.randint(1, 2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif current_player == computer_player:
                moves = calculate_possible_moves(board, computer_player)
                pass_random = random.randint(1, 10)
                if len(moves) == 0 or pass_random == 1:
                     if precedent_pass:
                        result = show_endgame_dialog(calculate_winner(board, black_captured, white_captured, 6.5))
                        if result:
                            board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
                            current_player = 1
                            move_counter = 1
                            precedent_pass = False
                     else:
                        current_player = 3 - current_player
                        move_counter += 1
                        precedent_pass = True
                else:
                    random_move = random.choice(moves)
                    row, col = random_move

                    atari_list = calculate_all_atari_groups(board, 3 - computer_player)
                    for item in atari_list:
                        if item[1] == (row, col):
                            for piece in item[0]:
                                board[piece[0]][piece[1]] = 0
                            white_captured += len(item[0])

                    board[row][col] = computer_player
                    current_player = 3 - current_player
                    move_counter += 1
                    precedent_pass = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = (mouse_x - BORDER_SIZE + CELL_SIZE // 2) // CELL_SIZE
                row = (mouse_y - BORDER_SIZE + CELL_SIZE // 2) // CELL_SIZE
                moves = calculate_possible_moves(board, current_player)

                if WIDTH - RIGHT_EMPTY_SPACE_SIZE < mouse_x < WIDTH and (HEIGHT - PASS_BUTTON_HEIGHT) // 2 < mouse_y < (
                            HEIGHT + PASS_BUTTON_HEIGHT) // 2:
                    if precedent_pass:
                        result = show_endgame_dialog(calculate_winner(board, black_captured, white_captured, 6.5))
                        if result:
                            board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
                            current_player = 1
                            move_counter = 1
                            precedent_pass = False
                    else:
                        current_player = 3 - current_player
                        move_counter += 1
                        precedent_pass = True

                elif (row, col) in moves:
                    atari_list = calculate_all_atari_groups(board, 3 - current_player)
                    for item in atari_list:
                        if item[1] == (row, col):
                            for piece in item[0]:
                                board[piece[0]][piece[1]] = 0
                            if current_player == 1:
                                black_captured += len(item[0])
                            else:
                                white_captured += len(item[0])

                    board[row][col] = current_player
                    current_player = 3 - current_player
                    move_counter += 1
                    precedent_pass = False

        draw_board()
        pygame.display.flip()
        pygame.time.Clock().tick(60)



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrong number of arguments!")
        sys.exit(1)

    opponent_type = sys.argv[1]

    if opponent_type == "human":
        play_against_human()
    elif opponent_type == "computer":
        play_against_computer()
    else:
        print("Invalid opponent type. Please use 'computer' or 'human'!")
