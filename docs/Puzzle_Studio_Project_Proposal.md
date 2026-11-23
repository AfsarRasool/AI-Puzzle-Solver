## FAST — NATIONAL UNIVERSITY OF COMPUTER AND EMERGING SCIENCES

FAST School of Computing · Karachi Campus

AL-2002 Artificial Intelligence (Laboratory) · Fall 2026

## PROJECT PROPOSAL

Project Title: Puzzle Studio: Sudoku, N-Queens and the 8-Puzzle

Project Idea: Idea from the provided Project Ideas list.

Category: Part A — Game

[GitHub Repository URL: AfsarRasool/AI-Puzzle-Solver: An interactive AI-based puzzle solving system implementing search and constraint satisfaction techniques, including N-Queens, Sudoku, and 8-Puzzle.](https://github.com/AfsarRasool/AI-Puzzle-Solver)

Date of Submission:

## Group Information

| Name | Roll Number | Section | Role in the project |
| --- | --- | --- | --- |
| Abubakar | 24k-2046 | BCY-3A | Group leader; AI algorithms and integration |
| Afsar Rasool | 24k-2016 | BCY-3A | Puzzle interface and algorithm implementation |

## 1. Project Title and Summary

Puzzle Studio is an interactive application that lets users play Sudoku, N-Queens, and the 8-Puzzle manually or ask an AI solver to find a solution. It demonstrates how different artificial intelligence search techniques solve the same type of problem in different ways. Sudoku will compare basic backtracking with the MRV heuristic and forward checking, N-Queens will compare backtracking with min-conflicts hill climbing, and the 8-Puzzle will compare breadth-first search with A* using Manhattan distance. The application will animate the solver’s steps and provide controls for animation speed. It will also display statistics such as nodes explored and time taken, helping students understand both the solution and the efficiency of each algorithm.

## 2. Problem Statement and Motivation

Logic puzzles are useful for learning problem-solving, but solving them manually can take time, and the reasoning behind a solution may not be obvious to a beginner. Their difficulty comes from the large number of possible states and the constraints that must be satisfied. In Sudoku, each row, column, and 3×3 box must contain valid numbers without repetition. In N-Queens, no two queens may attack each other, which requires checking conflicts across rows, columns, and diagonals. In the 8-Puzzle, tiles must be moved into a target arrangement, and exploring every possible move can be inefficient. A simple brute-force approach may examine many unnecessary states. Puzzle Studio will make these challenges easier to understand by showing how search strategies choose states, backtrack, or use heuristics to guide the search. Comparing node counts and execution times on the same puzzle instances will show why algorithm choice matters. The project is worthwhile because it turns abstract AI concepts into a visual, measurable learning experience.

## 3. Problem Formulation

## 3.1 PEAS Description

| Component | Description for the project |
| --- | --- |
| Performance measure | Find a valid solution; minimize unnecessary node exploration and execution time where applicable; display correct steps. |
| Environment | A digital application containing Sudoku grids, N-Queens boards, and 8-Puzzle boards. |
| Actuators | Place numbers, place or move queens, move puzzle tiles, and update the displayed board during animation. |
| Sensors | Read the current board, empty cells, queen positions, tile |


positions, and user-selected algorithm or speed.

## 3.2 Environment and Agent Type

- Observability: Fully observable — the complete puzzle state is visible.

- Determinism: Deterministic — each valid action has a predictable result.

- Change over time: Static while the solver is not acting; the displayed state changes as moves are made.

- State and actions: Discrete.

- Agents: Single-agent.

- Agent type: Goal-based, using search and constraint-solving methods.

## 3.3 Problem Representation

| Element | Representation |
| --- | --- |
| State representation | Sudoku: grid values. N-Queens: queen positions on the board. 8-Puzzle: arrangement of eight numbered tiles and one blank. |
| Actions / moves | Assign a valid number, place or reposition a queen, or move a tile into the blank space. |
| Initial state | A selected or generated puzzle board. |
| Goal or terminal test | All puzzle rules are satisfied and the target state is reached. |
| Cost, utility, fitness or evaluation | Nodes expanded and time taken; for A*, path cost plus Manhattan-distance heuristic; for min-conflicts, number of queen conflicts. |

## 4. Proposed AI Approach

| # | Technique | Role in the project | Own code or library |
| --- | --- | --- | --- |
| 1 | Sudoku backtracking; MRV + forward checking | Compare basic constraint search with a strategy that chooses the most constrained empty cell and removes inconsistent candidate values. | Own Python code |
| 2 | N-Queens backtracking; min-conflicts hill climbing | Compare systematic search with local search that repeatedly reduces queen conflicts. | Own Python code |
| 3 | 8-Puzzle BFS; A* with Manhattan distance | Compare breadth-first search with heuristic-guided search on the same solvable boards. | Own Python code |

Baseline: Basic backtracking for Sudoku and N-Queens, and BFS for the 8-Puzzle. Each alternative will be tested on the same compatible puzzle instances.

## Why these techniques fit

These techniques fit because each puzzle has a clear state, legal actions, and a goal test. Backtracking builds a candidate solution and reverses a choice when it violates a constraint. For Sudoku, Minimum Remaining Values (MRV) selects the empty cell with the fewest legal values, while forward checking updates the remaining candidates after each assignment. For N-Queens, min-conflicts hill climbing starts with a board arrangement and moves a queen to reduce conflicts. BFS explores states by increasing depth, while A* prioritizes states using f(n) = g(n) + h(n), where g(n) is the number of moves so far and h(n) is the Manhattan distance: the sum of each tile’s horizontal and vertical distance from its goal position. All algorithms will be implemented in Python rather than relying on a search library.

## 4.1 Planned Class Design

- Puzzle: stores the puzzle type, current state, goal test, and legal-action checks.

- SudokuSolver: implements plain backtracking and MRV with forward checking.

- NQueensSolver: implements backtracking and min-conflicts hill climbing.


- EightPuzzleSolver: implements BFS, A*, and Manhattan-distance calculation.

- PuzzleUI: displays boards, accepts user actions, controls animation speed, and shows statistics.

Relationship: PuzzleUI interacts with the relevant solver; each solver reads a puzzle state and returns solution steps and performance statistics.

## 5. Scope

## In scope — features to deliver

| # | Feature | Why it is essential |
| --- | --- | --- |
| 1 | Manual play for Sudoku, N-Queens, and 8-Puzzle | Allows users to interact with all three puzzles. |
| 2 | AI solving for each puzzle using the listed algorithms | Demonstrates and compares the required AI techniques. |
| 3 | Step-by-step solution animation with speed control | Makes algorithm decisions easier to follow. |
| 4 | Node counter and execution-time measurement | Provides measurable performance comparisons. |
| 5 | Results table comparing algorithms on the same test cases | Summarizes the effect of different search strategies. |

## Out of scope

The project will not include online multiplayer, user accounts, cloud storage, a mobile application, machine- learning model training, or an unlimited puzzle-generation service. Puzzle generation will be limited to manageable test instances, and the interface will focus on demonstrating the selected algorithms rather than providing advanced game features.

## 6. Data or Environment Source

| Source name and URL | Generated / simulated puzzle instances; no external dataset required. |
| --- | --- |
| Type | Generated / simulated. |
| Access requirements | No key needed; runs locally. |
| Approximate size | A fixed collection of test puzzles for each game, with additional small instances generated for demonstrations. |
| Licence / terms of use | No external dataset or third-party puzzle data required; project code will follow course requirements. |
| Offline fallback | All test puzzles and algorithms will be stored locally, so the application will run without a network connection. |

## 7. Evaluation Plan

| What will be compared | Sudoku: backtracking vs. MRV + forward checking. N- Queens: backtracking vs. min-conflicts. 8-Puzzle: BFS vs. A*. |
| --- | --- |
| Metrics | Correctness, nodes explored/expanded, execution time, and solution length for the 8-Puzzle. |
| Baseline | Plain backtracking for Sudoku and N-Queens; BFS for the 8-Puzzle. |
| Test instances / test set | The same fixed, solvable test instances will be used for each pair of algorithms. Puzzle difficulty will be recorded. |
| Number of runs and seed | Run each compatible instance multiple times; use a fixed random seed for generated puzzles and min-conflicts where applicable. |
| Planned charts (at least three) | 1. Nodes explored by algorithm. 2. Execution time by algorithm. 3. 8-Puzzle solution length for BFS and A*. |

## 8. Division of Work

| Member | Modules / components owned | Approximate share |
| --- | --- | --- |
| Abubakar | Core AI logic: Sudoku backtracking/MRV, BFS and A*; performance counters; testing and integration. | 50% |


| Afsar Rasool | N-Queens algorithms; user interface and puzzle interaction; animation controls and results display. | 50% |
| --- | --- | --- |

## 9. Milestones and Timeline

| # | Milestone — demonstrable result | Target date / owner |
| --- | --- | --- |
| 1 | All three board representations, manual controls, and goal checks work. | Week 1 — Both members |
| 2 | Sudoku and N-Queens solvers return valid solutions on test cases. | Week 2 — Abubakar / Afsar Rasool |
| 3 | BFS and A* solve the selected 8- Puzzle tests; node and time counters work. | Week 3 — Abubakar |
| 4 | Animation, speed control, and comparison table are integrated. | Week 4 — Afsar Rasool / Both |
| 5 | Experiments complete; three charts, documentation, and repository cleanup finished. | Before submission — Both |

## 10. Expected Outcome and Risks

The final application will allow users to choose one of three puzzles, play it manually, or watch an AI algorithm solve it step by step. Users will be able to control the animation speed and view node counts and execution times in a comparison table. We expect MRV with forward checking to reduce unnecessary Sudoku search in many cases, min-conflicts to find N-Queens solutions efficiently on suitable boards, and A* with Manhattan distance to explore fewer states than BFS on many 8-Puzzle instances. Results will depend on puzzle difficulty. Two key risks are slow search on difficult instances and integration delays. We will limit test difficulty, use solvable fixed test boards, and integrate each solver with the interface as soon as it passes unit tests.

## For office use — Lab

Instructor: Miss Amna Aslam

Proposal status: Approved / Approved with changes / Revision required

Comments: __________________________________________________________

Signature and date: _________________________________________________
