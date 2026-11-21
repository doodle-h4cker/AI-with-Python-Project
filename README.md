# 4 in a Row (Connect Four) – AI Search Algorithms

A course project for **AI with Python** by **Team Algo Minds**.

The project has two parts:

1. **`algorithm_comparison.py`** – a console program that generates a random mid-game board and compares three search algorithms on it: Minimax with Alpha-Beta pruning, Greedy Best-First Search and Breadth-First Search.
2. **`connect4_game.py`** – a playable fullscreen **Pygame** version where you (red) play against a Minimax + Alpha-Beta AI (yellow).

## Features

- 6 × 7 Connect Four board with horizontal, vertical and diagonal win detection
- Heuristic evaluation function: scores every 4-cell window (3-in-a-row, 2-in-a-row, blocking opponent threats) and prefers the centre column
- Move ordering from the centre outwards (`3, 2, 4, 1, 5, 0, 6`) to make pruning more effective
- Side-by-side comparison of nodes explored, branches pruned and execution time
- Pygame GUI with welcome screen, winning-line highlight and a Play Again button

## Algorithms

| Algorithm | Idea | Notes |
|---|---|---|
| Minimax + Alpha-Beta | Assumes the opponent plays optimally and prunes branches that cannot affect the result | Depth 4 in the comparison script, depth 5 in the game |
| Greedy Best-First | Always expands the state with the best heuristic score | Capped at 12,000 nodes |
| Breadth-First Search | Explores game states level by level | Capped at 12,000 nodes; no pruning, so it grows fastest |

## Getting started

**Requirements:** Python 3.8+ (the comparison script uses only the standard library; the game needs Pygame).

```bash
git clone https://github.com/<your-username>/four-in-a-row-ai.git
cd four-in-a-row-ai
pip install -r requirements.txt
```

### Run the algorithm comparison

```bash
python algorithm_comparison.py
```

A new random starting position is generated on every run, and each algorithm picks a move for the AI (Y) on that same board. The output ends with a performance table.

### Play the game

```bash
python connect4_game.py
```

| Control | Action |
|---|---|
| Click a column | Drop your disc |
| `Enter` | Start / play again |
| `Esc` | Quit |

## Project structure

```
four-in-a-row-ai/
├── algorithm_comparison.py   # Minimax vs Greedy vs BFS (console)
├── connect4_game.py          # Pygame game vs Minimax AI
├── requirements.txt
├── LICENSE
└── README.md
```

## Sample output

```
                  PERFORMANCE COMPARISON
Algorithm                                Nodes     Time (s)
-----------------------------------------------------------------
1. MINIMAX WITH ALPHA-BETA PRUNING         ...          ...
2. GREEDY BEST-FIRST SEARCH                ...          ...
3. BREADTH-FIRST SEARCH (BFS)              ...          ...
```
*(Replace with your own run, or add a screenshot at `docs/screenshot.png`.)*

## Team Algo Minds

- Member 1 – _name_
- Member 2 – _name_
- Member 3 – _name_

Course: AI with Python, IIIT Design and Manufacturing, Kancheepuram

## License

Released under the [MIT License](LICENSE).
