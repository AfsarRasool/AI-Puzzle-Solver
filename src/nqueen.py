"""
nqueen.py - everything about N-Queens in ONE file

  1. Hill Climbing   (core algorithm + step-by-step visualizer)
  2. Backtracking    (core algorithm, used for hints and for comparison)
  3. Play with hints (console game)
  4. Comparison      (Hill Climbing on random boards vs Backtracking on empty board)

State representation: state[row] = column of the queen in that row.
"""
import random
import time

from utils import (clear_screen, pause, header, ask_int, ask_menu, get_key, bar,
                   color, RESET, BOLD, CYAN, GREEN, RED, YELLOW, GRAY)


# =====================================================================
# 1. HILL CLIMBING  (your original logic)
# =====================================================================
def get_neighbour(curr_state):
    """All states reachable by moving ONE queen to another column."""
    neighbors = []
    n = len(curr_state)
    for i in range(n):
        for j in range(n):
            if j != curr_state[i]:
                new_neighbor = curr_state.copy()
                new_neighbor[i] = j
                neighbors.append(new_neighbor)
    return neighbors


def calculate_conflict(state):
    """Number of attacking queen pairs (0 = solution)."""
    count = 0
    n = len(state)
    for i in range(n):
        for j in range(i + 1, n):
            if state[i] == state[j] or abs(state[i] - state[j]) == abs(i - j):
                count += 1
    return count


def build_history(n=4, max_restarts=100):
    """Hill climbing with random restarts. Every step is saved for the visualizer."""
    history = []
    for restart in range(1, max_restarts + 1):
        curr_state = random.sample(range(n), n)
        curr_conflicts = calculate_conflict(curr_state)
        history.append({
            "action": "restart", "restart": restart, "iteration": 0,
            "current_state": curr_state.copy(),
            "current_conflicts": curr_conflicts, "neighbors": []
        })
        if curr_conflicts == 0:
            history[-1]["action"] = "solution"
            return history
        iteration = 0
        while True:
            iteration += 1
            neighbors = get_neighbour(curr_state)
            neighbor_info = [{"state": nb.copy(), "conflicts": calculate_conflict(nb)}
                             for nb in neighbors]
            best = min(neighbor_info, key=lambda x: x["conflicts"])
            best_neighbor = best["state"]
            best_conflicts = best["conflicts"]
            step = {
                "action": None, "restart": restart, "iteration": iteration,
                "current_state": curr_state.copy(),
                "current_conflicts": curr_conflicts,
                "neighbors": neighbor_info,
                "best_neighbor": best_neighbor.copy(),
                "best_conflicts": best_conflicts
            }
            if best_conflicts >= curr_conflicts:
                step["action"] = "local_minimum"
                history.append(step)
                break
            step["action"] = "move"
            history.append(step)
            curr_state = best_neighbor.copy()
            curr_conflicts = best_conflicts
            if curr_conflicts == 0:
                history.append({
                    "action": "solution", "restart": restart, "iteration": iteration,
                    "current_state": curr_state.copy(),
                    "current_conflicts": 0, "neighbors": []
                })
                return history
    history.append({
        "action": "limit_reached", "restart": max_restarts, "iteration": 0,
        "current_state": [], "current_conflicts": None, "neighbors": []
    })
    return history


def hill_climbing_fast(n, max_restarts=100):
    """
    Same algorithm as build_history (random restarts, steepest-ascent) but it
    does NOT store neighbours/steps - used by the comparison. Only statistics
    are collected.
    """
    t0 = time.perf_counter()
    stats = {"restarts": 0, "iterations": 0, "evaluated": 0, "local_minima": 0}
    initial = None
    state, conflicts = [], None
    solved = False
    for _ in range(max_restarts):
        stats["restarts"] += 1
        state = random.sample(range(n), n)
        conflicts = calculate_conflict(state)
        if initial is None:
            initial = (state.copy(), conflicts)
        while conflicts > 0:
            stats["iterations"] += 1
            neighbors = get_neighbour(state)
            stats["evaluated"] += len(neighbors)
            best_state, best_c = None, None
            for nb in neighbors:
                c = calculate_conflict(nb)
                if best_c is None or c < best_c:
                    best_state, best_c = nb, c
            if best_c >= conflicts:
                stats["local_minima"] += 1
                break
            state, conflicts = best_state, best_c
        if conflicts == 0:
            solved = True
            break
    return {
        "solved": solved, "time": time.perf_counter() - t0,
        "state": state if solved else None,
        "initial": initial, "final_conflicts": conflicts, **stats
    }


