"""
eight_puzzle.py - 8-Puzzle module (console)

Solver interface:
    result = solver.solve(state)
    -> {"steps": [...], "nodes": int, "time": float, "solved": bool}
"""
import random
import time
from collections import deque
from heapq import heappush, heappop

from utils import clear_screen, pause, header, color, ask_menu, GREEN, RED, GRAY, BOLD

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)  # 0 = blank


# ---------------------------------------------------------------- Puzzle --------------------------------
class EightPuzzle:
    """State = tuple of 9 numbers (row by row), 0 is the blank."""

    def __init__(self, state=GOAL):
        self.state = tuple(state)

    @staticmethod
    def is_goal(state):
        return state == GOAL

    @staticmethod
    def is_solvable(state):
        tiles = [t for t in state if t != 0]
        inversions = sum(1 for i in range(8) for j in range(i + 1, 8)
                         if tiles[i] > tiles[j])
        return inversions % 2 == 0

    @staticmethod
    def neighbors(state):
        """Return list of next states by sliding a tile into the blank."""
        b = state.index(0)
        r, c = divmod(b, 3)
        result = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                n = nr * 3 + nc
                s = list(state)
                s[b], s[n] = s[n], s[b]
                result.append(tuple(s))
        return result

    def move_tile(self, index):
        """Manual move: click on tile at `index`. Returns True if moved."""
        b = self.state.index(0)
        r1, c1 = divmod(index, 3)
        r2, c2 = divmod(b, 3)
        if abs(r1 - r2) + abs(c1 - c2) == 1:
            s = list(self.state)
            s[b], s[index] = s[index], s[b]
            self.state = tuple(s)
            return True
        return False

    def shuffle(self, moves=40, seed=None):
        """Shuffle by random legal moves from the goal (always solvable)."""
        rng = random.Random(seed)
        s, prev = GOAL, None
        for _ in range(moves):
            options = [n for n in self.neighbors(s) if n != prev]
            prev, s = s, rng.choice(options)
        self.state = s


