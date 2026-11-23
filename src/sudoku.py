"""
sudoku.py - everything about Sudoku in ONE file

  1. SudokuGame        : game logic (validation, hints, status)
  2. Solvers           : Backtracking / Forward Checking / MRV (+ step recorder)
  3. Play              : improved console board
  4. Visualizer        : step-by-step Forward Checking / MRV viewer
  5. Comparison        : Backtracking vs Forward Checking vs MRV on an empty board
"""
import time

from utils import (clear_screen, pause, header, ask_int, ask_menu, bar,
                   color, RESET, BOLD, DIM, CYAN, GREEN, RED, YELLOW, WHITE, GRAY)

BG_CYAN, BG_YELLOW, BG_RED = "\033[46;30m", "\033[43;30m", "\033[41;97m"

# ---------- sample puzzles (0 = empty) ----------
PUZZLES = {
    "1": ("Easy",   "530070000600195000098000060800060003400803001700020006060000280000419005000080079"),
    "2": ("Medium", "003020600900305001001806400008102900700000008006708200002609500800203009005010300"),
    "3": ("Hard",   "200080300060070084030500209000105408000000000402706000301007040720040060004010003"),
}
EMPTY_PUZZLE = "0" * 81


def to_board(puzzle):
    return [[int(puzzle[r * 9 + c]) for c in range(9)] for r in range(9)]