# =====================================================================
# 2. BACKTRACKING
# =====================================================================
def backtracking_solve(n):
    """Backtracking on an EMPTY board, row by row. Returns the first solution + stats."""
    t0 = time.perf_counter()
    cols = [-1] * n
    stats = {"nodes": 0, "backtracks": 0, "checks": 0}

    def safe(row, col):
        for r in range(row):
            stats["checks"] += 1
            if cols[r] == col or abs(cols[r] - col) == row - r:
                return False
        return True

    def place(row):
        if row == n:
            return True
        for col in range(n):
            if safe(row, col):
                cols[row] = col
                stats["nodes"] += 1          # a queen was placed
                if place(row + 1):
                    return True
                cols[row] = -1
                stats["backtracks"] += 1     # queen removed again
        return False

    solved = place(0)
    return {"solved": solved, "time": time.perf_counter() - t0,
            "state": cols if solved else None, **stats}


def get_hint(current_board):
    """
    Best empty cell number on the top empty row, or -1 when the queens already
    on the board can no longer lead to a solution. Existing queens are fixed.
    """
    n = len(current_board)
    placements = [-1] * n
    for row in range(n):
        queens = [c for c in range(n) if current_board[row][c] == 'Q']
        if len(queens) > 1:
            return -1
        if queens:
            placements[row] = queens[0]
    for row in range(n):
        if placements[row] == -1:
            continue
        for prev in range(row):
            if placements[prev] == -1:
                continue
            if (placements[prev] == placements[row] or
                    abs(prev - row) == abs(placements[prev] - placements[row])):
                return -1

    def is_safe(row, col):
        for other_row in range(row):
            other_col = placements[other_row]
            if other_col == -1:
                continue
            if other_col == col or abs(other_row - row) == abs(other_col - col):
                return False
        return True

    def backtrack(row):
        if row == n:
            return True
        if placements[row] != -1:
            return is_safe(row, placements[row]) and backtrack(row + 1)
        for col in range(n):
            if is_safe(row, col):
                placements[row] = col
                if backtrack(row + 1):
                    return True
                placements[row] = -1
        return False

    if not backtrack(0):
        return -1
    for row in range(n):
        if 'Q' not in current_board[row]:
            return row * n + placements[row]
    return -1


# =====================================================================
# BOARD DRAWING (shared by visualizer, comparison and game)
# =====================================================================
def get_conflicting_rows(state):
    conflicting = set()
    for i in range(len(state)):
        for j in range(i + 1, len(state)):
            if state[i] == state[j] or abs(state[i] - state[j]) == abs(i - j):
                conflicting.add(i)
                conflicting.add(j)
    return conflicting


def board_lines(state):
    """Board as a list of text lines (each 3 chars per column + row label)."""
    n = len(state)
    conflicting = get_conflicting_rows(state)
    lines = ["     " + "".join(f"{c + 1:^3}" for c in range(n))]
    for row in range(n):
        line = f" {row + 1:>2}  "
        for col in range(n):
            if col == state[row]:
                shade = RED + BOLD if row in conflicting else GREEN + BOLD
                line += color(" Q ", shade)
            else:
                line += " . " if (row + col) % 2 == 0 else color(" . ", GRAY)
        lines.append(line)
    return lines


def print_board(state):
    print()
    for line in board_lines(state):
        print(line)
    print()


