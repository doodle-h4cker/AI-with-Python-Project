import math
import sys
import pygame

# Game settings
ROWS = 6
COLS = 7
AI_DEPTH = 5

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
CELL_W = 150
CELL_H = 72
GAP = 8
BOARD_X = 0
BOARD_Y = 0
BOARD_WIDTH = 0
BOARD_HEIGHT = 0

EMPTY = 0
PLAYER = 1
COMPUTER = 2

BACKGROUND = (0, 0, 0)
BLUE = (37, 101, 165)
RED = (235, 55, 55)
YELLOW = (255, 195, 35)
WHITE = (245, 245, 245)
DARK = (245, 245, 245)
GREY = (185, 185, 185)
GREEN = (0, 105, 48)
HOLE = (232, 236, 241)

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("4 in a Row")
clock = pygame.time.Clock()

WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
CELL_W = int(min(WINDOW_WIDTH * 0.115, WINDOW_HEIGHT * 0.14))
CELL_H = int(min(WINDOW_HEIGHT * 0.075, WINDOW_WIDTH * 0.06))
GAP = max(5, int(min(WINDOW_WIDTH, WINDOW_HEIGHT) * 0.009))
BOARD_WIDTH = COLS * (CELL_W + GAP) - GAP
BOARD_HEIGHT = ROWS * (CELL_H + GAP) - GAP
BOARD_X = (WINDOW_WIDTH - BOARD_WIDTH) // 2
BOARD_Y = int(WINDOW_HEIGHT * 0.36)

TITLE_FONT = pygame.font.SysFont("arial", max(34, int(WINDOW_HEIGHT * 0.055)), bold=True)
FONT = pygame.font.SysFont("arial", max(21, int(WINDOW_HEIGHT * 0.027)), bold=True)
SMALL_FONT = pygame.font.SysFont("arial", max(15, int(WINDOW_HEIGHT * 0.019)))
STATUS_FONT = pygame.font.SysFont("arial", max(22, int(WINDOW_HEIGHT * 0.03)), bold=True)
WELCOME_FONT = pygame.font.SysFont("arial", max(28, int(WINDOW_HEIGHT * 0.04)), bold=True)
BUTTON_FONT = pygame.font.SysFont("arial", max(17, int(WINDOW_HEIGHT * 0.023)), bold=True)


# ------------------------- GAME FUNCTIONS -------------------------

def create_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


def get_valid_moves(board):
    # Check the middle columns first.
    order = [3, 2, 4, 1, 5, 0, 6]
    return [col for col in order if board[0][col] == EMPTY]


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def get_next_open_row(board, col):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row
    return None


def get_winning_positions(board, piece):
    # Return the four cells that form a winning line.
    # Horizontal
    for row in range(ROWS):
        for col in range(COLS - 3):
            positions = [(row, col + i) for i in range(4)]
            if all(board[r][c] == piece for r, c in positions):
                return positions

    # Vertical
    for row in range(ROWS - 3):
        for col in range(COLS):
            positions = [(row + i, col) for i in range(4)]
            if all(board[r][c] == piece for r, c in positions):
                return positions

    # Diagonal: bottom-left to top-right
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            positions = [(row - i, col + i) for i in range(4)]
            if all(board[r][c] == piece for r, c in positions):
                return positions

    # Diagonal: top-left to bottom-right
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            positions = [(row + i, col + i) for i in range(4)]
            if all(board[r][c] == piece for r, c in positions):
                return positions

    return []


def winning_move(board, piece):
    return bool(get_winning_positions(board, piece))


def is_draw(board):
    return all(board[0][col] != EMPTY for col in range(COLS))


def evaluate_window(window, piece):
    opponent = PLAYER if piece == COMPUTER else COMPUTER
    score = 0

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 8
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 3

    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 10

    return score


