from Board import Board
from State import State
from Astar import general_a_star, heuristic_chebyshev_sokoban
import time
import tracemalloc
import os

# ==========================================
# SOKOBAN PROBLEM CLASS
# ==========================================
class SokobanProblem:
    def __init__(self, board):
        self.board = board

    def is_goal(self, state):
        return set(state.boxes) == set(self.board.goals)

    def get_successors(self, state):
        from Astar import get_next_states
        return get_next_states(state, self.board)

def load_map(filename):
    walls, boxes = set(), set()
    goals = [] 
    player_pos = None

    if not os.path.exists(filename):
        return None, None, None, None

    with open(filename, "r", encoding="utf-8") as f:
        grid = [list(line.rstrip("\n")) for line in f]

    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            if char == '%':
                walls.add((x, y))
            elif char in ('C', 'D', '+'):
                goals.append((x, y))
            if char in ('A', '+'):
                player_pos = (x, y)
            if char in ('B', 'C'):
                boxes.add((x, y))

    return walls, goals, boxes, player_pos

# ==========================================
# EXPERIMENT EXECUTION FUNCTION
# ==========================================
def run_experiment(map_file):
    walls, goals, boxes, player_pos = load_map(map_file)
    
    if player_pos is None:
        print(f"Skipping {map_file}: File not found or invalid map.")
        return

    board = Board(walls, goals)
    start_state = State(player_pos, tuple(sorted(boxes)))
    problem = SokobanProblem(board)

    # 1. START MEASUREMENT
    tracemalloc.start() 
    start_time = time.perf_counter() 

    # 2. RUN ALGORITHM
    path = general_a_star(problem, start_state, heuristic_chebyshev_sokoban)

    # 3. STOP MEASUREMENT
    end_time = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 4. CALCULATE RESULTS
    execution_time = end_time - start_time
    peak_mem_mb = peak_mem / (1024 * 1024) 

    print("-" * 50)
    print(f"Experiment Report for: {map_file}")
    if path:
        print(f"Status: SOLUTION FOUND ({len(path) - 1} steps)")
    else:
        print("Status: NO SOLUTION FOUND")
        
    print(f"Time Complexity (Execution Time): {execution_time:.5f} seconds")
    print(f"Space Complexity (Peak Memory): {peak_mem_mb:.5f} MB")
    print("-" * 50)

if __name__ == "__main__":
    print("STARTING A* ALGORITHM EVALUATION EXPERIMENT...\n")
    
    # List of map files to test
    test_maps = [
        "input.txt",      
        "test_map_1.txt", 
        "test_map_2.txt",
        "test_map_3.txt"
    ]

    for map_file in test_maps:
        run_experiment(map_file)