# =====================================================================
# 3. HILL CLIMBING VISUALIZER
# =====================================================================
def print_neighbors(step):
    neighbors = step.get("neighbors", [])
    if not neighbors:
        print(color("No neighbors generated in this step.", GRAY))
        return
    best_conflicts = min(item["conflicts"] for item in neighbors)
    print(color("\nNEIGHBOR EXPLORATION", CYAN + BOLD))
    print("-" * 76)
    print(f"{'No.':<6}{'Neighbor State':<25}{'Conflicts':<13}{'Status'}")
    print("-" * 76)
    for index, neighbor in enumerate(neighbors, start=1):
        state_text = str(neighbor["state"])
        conflicts = neighbor["conflicts"]
        if conflicts == best_conflicts:
            status = color("BEST", GREEN + BOLD)
            state_text = color(state_text, GREEN + BOLD)
            conflict_text = color(str(conflicts), GREEN + BOLD)
        else:
            status = color("Candidate", GRAY)
            conflict_text = str(conflicts)
        print(f"{index:<6}{state_text:<34}{conflict_text:<13}{status}")
    print("-" * 76)
    print(color("BEST NEIGHBOR: ", GREEN + BOLD), step["best_neighbor"],
          color(f" | Conflicts: {step['best_conflicts']}", GREEN))


def display_step(history, index):
    clear_screen()
    step = history[index]
    action = step["action"]
    header("N-QUEENS | HILL CLIMBING VISUALIZER")
    print(f"\n  STEP: {index + 1} / {len(history)}"
          f"       SESSION: {step['restart']}"
          f"       ITERATION: {step['iteration']}")
    print("\n" + "-" * 76)
    if action == "restart":
        status = color("NEW RESTART", YELLOW + BOLD)
        description = "A new random initial state has been generated."
    elif action == "move":
        status = color("MOVE TO BEST NEIGHBOR", GREEN + BOLD)
        description = "An improvement was found. Moving to the best neighbor."
    elif action == "local_minimum":
        status = color("LOCAL MINIMUM", RED + BOLD)
        description = "No better neighbor exists. Restarting is required."
    elif action == "solution":
        status = color("SOLUTION FOUND!", GREEN + BOLD)
        description = "All queens are placed without any conflicts."
    else:
        status = color("RESTART LIMIT REACHED", RED + BOLD)
        description = "Maximum number of restarts has been reached."
    print(f"\n  STATUS: {status}")
    print(f"  {description}")
    print(color("\nCURRENT BOARD", CYAN + BOLD))
    if step["current_state"]:
        print_board(step["current_state"])
        print(f"  CURRENT STATE: {step['current_state']}")
        print(f"  CONFLICTS: {step['current_conflicts']}")
    if action in ("move", "local_minimum"):
        print_neighbors(step)
    print("\n" + "=" * 76)
    print(color("  <- LEFT: Previous Step", YELLOW), "      ",
          color("RIGHT ->: Next Step", YELLOW))
    print(color("  P: Previous", CYAN), "   ", color("N: Next", CYAN), "   ",
          color("Q: Back to menu", RED))
    print("=" * 76)


def run_visualizer():
    clear_screen()
    print("N-Queens Hill Climbing Visualizer")
    print("----------------------------------")
    n = 4 if ask_menu("Select board size", ["4 Queens", "8 Queens"]) == 1 else 8
    history = build_history(n=n)
    current_step = 0
    while True:
        display_step(history, current_step)
        key = get_key()
        if key in ("right", "n"):
            current_step = min(current_step + 1, len(history) - 1)
        elif key in ("left", "p"):
            current_step = max(current_step - 1, 0)
        elif key == "q":
            break


# =====================================================================
# 4. PLAY WITH HINTS
# =====================================================================
def check_solution(board):
    n = len(board)
    queens = [(r, c) for r in range(n) for c in range(n) if board[r][c] == 'Q']
    if len(queens) != n:
        return False
    for i in range(n):
        for j in range(i + 1, n):
            (r1, c1), (r2, c2) = queens[i], queens[j]
            if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                return False
    return True


def draw_play_board(board):
    n = len(board)
    state = [-1] * n
    for r in range(n):
        for c in range(n):
            if board[r][c] == 'Q':
                state[r] = c
    # queens that attack each other are shown in red
    bad = set()
    queens = [(r, c) for r in range(n) for c in range(n) if board[r][c] == 'Q']
    for i in range(len(queens)):
        for j in range(i + 1, len(queens)):
            (r1, c1), (r2, c2) = queens[i], queens[j]
            if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                bad.add(queens[i])
                bad.add(queens[j])
    sep = "+----" * n + "+"
    for r in range(n):
        print(sep)
        for c in range(n):
            cell = board[r][c]
            if cell == 'Q':
                text = color(f"{'Q':>2}", (RED if (r, c) in bad else GREEN) + BOLD)
            else:
                text = color(f"{cell:>2}", GRAY)
            print(f"| {text}", end=" ")
        print("|")
    print(sep)


