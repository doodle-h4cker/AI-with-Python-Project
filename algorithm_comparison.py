
import random
import time
import math
import copy
import heapq
from collections import deque

ROWS = 6
COLS = 7
EMPTY = "."
PLAYER = "R"
AI = "Y"

DEPTH = 4
NODE_LIMIT = 12000


# ---------------- BOARD FUNCTIONS ----------------

def create_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


def display_board(board):
    print("\n       1   2   3   4   5   6   7")
    print("     +" + "---+" * COLS)

    for r in range(ROWS):
        print(f" R{r+1}  | " + " | ".join(board[r]) + " |")
        print("     +" + "---+" * COLS)

    print("\nR = Player | Y = Computer | . = Empty")


def valid_moves(board):
    order = [3, 2, 4, 1, 5, 0, 6]
    return [c for c in order if board[0][c] == EMPTY]


def next_row(board, col):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return None


def make_move(board, col, piece):
    r = next_row(board, col)
    if r is not None:
        board[r][col] = piece
        return True
    return False


def winner(board, piece):

    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c+i] == piece for i in range(4)):
                return True

    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r+i][c] == piece for i in range(4)):
                return True

    # Diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True

    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True

    return False


def terminal(board):
    return winner(board, AI) or winner(board, PLAYER) or not valid_moves(board)


def opponent(piece):
    return PLAYER if piece == AI else AI


# ---------------- HEURISTIC FUNCTION ----------------

def evaluate_window(window, piece):
    other = opponent(piece)
    score = 0

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 8
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 3

    if window.count(other) == 3 and window.count(EMPTY) == 1:
        score -= 10

    return score


def evaluate(board):

    if winner(board, AI):
        return 100000

    if winner(board, PLAYER):
        return -100000

    score = 0

    # Prefer the centre column
    centre = [board[r][COLS // 2] for r in range(ROWS)]
    score += centre.count(AI) * 6
    score -= centre.count(PLAYER) * 6

    # Horizontal windows
    for r in range(ROWS):
        for c in range(COLS - 3):
            window = board[r][c:c+4]
            score += evaluate_window(window, AI)
            score -= evaluate_window(window, PLAYER)

    # Vertical windows
    for r in range(ROWS - 3):
        for c in range(COLS):
            window = [board[r+i][c] for i in range(4)]
            score += evaluate_window(window, AI)
            score -= evaluate_window(window, PLAYER)

    # Diagonal windows
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, AI)
            score -= evaluate_window(window, PLAYER)

    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r-i][c+i] for i in range(4)]
            score += evaluate_window(window, AI)
            score -= evaluate_window(window, PLAYER)

    return score


# ---------------- 1. MINIMAX WITH ALPHA-BETA ----------------

def minimax(board, depth, alpha, beta, maximizing, stats):

    stats["nodes"] += 1
    moves = valid_moves(board)

    if depth == 0 or terminal(board):
        return None, evaluate(board)

    if maximizing:

        best_score = -math.inf
        best_col = moves[0]

        for col in moves:
            child = copy.deepcopy(board)
            make_move(child, col, AI)

            _, score = minimax(
                child, depth-1, alpha, beta, False, stats
            )

            if score > best_score:
                best_score = score
                best_col = col

            alpha = max(alpha, best_score)

            if alpha >= beta:
                stats["pruned"] += len(moves) - moves.index(col) - 1
                break

        return best_col, best_score

    else:

        best_score = math.inf
        best_col = moves[0]

        for col in moves:
            child = copy.deepcopy(board)
            make_move(child, col, PLAYER)

            _, score = minimax(
                child, depth-1, alpha, beta, True, stats
            )

            if score < best_score:
                best_score = score
                best_col = col

            beta = min(beta, best_score)

            if alpha >= beta:
                stats["pruned"] += len(moves) - moves.index(col) - 1
                break

        return best_col, best_score


def run_minimax(board):

    stats = {"nodes": 0, "pruned": 0}
    start = time.perf_counter()

    col, score = minimax(
        board, DEPTH, -math.inf, math.inf, True, stats
    )

    elapsed = time.perf_counter() - start

    return col, score, stats, elapsed


# ---------------- 2. GREEDY BEST-FIRST SEARCH ----------------