# ---------- peers: for every cell, the other cells in its row, column and box ----------
PEERS = []
for _i in range(81):
    _r, _c = _i // 9, _i % 9
    _p = set()
    for _k in range(9):
        _p.add(_r * 9 + _k)
        _p.add(_k * 9 + _c)
    for _rr in range(_r // 3 * 3, _r // 3 * 3 + 3):
        for _cc in range(_c // 3 * 3, _c // 3 * 3 + 3):
            _p.add(_rr * 9 + _cc)
    _p.discard(_i)
    PEERS.append(sorted(_p))


def label(i):
    """Cell number 0..80 -> readable name, e.g. 0 -> r1c1."""
    return f"r{i // 9 + 1}c{i % 9 + 1}"


def clues_conflict(grid):
    """True if two given numbers contradict each other."""
    return any(grid[i] and any(grid[p] == grid[i] for p in PEERS[i]) for i in range(81))


# =====================================================================
# 1. GAME LOGIC  (your SudokuGame class, plus a 'given' mask)
# =====================================================================
class SudokuGame:
    def __init__(self, board):
        self.board = board
        self.size = 9
        # original clues can not be removed by the player
        self.given = [[board[r][c] != 0 for c in range(9)] for r in range(9)]

    def is_valid(self, row, col, num):
        return self.is_valid_on_board(self.board, row, col, num)

    def get_candidates(self, row, col):
        if 1 <= self.board[row][col] <= 9:
            return []
        return [n for n in range(1, 10) if self.is_valid(row, col, n)]

    def find_empty(self):
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    return row, col
        return None

    def place_number(self, row, col, num):
        if num < 1 or num > 9:
            return False, "Enter a number between 1 and 9."
        if self.board[row][col] != 0:
            return False, "This cell is already occupied."
        if self.is_valid(row, col, num):
            self.board[row][col] = num
            return True, "Number placed successfully."
        return False, "Invalid move! That number already exists in the row, column or box."

    def is_valid_on_board(self, board, row, col, num):
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False
        start_row, start_col = (row // 3) * 3, (col // 3) * 3
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if board[i][j] == num:
                    return False
        return True

    def solve_backtracking(self, board):
        empty_cell = None
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    empty_cell = (row, col)
                    break
            if empty_cell is not None:
                break
        if empty_cell is None:
            return True
        row, col = empty_cell
        for num in range(1, 10):
            if self.is_valid_on_board(board, row, col, num):
                board[row][col] = num
                if self.solve_backtracking(board):
                    return True
                board[row][col] = 0
        return False

    def get_hint(self):
        solution = [row.copy() for row in self.board]
        if not self.solve_backtracking(solution):
            return None
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    return row, col, solution[row][col]
        return None

    def remove_number(self, row, col):
        if self.given[row][col]:
            return False, "That number is part of the puzzle and can not be removed."
        if self.board[row][col] == 0:
            return False, "This cell is already empty."
        self.board[row][col] = 0
        return True, "Number removed successfully."

    def get_game_status(self):
        empty_cell = self.find_empty()
        solution = [row.copy() for row in self.board]
        if not self.solve_backtracking(solution):
            return "unsolvable"
        if empty_cell is None:
            return "completed"
        return "in_progress"

    def solved_copy(self):
        solution = [row.copy() for row in self.board]
        return solution if self.solve_backtracking(solution) else None


# =====================================================================
# 3. PLAY  (improved board)
# =====================================================================
def display_board(game, highlight=None, hint_cell=None):
    """
    Colourful board with row / column numbers (1-9) and thick 3x3 boxes.
      white bold = given clue      green = your number
      cyan bg    = last change     yellow bg = hint
    """
    board = game.board
    filled = sum(1 for r in range(9) for c in range(9) if board[r][c])
    print(color(f"\n   Filled: {filled}/81   Empty: {81 - filled}", GRAY))
    print()
    print("      " + " ".join("".join(color(f" {c + 1} ", CYAN + BOLD)
                                       for c in range(b * 3, b * 3 + 3))
                                for b in range(3)))
    top = "     ╔"+"╦".join(["═"*9]*3)+"╗"
    mid = "     ╠"+"╬".join(["═"*9]*3)+"╣"
    bot = "     ╚"+"╩".join(["═"*9]*3)+"╝"
    print(top)
    for r in range(9):
        line = f"  {color(r + 1, CYAN + BOLD)}  ║"
        for c in range(9):
            v = board[r][c]
            text = str(v) if v else "·"
            if (r, c) == hint_cell:
                cell = color(f" {text} ", "\033[43;30m")
            elif (r, c) == highlight:
                cell = color(f" {text} ", "\033[46;30m")
            elif v == 0:
                cell = color(f" {text} ", GRAY)
            elif game.given[r][c]:
                cell = color(f" {text} ", WHITE + BOLD)
            else:
                cell = color(f" {text} ", GREEN)
            line += cell
            if c % 3 == 2:
                line += "║"
        print(line)
        if r % 3 == 2 and r != 8:
            print(mid)
    print(bot)


def _parse_numbers(text, count):
    parts = text.replace(",", " ").split()
    if len(parts) != count or not all(p.isdigit() for p in parts):
        return None
    return [int(p) for p in parts]


def play_game():
    clear_screen()
    header("SUDOKU  |  PLAY")
    print("\n  Choose a puzzle:")
    for k, (name, _) in PUZZLES.items():
        print(f"    {k}) {name}")
    choice = ask_int("\n  Puzzle [1-3] > ", 1, 3)
    game = SudokuGame(to_board(PUZZLES[str(choice)][1]))
    message, highlight, hint_cell = "", None, None
    while True:
        clear_screen()
        header("SUDOKU  |  PLAY")
        display_board(game, highlight, hint_cell)
        print(color("\n  p  row col num   place a number   (example: p 1 3 4)", GRAY))
        print(color("  r  row col       remove a number", GRAY))
        print(color("  c  row col       show candidates   h  hint   s  status", GRAY))
        print(color("  solve = show full solution          q  back to menu", GRAY))
        if message:
            print("\n  " + message)
        message, highlight, hint_cell = "", None, None
        cmd = input("\n  > ").strip().lower()
        if not cmd:
            continue
        action, args = cmd.split()[0], cmd[len(cmd.split()[0]):]
        if action in ("q", "quit", "-1"):
            return
        if action == "p":
            nums = _parse_numbers(args, 3)
            if not nums or not (1 <= nums[0] <= 9 and 1 <= nums[1] <= 9):
                message = color("Use:  p row col num   (all between 1 and 9)", RED)
                continue
            ok, msg = game.place_number(nums[0] - 1, nums[1] - 1, nums[2])
            message = color(msg, GREEN if ok else RED)
            if ok:
                highlight = (nums[0] - 1, nums[1] - 1)
                if game.find_empty() is None:
                    clear_screen()
                    header("SUDOKU  |  PLAY")
                    display_board(game, highlight)
                    print(color("\n  Congratulations! You completed the Sudoku!", GREEN + BOLD))
                    pause()
                    return
        elif action == "r":
            nums = _parse_numbers(args, 2)
            if not nums or not all(1 <= x <= 9 for x in nums):
                message = color("Use:  r row col", RED)
                continue
            ok, msg = game.remove_number(nums[0] - 1, nums[1] - 1)
            message = color(msg, GREEN if ok else RED)
        elif action == "c":
            nums = _parse_numbers(args, 2)
            if not nums or not all(1 <= x <= 9 for x in nums):
                message = color("Use:  c row col", RED)
                continue
            r, c = nums[0] - 1, nums[1] - 1
            if game.board[r][c]:
                message = color("That cell is already filled.", RED)
            else:
                cands = game.get_candidates(r, c)
                message = color(f"Candidates for row {r + 1}, col {c + 1}: "
                                f"{cands if cands else 'none (dead end!)'}", YELLOW)
                highlight = (r, c)
        elif action == "h":
            hint = game.get_hint()
            if hint is None:
                message = color("No solution exists for the current board. Remove a number.", RED)
            else:
                r, c, n = hint
                message = color(f"Hint: place {n} at row {r + 1}, column {c + 1}.", YELLOW + BOLD)
                hint_cell = (r, c)
        elif action == "s":
            status = game.get_game_status()
            texts = {"in_progress": ("Game is in progress - still solvable.", GREEN),
                     "completed": ("Completed!", GREEN),
                     "unsolvable": ("This board can not be solved. Remove a number.", RED)}
            message = color(*texts[status])
        elif action == "solve":
            sol = game.solved_copy()
            if sol is None:
                message = color("No solution exists for the current board.", RED)
            else:
                game.board = sol
                message = color("Solved by backtracking.", GREEN)
        else:
            message = color("Unknown command.", RED)


# =====================================================================
# 2. SOLVER WITH STEP RECORDER  (your MRV + Forward Checking code)
# =====================================================================
def run_solver(puzzle, use_mrv, keep_frames):
    grid = [int(ch) for ch in puzzle]
    given = [v != 0 for v in grid]
    stats = {"assignments": 0, "backtracks": 0, "prunes": 0}
    history = []
    domains = [set() for _ in range(81)]
    for i in range(81):
        if grid[i] == 0:
            domains[i] = set(range(1, 10)) - {grid[p] for p in PEERS[i]}

    def record(title, notes, current=None, pruned=(), fail=None, force=False):
        if not keep_frames and not force:
            return
        if len(history) >= 5000 and not force:
            raise OverflowError
        history.append({
            "title": title, "notes": notes, "grid": grid[:],
            "doms": ["".join(map(str, sorted(domains[i]))) if grid[i] == 0 else ""
                     for i in range(81)],
            "current": current, "pruned": list(pruned), "fail": fail,
            "stats": (stats["assignments"], stats["backtracks"], stats["prunes"]),
        })

    def solve():
        empty = [i for i in range(81) if grid[i] == 0]
        if not empty:
            return True
        if use_mrv:
            cell = min(empty, key=lambda i: len(domains[i]))
            why = f"MRV: {label(cell)} has the fewest remaining values ({len(domains[cell])})."
        else:
            cell = empty[0]
            why = f"Fixed order: {label(cell)} is the first empty cell."
        values = sorted(domains[cell])
        record(f"SELECT {label(cell)}",
               [why, f"Domain of {label(cell)} = {values}"], current=cell)
        if not values:
            stats["backtracks"] += 1
            record(f"DEAD END at {label(cell)}",
                   ["Domain is empty, so the previous choice was wrong. Backtrack."], fail=cell)
            return False
        for v in values:
            grid[cell] = v
            stats["assignments"] += 1
            removed, wipeout, notes = [], None, []
            for p in PEERS[cell]:
                if grid[p] == 0 and v in domains[p]:
                    domains[p].remove(v)
                    removed.append(p)
                    stats["prunes"] += 1
                    notes.append(f"{label(p)}: removed {v}, domain is now {sorted(domains[p])}")
                    if len(domains[p]) == 0:
                        wipeout = p
                        notes.append(f"WIPE-OUT: {label(p)} has no value left!")
                        break
            if not removed:
                notes.append(f"{v} was in no peer domain, nothing to remove.")
            if len(notes) > 7:
                notes = notes[:6] + [f"... {len(notes) - 6} more lines"]
            record(f"TRY {label(cell)} = {v}", notes,
                   current=cell, pruned=removed, fail=wipeout)
            if wipeout is None and solve():
                return True
            for p in removed:
                domains[p].add(v)
            grid[cell] = 0
            stats["backtracks"] += 1
            record(f"BACKTRACK: undo {label(cell)} = {v}",
                   ["Value removed again, domains restored. Trying the next value."],
                   current=cell)
        return False

    if clues_conflict(grid):
        return None, history, given, stats
    try:
        solved = solve()
    except OverflowError:
        return "TOO_LONG", history, given, stats
    if solved:
        record("SOLVED!", ["Every cell is filled."], force=True)
    else:
        record("NO SOLUTION", ["The search tried everything."], force=True)
    return solved, history, given, stats


# =====================================================================
# 4. VISUALIZER
# =====================================================================
def draw(f, given, name, number, total, clear):
    if clear:
        clear_screen()
    print(f"{BOLD}{CYAN}=== {name} ===   Step {number}/{total}{RESET}")
    print(f"Assignments: {f['stats'][0]}   Backtracks: {f['stats'][1]}   "
          f"Prunes: {f['stats'][2]}")

    def colour(i, text, normal):
        if i == f["fail"]:
            return f"{BG_RED}{text}{RESET}"
        if i == f["current"]:
            return f"{BG_CYAN}{text}{RESET}"
        if i in f["pruned"]:
            return f"{BG_YELLOW}{text}{RESET}"
        return normal(text)

    def plain(text):
        return text

    print(f"\n{BOLD}BOARD{RESET}  (white = given, green = placed by the search)")
    print("     " + " ".join("".join(f" {c + 1} " for c in range(b * 3, b * 3 + 3))
                               for b in range(3)))
    print("    ╔" + "╦".join(["═" * 9] * 3) + "╗")
    for r in range(9):
        line = f" {r + 1}  ║"
        for c in range(9):
            i = r * 9 + c
            v = f["grid"][i]
            text = f" {v if v else '·'} "
            if given[i]:
                line += colour(i, text, lambda t: f"{BOLD}{WHITE}{t}{RESET}")
            elif v:
                line += colour(i, text, lambda t: f"{GREEN}{t}{RESET}")
            else:
                line += colour(i, text, lambda t: f"{DIM}{t}{RESET}")
            if c % 3 == 2:
                line += "║"
        print(line)
        if r % 3 == 2 and r != 8:
            print("    ╠" + "╬".join(["═" * 9] * 3) + "╣")
    print("    ╚" + "╩".join(["═" * 9] * 3) + "╝")

    print(f"\n{BOLD}DOMAINS{RESET}  (each empty cell shows the values it can still take)")
    print("    " + " ".join(f"c{c + 1}".center(9) for c in range(9)))
    for r in range(9):
        if r % 3 == 0:
            print("   " + "#" * 91)
        line = f"r{r + 1} #"
        for c in range(9):
            i = r * 9 + c
            v = f["grid"][i]
            if v:
                line += colour(i, str(v).center(9), lambda t: f"{GREEN}{t}{RESET}")
            else:
                line += colour(i, f["doms"][i].center(9), plain)
            line += "#" if c % 3 == 2 else "|"
        print(line)
    print("   " + "#" * 91)
    print(f"\n{BOLD}{f['title']}{RESET}")
    for n in f["notes"]:
        print(f"   {n}")
    print()


def run_visualizer():
    algorithms = {1: ("Forward Checking", False), 2: ("MRV (with Forward Checking)", True)}
    clear_screen()
    header("SUDOKU  |  SOLVER VISUALIZER")
    name, use_mrv = algorithms[ask_menu("Choose an algorithm", ["Forward Checking", "MRV"])]
    pick = ask_menu("Choose a puzzle", ["Easy", "Medium", "Hard", "Type my own"])
    if pick != 4:
        puzzle = PUZZLES[str(pick)][1]
    else:
        puzzle = ""
        while len(puzzle) != 81 or not puzzle.isdigit():
            puzzle = "".join(input("Type 81 digits (0 or . = empty): ").split()).replace(".", "0")
    step = ""
    while step not in ("y", "n"):
        step = input("Step-by-step? (y/n): ").strip().lower()
    solved, history, given, stats = run_solver(puzzle, use_mrv, step == "y")
    if solved is None:
        print("The clues of this puzzle contradict each other.")
    elif solved == "TOO_LONG":
        print("Too many steps to show. Try step-by-step = n, or use MRV.")
    elif step == "n":
        draw(history[-1], given, name, 1, 1, clear=False)
    else:
        i = 0
        while True:
            draw(history[i], given, name, i + 1, len(history), clear=True)
            cmd = input("[Enter] next   [b] back   [g] go to step   "
                        "[e] end   [q] quit > ").strip().lower()
            if cmd in ("", "n"):
                i = min(i + 1, len(history) - 1)
            elif cmd == "b":
                i = max(i - 1, 0)
            elif cmd == "e":
                i = len(history) - 1
            elif cmd == "g":
                number = input("Step number: ").strip()
                if number.isdigit():
                    i = min(max(int(number) - 1, 0), len(history) - 1)
            elif cmd == "q":
                break
    if solved not in (None, "TOO_LONG"):
        print(f"\nTotal: {stats['assignments']} assignments, "
              f"{stats['backtracks']} backtracks, {stats['prunes']} prunes")
    pause()


# =====================================================================
# 5. COMPARISON  (lean solvers - no frames, only counters)
# =====================================================================
class _LimitReached(Exception):
    pass


def solve_for_comparison(puzzle, mode, limit=3_000_000):
    """
    mode: 'bt'  - plain backtracking, first empty cell, tries 1..9
          'fc'  - forward checking, first empty cell
          'mrv' - forward checking + Minimum Remaining Values
    Returns a dict of statistics.
    """
    grid = [int(ch) for ch in puzzle]
    empties = [i for i in range(81) if grid[i] == 0]
    stats = {"nodes": 0, "assignments": 0, "backtracks": 0, "prunes": 0,
             "checks": 0, "max_depth": 0}
    domains = [set() for _ in range(81)]
    if mode != "bt":
        for i in empties:
            domains[i] = set(range(1, 10)) - {grid[p] for p in PEERS[i]}

    def tick():
        stats["assignments"] += 1
        if stats["assignments"] > limit:
            raise _LimitReached

    def solve_bt(k):
        if k == len(empties):
            return True
        stats["nodes"] += 1
        stats["max_depth"] = max(stats["max_depth"], k)
        cell = empties[k]
        for v in range(1, 10):
            ok = True
            for p in PEERS[cell]:                  # is v already used by a peer?
                stats["checks"] += 1
                if grid[p] == v:
                    ok = False
                    break
            if not ok:
                continue
            grid[cell] = v
            tick()
            if solve_bt(k + 1):
                return True
            grid[cell] = 0
            stats["backtracks"] += 1
        return False

    def solve_fc(k, use_mrv):
        if k == len(empties):
            return True
        stats["nodes"] += 1
        stats["max_depth"] = max(stats["max_depth"], k)
        if use_mrv:
            cell = min((i for i in empties if grid[i] == 0), key=lambda i: len(domains[i]))
        else:
            cell = empties[k]
        for v in sorted(domains[cell]):
            grid[cell] = v
            tick()
            removed, wipeout = [], False
            for p in PEERS[cell]:
                if grid[p] == 0:
                    stats["checks"] += 1
                    if v in domains[p]:
                        domains[p].remove(v)
                        removed.append(p)
                        stats["prunes"] += 1
                        if not domains[p]:
                            wipeout = True
                            break
            if not wipeout and solve_fc(k + 1, use_mrv):
                return True
            for p in removed:
                domains[p].add(v)
            grid[cell] = 0
            stats["backtracks"] += 1
        return False

    t0 = time.perf_counter()
    status = "solved"
    if clues_conflict(grid):
        status = "invalid"
    else:
        try:
            ok = solve_bt(0) if mode == "bt" else solve_fc(0, mode == "mrv")
            status = "solved" if ok else "no solution"
        except _LimitReached:
            status = "gave up"
    stats["time"] = time.perf_counter() - t0
    stats["status"] = status
    stats["grid"] = grid[:] if status == "solved" else None
    return stats


def _compare_rows(puzzle, runs=5):
    algos = [("bt", "Backtracking"), ("fc", "Forward Checking"), ("mrv", "MRV + FC")]
    results = []
    for mode, name in algos:
        res = solve_for_comparison(puzzle, mode)
        if res["status"] == "solved" and res["time"] < 0.5:      # repeat tiny runs for a stable time
            times = [res["time"]] + [solve_for_comparison(puzzle, mode)["time"]
                                     for _ in range(runs - 1)]
            res["time"] = sum(times) / len(times)
        results.append((name, res))
    return results


def _print_solution(grid):
    for r in range(9):
        if r % 3 == 0 and r:
            print("      ------+-------+------")
        row = grid[r * 9:r * 9 + 9]
        print("      " + " | ".join(" ".join(str(v) for v in row[b * 3:b * 3 + 3])
                                     for b in range(3)))


def run_comparison():
    clear_screen()
    header("SUDOKU  |  COMPARISON")
    print("\n  Backtracking, Forward Checking and MRV solve the same board.")
    print("  Everything runs in the background - only the statistics are shown.")
    pick = ask_menu("Which board?", ["Empty board", "Easy puzzle", "Medium puzzle", "Hard puzzle"])
    if pick == 1:
        title, puzzle = "empty board", EMPTY_PUZZLE
    else:
        title, puzzle = PUZZLES[str(pick - 1)][0] + " puzzle", PUZZLES[str(pick - 1)][1]
    print(color("\n  Running (plain backtracking may be slow on hard puzzles)...", GRAY))
    results = _compare_rows(puzzle)

    clear_screen()
    header(f"SUDOKU COMPARISON  |  {title}")
    given = sum(ch != "0" for ch in puzzle)
    print(f"\n  Given numbers: {given}    Empty cells: {81 - given}\n")
    W = 22
    print(color(f"  {'':<{W}}" + "".join(f"{n:<20}" for n, _ in results), CYAN + BOLD))
    print("  " + "-" * (W + 60))

    # find the winner of each row (lowest number wins), only among solved runs
    def row(label_, key, fmt, lower_is_best=True, skip_best=False):
        values = [r[key] for _, r in results]
        solved_vals = [r[key] for _, r in results if r["status"] == "solved"]
        best = min(solved_vals) if (solved_vals and not skip_best) else None
        line = f"  {label_:<{W}}"
        for _, r in results:
            text = fmt(r[key])
            padded = f"{text:<20}"
            if best is not None and r["status"] == "solved" and r[key] == best:
                padded = color(f"{text:<20}", GREEN + BOLD)
            line += padded
        print(line)

    print(f"  {'Result':<{W}}" + "".join(
        color(f"{r['status']:<20}", GREEN if r['status'] == 'solved' else RED)
        for _, r in results))
    row("Time (ms)", "time", lambda v: f"{v * 1000:.3f}")
    row("Assignments", "assignments", lambda v: f"{v:,}")
    row("Backtracks", "backtracks", lambda v: f"{v:,}")
    row("Nodes visited", "nodes", lambda v: f"{v:,}")
    row("Constraint checks", "checks", lambda v: f"{v:,}")
    row("Values pruned", "prunes", lambda v: f"{v:,}", skip_best=True)
    row("Deepest level", "max_depth", lambda v: f"{v}", skip_best=True)
    print(color("\n  (green = best in that row)", GRAY))

    # bars
    ok = [(n, r) for n, r in results if r["status"] == "solved"]
    if ok:
        for key, name, fmt in (("time", "TIME (ms)", lambda v: f"{v * 1000:.3f}"),
                               ("assignments", "ASSIGNMENTS", lambda v: f"{v:,}"),
                               ("backtracks", "BACKTRACKS", lambda v: f"{v:,}")):
            top = max(r[key] for _, r in ok)
            print(color(f"\n  {name}", BOLD))
            for n, r in results:
                if r["status"] == "solved":
                    print(f"  {n:<18}{color(bar(r[key], top), YELLOW)} {fmt(r[key])}")
                else:
                    print(f"  {n:<18}{color(r['status'], RED)}")

        # ranking: points = position by time + assignments + backtracks
        points = {n: 0 for n, _ in ok}
        for key in ("time", "assignments", "backtracks"):
            for pos, (n, _) in enumerate(sorted(ok, key=lambda x: x[1][key])):
                points[n] += pos
        ranking = sorted(ok, key=lambda x: (points[x[0]], x[1]["time"]))
        print(color("\n  RANKING  (time + assignments + backtracks)", BOLD))
        medals = ["1st", "2nd", "3rd"]
        for pos, (n, r) in enumerate(ranking):
            print(f"  {medals[pos]}  {n:<18} {r['time'] * 1000:.3f} ms, "
                  f"{r['assignments']:,} assignments, {r['backtracks']:,} backtracks")
        print(color(f"\n  WINNER: {ranking[0][0]}", GREEN + BOLD))
        print(color("\n  SOLUTION FOUND", BOLD))
        _print_solution(ranking[0][1]["grid"])
    else:
        print(color("\n  No algorithm finished this puzzle.", RED))
    pause()


# =====================================================================
# MODULE MENU
# =====================================================================
def run():
    while True:
        clear_screen()
        header("SUDOKU")
        choice = ask_menu("What do you want to do?", [
            "Play Sudoku",
            "Solver visualizer (Forward Checking / MRV, step by step)",
            "Compare Backtracking vs Forward Checking vs MRV",
            "Back to main menu",
        ])
        if choice == 1:
            play_game()
        elif choice == 2:
            run_visualizer()
        elif choice == 3:
            run_comparison()
        else:
            return


if __name__ == "__main__":
    run()