def play_with_hints():
    clear_screen()
    n = 4 if ask_menu("Select board size", ["4 x 4", "8 x 8"]) == 1 else 8
    while True:
        board = [[r * n + c for c in range(n)] for r in range(n)]
        message = ""
        while True:
            clear_screen()
            header(f"N-QUEENS  |  PLAY WITH HINTS  ({n}x{n})")
            draw_play_board(board)
            placed = sum(row.count('Q') for row in board)
            print(f"\n  Queens placed: {placed}/{n}")
            print(color("  Type a cell number to place a queen", GRAY))
            print(color("  -2 = hint    -3 = remove a queen    -1 = back to menu", GRAY))
            if message:
                print("\n  " + message)
            message = ""
            try:
                number = int(input("\n  Your move > "))
            except ValueError:
                message = color("Enter a valid number!", RED)
                continue
            if number == -1:
                return
            if number == -2:
                hint = get_hint(board)
                if hint == -1:
                    message = color("No solution is possible with the current queens. "
                                    "Remove one (-3).", RED)
                else:
                    r, c = divmod(hint, n)
                    message = color(f"Hint: place a queen on cell {hint} "
                                    f"(row {r + 1}, column {c + 1}).", YELLOW + BOLD)
                continue
            if number == -3:
                try:
                    pos = int(input("  Cell number of the queen to remove > "))
                except ValueError:
                    message = color("Enter a valid number!", RED)
                    continue
                if not 0 <= pos < n * n:
                    message = color("That cell does not exist.", RED)
                    continue
                r, c = divmod(pos, n)
                if board[r][c] != 'Q':
                    message = color("There is no queen on that cell.", RED)
                else:
                    board[r][c] = pos
                continue
            if not 0 <= number < n * n:
                message = color("That cell does not exist.", RED)
                continue
            r, c = divmod(number, n)
            if board[r][c] == 'Q':
                message = color("A queen is already there!", RED)
                continue
            board[r][c] = 'Q'
            if sum(row.count('Q') for row in board) == n:
                clear_screen()
                header(f"N-QUEENS  |  PLAY WITH HINTS  ({n}x{n})")
                draw_play_board(board)
                if check_solution(board):
                    print(color("\n  Congratulations! The solution is correct.", GREEN + BOLD))
                else:
                    print(color("\n  All queens are placed, but the solution is incorrect.",
                                RED + BOLD))
                if input("\n  Play again? (y/n) > ").strip().lower() != "y":
                    return
                break


# =====================================================================
# 5. COMPARISON: Hill Climbing (random board) vs Backtracking (empty board)
# =====================================================================
def _avg(values):
    return sum(values) / len(values) if values else 0.0


def _side_by_side(left_title, left_lines, right_title, right_lines, gap=6):
    visible = 5 + 3 * (len(left_lines) - 1)           # visible width of one board
    print(f"  {left_title:<{visible + gap}}{right_title}")
    for a, b in zip(left_lines, right_lines):
        print(f"  {a}{' ' * gap}{b}")


