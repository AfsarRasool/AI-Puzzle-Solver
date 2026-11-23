"""
experiments.py - reproduces every number and chart in Chapter 6 of the report.

    python experiments.py --seed 42            # tables + results/results.json
    python experiments.py --seed 42 --charts   # also saves PNG charts (needs matplotlib)

Experiments
  A. N-Queens : Hill Climbing (random board) vs Backtracking (empty board), N = 4..12
  B. Sudoku   : Backtracking vs Forward Checking vs MRV+FC on 4 boards
  C. 8-Puzzle : BFS vs A* (Manhattan distance) on random solvable boards
"""
import argparse
import json
import os
import random
import statistics as st

import nqueen
import sudoku
from eight_puzzle import EightPuzzle, EightPuzzleSolver

NQ_SIZES = list(range(4, 13))


# ---------------------------------------------------------------- A. N-Queens
def exp_nqueens(trials):
    rows = []
    for n in NQ_SIZES:
        hc = [nqueen.hill_climbing_fast(n, 100) for _ in range(trials)]
        bt = [nqueen.backtracking_solve(n) for _ in range(trials)]
        rows.append({
            "n": n,
            "hc_success": 100 * sum(r["solved"] for r in hc) / trials,
            "hc_time_ms": st.mean(r["time"] for r in hc) * 1000,
            "hc_restarts": st.mean(r["restarts"] for r in hc),
            "hc_iterations": st.mean(r["iterations"] for r in hc),
            "hc_evaluated": st.mean(r["evaluated"] for r in hc),
            "bt_success": 100 * sum(r["solved"] for r in bt) / trials,
            "bt_time_ms": st.mean(r["time"] for r in bt) * 1000,
            "bt_nodes": bt[0]["nodes"],
            "bt_backtracks": bt[0]["backtracks"],
        })
    return rows


# ---------------------------------------------------------------- B. Sudoku
def exp_sudoku(runs=5):
    boards = [("Empty", sudoku.EMPTY_PUZZLE)] + \
             [(name, p) for name, p in sudoku.PUZZLES.values()]
    rows = []
    for bname, puzzle in boards:
        for mode, aname in (("bt", "Backtracking"), ("fc", "Forward Checking"),
                            ("mrv", "MRV + FC")):
            results = [sudoku.solve_for_comparison(puzzle, mode) for _ in range(runs)]
            r = results[0]
            rows.append({
                "board": bname, "algorithm": aname, "status": r["status"],
                "time_ms": st.mean(x["time"] for x in results) * 1000,
                "assignments": r["assignments"], "backtracks": r["backtracks"],
                "nodes": r["nodes"], "checks": r["checks"], "prunes": r["prunes"],
            })
    return rows


# ---------------------------------------------------------------- C. 8-Puzzle
def exp_eight(boards, seed):
    solver, puzzle = EightPuzzleSolver(), EightPuzzle()
    rows = []
    for i in range(boards):
        puzzle.shuffle(moves=40, seed=seed + i)
        start = puzzle.state
        bfs, astar = solver.solve(start, "bfs"), solver.solve(start, "astar")
        rows.append({
            "board": i, "moves_bfs": len(bfs["steps"]) - 1, "moves_astar": len(astar["steps"]) - 1,
            "nodes_bfs": bfs["nodes"], "nodes_astar": astar["nodes"],
            "time_bfs_ms": bfs["time"] * 1000, "time_astar_ms": astar["time"] * 1000,
        })
    return rows


# ---------------------------------------------------------------- printing
def print_tables(nq, sd, ep):
    print("\nA. N-QUEENS  (Hill Climbing vs Backtracking)")
    print(f"{'N':>3} {'HC solved%':>11} {'HC ms':>9} {'HC restarts':>12} {'HC evals':>10}"
          f" {'BT solved%':>11} {'BT ms':>9} {'BT nodes':>9} {'BT backtr.':>11}")
    for r in nq:
        print(f"{r['n']:>3} {r['hc_success']:>11.0f} {r['hc_time_ms']:>9.3f} {r['hc_restarts']:>12.1f}"
              f" {r['hc_evaluated']:>10.0f} {r['bt_success']:>11.0f} {r['bt_time_ms']:>9.3f}"
              f" {r['bt_nodes']:>9} {r['bt_backtracks']:>11}")
    print("\nB. SUDOKU")
    print(f"{'Board':<8}{'Algorithm':<18}{'Result':<8}{'ms':>8}{'Assign.':>9}{'Backtr.':>9}"
          f"{'Nodes':>8}{'Checks':>10}{'Prunes':>8}")
    for r in sd:
        print(f"{r['board']:<8}{r['algorithm']:<18}{r['status']:<8}{r['time_ms']:>8.3f}"
              f"{r['assignments']:>9}{r['backtracks']:>9}{r['nodes']:>8}{r['checks']:>10}{r['prunes']:>8}")
    print(f"\nC. 8-PUZZLE  ({len(ep)} random boards)")
    for k, label in (("nodes", "nodes expanded"), ("time", "time (ms)")):
        b = st.mean(r[f"{k}_bfs" if k == "nodes" else "time_bfs_ms"] for r in ep)
        a = st.mean(r[f"{k}_astar" if k == "nodes" else "time_astar_ms"] for r in ep)
        print(f"  mean {label:<15} BFS {b:>12.1f}   A* {a:>10.1f}   ratio {b / a:.1f}x")
    same = sum(r["moves_bfs"] == r["moves_astar"] for r in ep)
    print(f"  same solution length on {same}/{len(ep)} boards; "
          f"mean moves {st.mean(r['moves_astar'] for r in ep):.1f}")


