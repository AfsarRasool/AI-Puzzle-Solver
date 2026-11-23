"""
Puzzle Studio - AI Project
Single entry point.  Run:   python main.py
"""
import nqueen
import sudoku
import eight_puzzle
from utils import clear_screen, header, ask_menu, color, CYAN, BOLD


def main():
    while True:
        clear_screen()
        header("PUZZLE STUDIO  -  AI PROJECT")
        print(color("\n  N-Queens : Hill Climbing vs Backtracking", CYAN))
        print(color("  Sudoku   : Backtracking vs Forward Checking vs MRV", CYAN))
        print(color("  8-Puzzle : BFS vs A*", CYAN))
        choice = ask_menu("Main menu", ["N-Queens", "Sudoku", "8-Puzzle", "Exit"])
        if choice == 1:
            nqueen.run()
        elif choice == 2:
            sudoku.run()
        elif choice == 3:
            eight_puzzle.run()
        else:
            clear_screen()
            print("Goodbye!")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