def run_greedy(board):

    start = time.perf_counter()
    stats = {"nodes": 0}

    queue = []
    counter = 0
    best_col = None
    best_score = -math.inf

    # Add all possible first moves
    for col in valid_moves(board):

        child = copy.deepcopy(board)
        make_move(child, col, AI)

        score = evaluate(child)

        heapq.heappush(
            queue, (-score, counter, child, 1, PLAYER, col)
        )
        counter += 1

    while queue and stats["nodes"] < NODE_LIMIT:

        _, _, state, depth, turn, first_move = heapq.heappop(queue)

        stats["nodes"] += 1
        score = evaluate(state)

        if score > best_score:
            best_score = score
            best_col = first_move

        if winner(state, AI):
            best_col = first_move
            best_score = score
            break

        if depth >= DEPTH or terminal(state):
            continue

        for col in valid_moves(state):

            child = copy.deepcopy(state)
            make_move(child, col, turn)

            child_score = evaluate(child)

            heapq.heappush(
                queue,
                (-child_score, counter, child,
                 depth+1, opponent(turn), first_move)
            )
            counter += 1

    elapsed = time.perf_counter() - start

    return best_col, best_score, stats, elapsed


# ---------------- 3. BREADTH-FIRST SEARCH ----------------

def run_bfs(board):

    start = time.perf_counter()
    stats = {"nodes": 0}

    queue = deque()
    best_col = None
    best_score = -math.inf

    # Add all possible first moves
    for col in valid_moves(board):

        child = copy.deepcopy(board)
        make_move(child, col, AI)

        queue.append((child, PLAYER, 1, col))

    while queue and stats["nodes"] < NODE_LIMIT:

        state, turn, depth, first_move = queue.popleft()

        stats["nodes"] += 1
        score = evaluate(state)

        if score > best_score:
            best_score = score
            best_col = first_move

        if winner(state, AI):
            best_col = first_move
            best_score = score
            break

        if depth >= DEPTH or terminal(state):
            continue

        for col in valid_moves(state):

            child = copy.deepcopy(state)
            make_move(child, col, turn)

            queue.append(
                (child, opponent(turn), depth+1, first_move)
            )

    elapsed = time.perf_counter() - start

    return best_col, best_score, stats, elapsed


# ---------------- RANDOM BOARD GENERATION ----------------

def random_position():

    while True:

        board = create_board()
        total_moves = random.choice([7, 9, 11, 13])

        for move in range(total_moves):

            piece = PLAYER if move % 2 == 0 else AI
            options = valid_moves(board)
            random.shuffle(options)

            safe_moves = []

            for col in options:

                test = copy.deepcopy(board)
                make_move(test, col, piece)

                if not winner(test, piece):
                    safe_moves.append(col)

            if not safe_moves:
                break

            make_move(board, random.choice(safe_moves), piece)

        if not winner(board, PLAYER) and not winner(board, AI):
            return board


# ---------------- RESULTS ----------------

def show_result(name, result):

    col, score, stats, elapsed = result

    print("\n" + name)
    print("-" * 45)

    print("Selected Column :", col + 1)
    print("Evaluation Score:", score)
    print("Nodes Explored  :", stats["nodes"])

    if "pruned" in stats:
        print("Branches Pruned :", stats["pruned"])

    print("Execution Time  :", round(elapsed, 6), "seconds")

    test_board = copy.deepcopy(board)
    make_move(test_board, col, AI)

    print("\nBoard after selected move:")
    display_board(test_board)


# ---------------- MAIN PROGRAM ----------------

print("\n" + "=" * 55)
print("             4 IN A ROW - AI SIMULATION")
print("=" * 55)

print("\nGenerating a random game position...")

board = random_position()

print("\nInitial Board:")
display_board(board)

algorithms = [
    ("1. MINIMAX WITH ALPHA-BETA PRUNING", run_minimax),
    ("2. GREEDY BEST-FIRST SEARCH", run_greedy),
    ("3. BREADTH-FIRST SEARCH (BFS)", run_bfs)
]

results = []

for name, algorithm in algorithms:

    print("\nRunning", name, "...")

    result = algorithm(board)
    results.append((name, result))

    show_result(name, result)


# ---------------- PERFORMANCE COMPARISON ----------------

print("\n" + "=" * 65)
print("                  PERFORMANCE COMPARISON")
print("=" * 65)

print(f"{'Algorithm':37} {'Nodes':>8} {'Time (s)':>12}")
print("-" * 65)

for name, result in results:

    _, _, stats, elapsed = result

    print(
        f"{name:37} "
        f"{stats['nodes']:>8} "
        f"{elapsed:>12.6f}"
    )

print("\nALGORITHM SUMMARY")
print("-" * 65)

print("Minimax + Alpha-Beta : Searches opponent responses and prunes branches.")
print("Greedy Best-First    : Expands states with the best heuristic score.")
print("BFS                  : Explores game states level by level.")

print("\nNote: All algorithms use the same initial board.")
print("The random starting position changes each time the program runs.")
print("=" * 65)