# ---------------------------------------------------------------- charts
def make_charts(nq, sd, ep, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(out, exist_ok=True)
    C1, C2, C3 = "#2F5597", "#C55A11", "#548235"

    # 1. N-Queens: average time per N (log scale)
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=200)
    ns = [r["n"] for r in nq]
    w = 0.38
    ax.bar([n - w / 2 for n in ns], [r["hc_time_ms"] for r in nq], w, label="Hill Climbing", color=C2)
    ax.bar([n + w / 2 for n in ns], [r["bt_time_ms"] for r in nq], w, label="Backtracking", color=C1)
    ax.set_yscale("log"); ax.set_xticks(ns)
    ax.set_xlabel("Board size N"); ax.set_ylabel("Average time (ms, log scale)")
    ax.set_title("N-Queens: time to find a solution"); ax.legend(); ax.grid(axis="y", alpha=.3)
    for r in nq:
        if r["hc_success"] < 100:
            ax.annotate(f"{r['hc_success']:.0f}%", (r["n"] - w / 2, r["hc_time_ms"]),
                        ha="center", va="bottom", fontsize=7, color="#7F3B00")
    fig.tight_layout(); fig.savefig(f"{out}/chart_nqueens_time.png"); plt.close(fig)

    # 2. Sudoku: assignments per board (log scale)
    boards = ["Empty", "Easy", "Medium", "Hard"]
    algos = ["Backtracking", "Forward Checking", "MRV + FC"]
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=200)
    for k, (a, c) in enumerate(zip(algos, (C2, C1, C3))):
        vals = [next(r["assignments"] for r in sd if r["board"] == b and r["algorithm"] == a) for b in boards]
        xs = [i + (k - 1) * 0.26 for i in range(4)]
        bars = ax.bar(xs, vals, 0.26, label=a, color=c)
        for x, v in zip(xs, vals):
            ax.text(x, v * 1.08, f"{v:,}", ha="center", fontsize=6.5)
    ax.set_yscale("log"); ax.set_xticks(range(4)); ax.set_xticklabels(boards)
    ax.set_ylabel("Assignments (log scale)"); ax.set_title("Sudoku: search effort per algorithm")
    ax.legend(); ax.grid(axis="y", alpha=.3)
    fig.tight_layout(); fig.savefig(f"{out}/chart_sudoku_assignments.png"); plt.close(fig)

    # 3. 8-Puzzle: nodes expanded vs solution length
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=200)
    ax.scatter([r["moves_bfs"] for r in ep], [r["nodes_bfs"] for r in ep], s=14, color=C2, label="BFS", alpha=.8)
    ax.scatter([r["moves_astar"] for r in ep], [r["nodes_astar"] for r in ep], s=14, color=C1, label="A* (Manhattan)", alpha=.8)
    ax.set_yscale("log"); ax.set_xlabel("Optimal solution length (moves)")
    ax.set_ylabel("Nodes expanded (log scale)"); ax.set_title(f"8-Puzzle: nodes expanded on {len(ep)} boards")
    ax.legend(); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(f"{out}/chart_8puzzle_nodes.png"); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=100, help="N-Queens trials per board size")
    ap.add_argument("--boards", type=int, default=100, help="8-Puzzle boards")
    ap.add_argument("--charts", action="store_true")
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    random.seed(a.seed)
    nq, sd, ep = exp_nqueens(a.trials), exp_sudoku(), exp_eight(a.boards, a.seed)
    print_tables(nq, sd, ep)
    os.makedirs(a.out, exist_ok=True)
    with open(f"{a.out}/results.json", "w") as f:
        json.dump({"seed": a.seed, "nqueens": nq, "sudoku": sd, "eight_puzzle": ep}, f, indent=1)
    if a.charts:
        make_charts(nq, sd, ep, a.out)
        print(f"\nCharts saved in {a.out}/")


if __name__ == "__main__":
    main()