def score_position(board, piece):
    score = 0

    # Prefer the centre column.
    centre = [board[row][COLS // 2] for row in range(ROWS)]
    score += centre.count(piece) * 6

    # Check horizontal groups of four.
    for row in range(ROWS):
        for col in range(COLS - 3):
            window = board[row][col:col + 4]
            score += evaluate_window(window, piece)

    # Check vertical groups of four.
    for row in range(ROWS - 3):
        for col in range(COLS):
            window = [board[row + i][col] for i in range(4)]
            score += evaluate_window(window, piece)

    # Check diagonal groups of four.
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            window = [board[row + i][col + i] for i in range(4)]
            score += evaluate_window(window, piece)

    for row in range(3, ROWS):
        for col in range(COLS - 3):
            window = [board[row - i][col + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score


def minimax(board, depth, alpha, beta, maximizing_player):
    valid_moves = get_valid_moves(board)

    if winning_move(board, COMPUTER):
        return None, 1_000_000 + depth
    if winning_move(board, PLAYER):
        return None, -1_000_000 - depth
    if depth == 0 or not valid_moves:
        return None, score_position(board, COMPUTER)

    if maximizing_player:
        best_score = -math.inf
        best_col = valid_moves[0]

        for col in valid_moves:
            row = get_next_open_row(board, col)
            child = [r[:] for r in board]
            drop_piece(child, row, col, COMPUTER)

            _, score = minimax(child, depth - 1, alpha, beta, False)

            if score > best_score:
                best_score = score
                best_col = col

            alpha = max(alpha, best_score)
            if alpha >= beta:
                break

        return best_col, best_score

    best_score = math.inf
    best_col = valid_moves[0]

    for col in valid_moves:
        row = get_next_open_row(board, col)
        child = [r[:] for r in board]
        drop_piece(child, row, col, PLAYER)

        _, score = minimax(child, depth - 1, alpha, beta, True)

        if score < best_score:
            best_score = score
            best_col = col

        beta = min(beta, best_score)
        if alpha >= beta:
            break

    return best_col, best_score


def get_computer_move(board):
    col, _ = minimax(board, AI_DEPTH, -math.inf, math.inf, True)
    return col


# --------------------------- DRAWING ---------------------------

def draw_text(text, font, colour, x, y, centre=True):
    image = font.render(text, True, colour)
    rect = image.get_rect()
    if centre:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))
    screen.blit(image, rect)


def draw_button(rect, text):
    pygame.draw.rect(screen, GREEN, rect, border_radius=16)
    pygame.draw.rect(screen, (0, 180, 80), rect, 2, border_radius=16)
    draw_text(text, BUTTON_FONT, WHITE, rect.centerx, rect.centery)


def draw_header():
    draw_text("4 IN A ROW", TITLE_FONT, WHITE, WINDOW_WIDTH // 2,
              int(WINDOW_HEIGHT * 0.09))


def draw_legend(y):
    gap = int(WINDOW_WIDTH * 0.045)
    center = WINDOW_WIDTH // 2
    pygame.draw.circle(screen, RED, (center - gap, y), max(9, CELL_H // 5))
    draw_text("Player", FONT, WHITE, center - gap + 28, y)
    pygame.draw.circle(screen, YELLOW, (center + gap, y), max(9, CELL_H // 5))
    draw_text("Computer", FONT, WHITE, center + gap + 52, y)


def draw_board(board, status):
    screen.fill(BACKGROUND)
    draw_header()
    draw_legend(int(WINDOW_HEIGHT * 0.23))

    label_y = BOARD_Y - max(22, int(WINDOW_HEIGHT * 0.025))
    for col in range(COLS):
        x = BOARD_X + col * (CELL_W + GAP) + CELL_W // 2
        draw_text(f"ROW {col + 1}", SMALL_FONT, WHITE, x, label_y)

    for row in range(ROWS):
        for col in range(COLS):
            x = BOARD_X + col * (CELL_W + GAP)
            y = BOARD_Y + row * (CELL_H + GAP)
            pygame.draw.rect(screen, BLUE, (x, y, CELL_W, CELL_H), border_radius=10)
            cx = x + CELL_W // 2
            cy = y + CELL_H // 2
            piece = board[row][col]
            colour = RED if piece == PLAYER else YELLOW if piece == COMPUTER else HOLE
            pygame.draw.circle(screen, colour, (cx, cy), max(13, min(CELL_W, CELL_H) // 3))

    draw_text(status, STATUS_FONT, WHITE, WINDOW_WIDTH // 2,
              min(WINDOW_HEIGHT - 45, BOARD_Y + BOARD_HEIGHT + int(WINDOW_HEIGHT * 0.07)))
    pygame.display.flip()


def draw_welcome():
    screen.fill(BACKGROUND)
    draw_header()

    draw_text("Welcome to 4 in a Row!", WELCOME_FONT, WHITE,
              WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.34))
    draw_text("Challenge the computer and connect four discs to win.",
              FONT, WHITE, WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.42))

    button = pygame.Rect(0, 0, int(WINDOW_WIDTH * 0.24), int(WINDOW_HEIGHT * 0.075))
    button.center = (WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.55))
    draw_button(button, "TAP ENTER TO PLAY")

    draw_legend(int(WINDOW_HEIGHT * 0.70))
    pygame.display.flip()
    return button


def draw_end_screen(message, colour, board, winning_positions):
    # Keep the final board visible so the player can inspect the winning line.
    draw_board(board, message)

    # Highlight the four connected discs with bright outlines.
    for row, col in winning_positions:
        cx = BOARD_X + col * (CELL_W + GAP) + CELL_W // 2
        cy = BOARD_Y + row * (CELL_H + GAP) + CELL_H // 2
        radius = max(13, min(CELL_W, CELL_H) // 3)
        pygame.draw.circle(screen, WHITE, (cx, cy), radius + 7, max(3, radius // 5))
        pygame.draw.circle(screen, GREEN, (cx, cy), radius + 11, max(2, radius // 9))

    # Show the result and restart button below the board.
    banner = pygame.Rect(0, 0, int(WINDOW_WIDTH * 0.34), int(WINDOW_HEIGHT * 0.06))
    banner.center = (WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.90))
    pygame.draw.rect(screen, GREEN, banner, border_radius=14)
    draw_text(message, FONT, WHITE, banner.centerx, banner.centery)

    restart = pygame.Rect(0, 0, int(WINDOW_WIDTH * 0.18), int(WINDOW_HEIGHT * 0.06))
    restart.center = (WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.975))
    restart.bottom = WINDOW_HEIGHT - 6
    draw_button(restart, "PLAY AGAIN")
    pygame.display.flip()
    return restart


# --------------------------- MAIN PROGRAM ---------------------------

def main():
    board = create_board()
    game_state = "welcome"
    current_turn = PLAYER
    message = ""
    message_colour = WHITE
    winning_positions = []
    computer_waiting = False
    computer_move_time = 0
    start_button = pygame.Rect(0, 0, 1, 1)
    restart_button = pygame.Rect(0, 0, 1, 1)

    running = True
    while running:
        clock.tick(60)

        if game_state == "welcome":
            start_button = draw_welcome()
        elif game_state == "playing":
            status = "Your turn - click a column" if current_turn == PLAYER else "Computer is thinking..."
            draw_board(board, status)
        elif game_state == "finished":
            restart_button = draw_end_screen(message, message_colour, board, winning_positions)

        if game_state == "playing" and computer_waiting:
            if pygame.time.get_ticks() >= computer_move_time:
                col = get_computer_move(board)
                if col is not None:
                    row = get_next_open_row(board, col)
                    if row is not None:
                        drop_piece(board, row, col, COMPUTER)

                computer_waiting = False
                winning_positions = get_winning_positions(board, COMPUTER)
                if winning_positions:
                    game_state = "finished"
                    message = "COMPUTER WINS!"
                    message_colour = YELLOW
                elif is_draw(board):
                    game_state = "finished"
                    message = "IT'S A DRAW!"
                    message_colour = WHITE
                else:
                    current_turn = PLAYER

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN and game_state in ("welcome", "finished"):
                    board = create_board()
                    winning_positions = []
                    game_state = "playing"
                    current_turn = PLAYER
                    computer_waiting = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos

                if game_state == "welcome" and start_button.collidepoint(event.pos):
                    board = create_board()
                    winning_positions = []
                    game_state = "playing"
                    current_turn = PLAYER
                    computer_waiting = False

                elif game_state == "finished" and restart_button.collidepoint(event.pos):
                    board = create_board()
                    winning_positions = []
                    game_state = "playing"
                    current_turn = PLAYER
                    computer_waiting = False

                elif game_state == "playing" and current_turn == PLAYER:
                    if BOARD_X <= mouse_x < BOARD_X + BOARD_WIDTH:
                        col = (mouse_x - BOARD_X) // (CELL_W + GAP)
                        if col < COLS:
                            row = get_next_open_row(board, col)
                            if row is not None:
                                drop_piece(board, row, col, PLAYER)
                                winning_positions = get_winning_positions(board, PLAYER)
                                if winning_positions:
                                    game_state = "finished"
                                    message = "YOU WIN!"
                                    message_colour = RED
                                elif is_draw(board):
                                    game_state = "finished"
                                    message = "IT'S A DRAW!"
                                    message_colour = WHITE
                                else:
                                    current_turn = COMPUTER
                                    computer_waiting = True
                                    computer_move_time = pygame.time.get_ticks() + 350

    pygame.quit()
    sys.exit()

    
if __name__ == "__main__":
    main()