# ---------------------------------------------------------------- Solvers
def manhattan(state):
    # manhattan sums the row and cols to reach the destination
    total = 0
    for i, t in enumerate(state):
        if t != 0:
            g = t - 1  # goal index of tile t
            total += abs(i // 3 - g // 3) + abs(i % 3 - g % 3)
    return total


def build_path(parent, state):
    path = []
    while state is not None:
        path.append(state)
        state = parent[state]
    return path[::-1]


class EightPuzzleSolver:
    def solve(self, start, algorithm="astar"):
        if not EightPuzzle.is_solvable(start):
            return {"steps": [], "nodes": 0, "time": 0.0, "solved": False}
        return self.bfs(start) if algorithm == "bfs" else self.astar(start)

    def bfs(self, start):
        t0 = time.perf_counter()
        parent = {start: None}
        queue = deque([start])
        nodes = 0
        while queue:
            s = queue.popleft()
            nodes += 1  # node expanded
            if s == GOAL:
                return {"steps": build_path(parent, s), "nodes": nodes,
                        "time": time.perf_counter() - t0, "solved": True}
            for n in EightPuzzle.neighbors(s):
                if n not in parent:
                    parent[n] = s
                    queue.append(n)
        return {"steps": [], "nodes": nodes,
                "time": time.perf_counter() - t0, "solved": False}

    def astar(self, start):
        t0 = time.perf_counter()
        parent = {start: None}
        g_cost = {start: 0}
        counter = 0  # tie-breaker so heap never compares states
        heap = [(manhattan(start), counter, start)]
        closed = set()
        nodes = 0
        while heap:
            _, _, s = heappop(heap)
            if s in closed:
                continue
            closed.add(s)
            nodes += 1  # node expanded
            if s == GOAL:
                return {"steps": build_path(parent, s), "nodes": nodes,
                        "time": time.perf_counter() - t0, "solved": True}
            for n in EightPuzzle.neighbors(s):
                new_g = g_cost[s] + 1
                if n not in g_cost or new_g < g_cost[n]:
                    g_cost[n] = new_g
                    parent[n] = s
                    counter += 1
                    heappush(heap, (new_g + manhattan(n), counter, n))
        return {"steps": [], "nodes": nodes,
                "time": time.perf_counter() - t0, "solved": False}


# ---------------------------------------------------------------- Console
def show(state):
    print("+---+---+---+")
    for r in range(3):
        row = state[r * 3:r * 3 + 3]
        print("|" + "|".join(f" {t if t else ' '} " for t in row) + "|")
        print("+---+---+---+")


def stats_text(name, res):
    return (f"{name.upper():<6} nodes={res['nodes']:<8} "
            f"time={res['time'] * 1000:.2f} ms  moves={len(res['steps']) - 1}")


def tile_moves(steps):
    """Convert a list of states into the tile numbers that were slid."""
    return [a[b.index(0)] for a, b in zip(steps, steps[1:])]


def a_star_review(start, user_moves, solved, solver):
    """After the game, A* inspects the board and reports the results."""
    res = solver.solve(start, "astar")
    best = tile_moves(res["steps"])
    print("\n=========== A* REVIEW ===========")
    print("Starting board was:")
    show(start)
    print(f"Your result      : {'solved' if solved else 'gave up'} "
          f"({len(user_moves)} moves)")
    print(f"A* optimal       : {len(best)} moves "
          f"(nodes={res['nodes']}, time={res['time'] * 1000:.2f} ms)")
    if solved:
        extra = len(user_moves) - len(best)
        if extra == 0:
            print("Verdict          : Perfect! You matched the optimal solution.")
        else:
            eff = 100 * len(best) / len(user_moves)
            print(f"Verdict          : {extra} extra moves, "
                  f"efficiency {eff:.0f}%")
    print("Your moves       :", " ".join(map(str, user_moves)) or "-")
    print("A* suggests      :", " ".join(map(str, best)) or "-")


def user_mode(puzzle, solver):
    """User plays first; A* reviews the game at the end."""
    start = puzzle.state
    user_moves = []
    message = ""
    solved = True
    while not EightPuzzle.is_goal(puzzle.state):
        clear_screen()                                   # clean screen every step
        header("8-PUZZLE  |  USER MODE")
        print("\n  Type the number of a tile next to the blank to move it.")
        print("  Type 'q' to give up. A* will review your game at the end.\n")
        show(puzzle.state)
        if message:
            print("\n  " + color(message, RED))
        message = ""
        cmd = input(f"\nMove {len(user_moves) + 1} > ").strip().lower()
        if cmd == "q":
            solved = False
            break
        if not cmd.isdigit() or not 1 <= int(cmd) <= 8:
            message = "Enter a tile number from 1 to 8."
            continue
        tile = int(cmd)
        if puzzle.move_tile(puzzle.state.index(tile)):
            user_moves.append(tile)
        else:
            message = "That tile is not next to the blank."
    clear_screen()
    header("8-PUZZLE  |  USER MODE")
    if solved:
        print()
        show(puzzle.state)
        print(color("\nYou solved it!", GREEN + BOLD))
    a_star_review(start, user_moves, solved, solver)
    puzzle.state = start  # reset so the same board can be replayed or compared
    pause()


def ai_mode(puzzle, solver):
    """AI solves the current board and shows the steps one by one."""
    algo = ask_menu("Algorithm", ["BFS", "A*"])
    name = "bfs" if algo == 1 else "astar"
    try:
        delay = float(input("Delay per step in seconds (e.g. 0.5) > ") or 0.5)
    except ValueError:
        delay = 0.5
    res = solver.solve(puzzle.state, name)
    if not res["solved"]:
        print("No solution found.")
        pause()
        return
    total = len(res["steps"]) - 1
    for i, s in enumerate(res["steps"]):
        clear_screen()                                   # clean screen every step
        header(f"8-PUZZLE  |  AI MODE  ({'BFS' if name == 'bfs' else 'A*'})")
        print(f"\n  Step {i} / {total}\n")
        show(s)
        time.sleep(delay)
    puzzle.state = res["steps"][-1]
    print()
    print(stats_text(name, res))
    pause()


def compare(puzzle, solver):
    clear_screen()
    header("8-PUZZLE  |  COMPARE BFS vs A*")
    print("\nBoard:")
    show(puzzle.state)
    print(f"\n{'Algo':<6}{'Nodes':>10}{'Time(ms)':>12}{'Moves':>8}")
    for name in ("bfs", "astar"):
        res = solver.solve(puzzle.state, name)
        if res["solved"]:
            print(f"{name.upper():<6}{res['nodes']:>10}"
                  f"{res['time'] * 1000:>12.2f}{len(res['steps']) - 1:>8}")
    pause()


def run():
    puzzle, solver = EightPuzzle(), EightPuzzleSolver()
    puzzle.shuffle()
    while True:
        clear_screen()
        header("8-PUZZLE")
        print("\nCurrent board:")
        show(puzzle.state)
        choice = ask_menu("Menu", [
            "Play yourself (user mode)",
            "Let the AI solve it",
            "Compare BFS vs A* on this board",
            "New shuffled board",
            "Back to main menu",
        ])
        if choice == 1:
            user_mode(puzzle, solver)
        elif choice == 2:
            ai_mode(puzzle, solver)
        elif choice == 3:
            compare(puzzle, solver)
        elif choice == 4:
            puzzle.shuffle()
        else:
            return


if __name__ == "__main__":
    run()