def run_comparison():
    clear_screen()
    header("N-QUEENS  |  COMPARISON")
    print("\n  Hill Climbing gets a RANDOM board, Backtracking gets an EMPTY board.")
    print("  Everything runs in the background - only the statistics are shown.\n")
    n = ask_int("  Board size N (4-12) [8] > ", 4, 12, default=8)
    trials = ask_int("  Number of trials (1-100) [20] > ", 1, 100, default=20)
    max_restarts = 100

    print(color("\n  Running...", GRAY))
    hc_runs = [hill_climbing_fast(n, max_restarts) for _ in range(trials)]
    bt_runs = [backtracking_solve(n) for _ in range(trials)]

    hc_ok = [r for r in hc_runs if r["solved"]]
    hc_times = [r["time"] * 1000 for r in hc_runs]
    bt_times = [r["time"] * 1000 for r in bt_runs]
    bt = bt_runs[0]
    hc_rate = 100 * len(hc_ok) / trials
    bt_rate = 100 * sum(r["solved"] for r in bt_runs) / trials

    clear_screen()
    header(f"N-QUEENS COMPARISON  |  N = {n}  |  {trials} trial(s)")
    W = 24
    print(color(f"\n  {'':<{W}}{'HILL CLIMBING':<22}BACKTRACKING", CYAN + BOLD))
    print("  " + "-" * 68)

    def row(label, a, b):
        print(f"  {label:<{W}}{str(a):<22}{b}")

    row("Starting board", "random permutation", "empty board")
    row("Strategy", f"restarts <= {max_restarts}", "row by row, undo on conflict")
    row("Solved", f"{len(hc_ok)}/{trials} ({hc_rate:.0f}%)", f"{trials}/{trials} ({bt_rate:.0f}%)")
    row("Avg time (ms)", f"{_avg(hc_times):.3f}", f"{_avg(bt_times):.3f}")
    row("Fastest / slowest (ms)", f"{min(hc_times):.3f} / {max(hc_times):.3f}",
        f"{min(bt_times):.3f} / {max(bt_times):.3f}")
    row("Avg restarts used", f"{_avg([r['restarts'] for r in hc_runs]):.1f}", "-")
    row("Avg moves (iterations)", f"{_avg([r['iterations'] for r in hc_runs]):.1f}", "-")
    row("Avg local minima hit", f"{_avg([r['local_minima'] for r in hc_runs]):.1f}", "-")
    row("States evaluated (avg)", f"{_avg([r['evaluated'] for r in hc_runs]):.0f}", "-")
    row("Queens placed (nodes)", "-", bt["nodes"])
    row("Backtracks", "-", bt["backtracks"])
    row("Safety checks", "-", bt["checks"])
    row("Same result every run?", "no (random)", "yes (deterministic)")

    # ----- bar chart of the average time -----
    hc_avg, bt_avg = _avg(hc_times), _avg(bt_times)
    top = max(hc_avg, bt_avg, 1e-9)
    print(color("\n  AVERAGE TIME", BOLD))
    print(f"  Hill Climbing  {color(bar(hc_avg, top), YELLOW)} {hc_avg:.3f} ms")
    print(f"  Backtracking   {color(bar(bt_avg, top), GREEN)} {bt_avg:.3f} ms")

    # ----- verdict -----
    print(color("\n  VERDICT", BOLD))
    if hc_avg > 0 and bt_avg > 0:
        if bt_avg <= hc_avg:
            print(f"  Fastest      : {color('Backtracking', GREEN + BOLD)} "
                  f"({hc_avg / bt_avg:.1f}x faster on average)")
        else:
            print(f"  Fastest      : {color('Hill Climbing', GREEN + BOLD)} "
                  f"({bt_avg / hc_avg:.1f}x faster on average)")
    if hc_rate < 100:
        print(f"  Reliability  : Backtracking always finds a solution; Hill Climbing "
              f"failed in {trials - len(hc_ok)} of {trials} runs.")
    else:
        print("  Reliability  : both solved every trial "
              "(Hill Climbing needed restarts to escape local minima).")

    # ----- example boards -----
    first = hc_runs[0]
    print(color("\n  EXAMPLE BOARDS", BOLD))
    if first["initial"]:
        print(f"\n  Hill Climbing started from {first['initial'][0]} "
              f"with {first['initial'][1]} conflicts.")
    if first["solved"] and bt["solved"]:
        _side_by_side("Hill Climbing solution:", board_lines(first["state"]),
                      "Backtracking solution:", board_lines(bt["state"]))
    elif bt["solved"]:
        print("  (Hill Climbing did not solve trial 1.)")
        print_board(bt["state"])
    pause()


# =====================================================================
# MODULE MENU
# =====================================================================
def run():
    while True:
        clear_screen()
        header("N-QUEENS")
        choice = ask_menu("What do you want to do?", [
            "Play with hints",
            "Hill Climbing visualizer (step by step)",
            "Compare Hill Climbing vs Backtracking",
            "Back to main menu",
        ])
        if choice == 1:
            play_with_hints()
        elif choice == 2:
            run_visualizer()
        elif choice == 3:
            run_comparison()
        else:
            return


if __name__ == "__main__":
    run()
