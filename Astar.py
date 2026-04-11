import State
import heapq

directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

def is_deadlock(state, board):
    walls = board.walls
    goals = board.goals

    for box in state.boxes:
        x, y = box
        if box in goals:
            continue

        if (x-1, y) in walls and (x, y-1) in walls: return True
        if (x-1, y) in walls and (x, y+1) in walls: return True
        if (x+1, y) in walls and (x, y-1) in walls: return True
        if (x+1, y) in walls and (x, y+1) in walls: return True

        if (x-1, y) in walls or (x+1, y) in walls:
            has_goal_in_col = any(gx == x for gx, gy in goals)
            if not has_goal_in_col: return True

        if (x, y-1) in walls or (x, y+1) in walls:
            has_goal_in_row = any(gy == y for gx, gy in goals)
            if not has_goal_in_row: return True

    return False


def get_next_states(current_state, board):
    for dx, dy in directions:
        new_player_pos = (current_state.player_pos[0] + dx, current_state.player_pos[1] + dy)

        if new_player_pos in board.walls:
            continue

        if new_player_pos in current_state.boxes:
            new_box_pos = (new_player_pos[0] + dx, new_player_pos[1] + dy)
            if new_box_pos in board.walls or new_box_pos in current_state.boxes:
                continue

            new_boxes_set = set(current_state.boxes)
            new_boxes_set.remove(new_player_pos)
            new_boxes_set.add(new_box_pos)

            new_boxes_tuple = tuple(sorted(new_boxes_set))
            temp_state = State.State(new_player_pos, new_boxes_tuple, current_state.g + 1)

            if is_deadlock(temp_state, board):
                continue
            yield temp_state
        else:
            yield State.State(new_player_pos, current_state.boxes, current_state.g + 1)


def reconstruct_path(came_from, current_state):
    path = [current_state]
    while current_state in came_from:
        current_state = came_from[current_state]
        path.append(current_state)
    path.reverse()
    return path


# ====================== GENERAL A* (DÙNG CHUNG CHO TASK 1 VÀ TASK 2) ======================
def general_a_star(problem, start_state, heuristic_func):
    """
    A* GENERAL - DÙNG CHO CẢ TASK 1 (8-Puzzle) VÀ TASK 2 (Sokoban)
    """
    open_set = []
    counter = 0
    start_h = heuristic_func(start_state, problem)
    heapq.heappush(open_set, (start_h, counter, start_state))

    came_from = {}
    g_score = {start_state: 0}

    while open_set:
        _, _, current_state = heapq.heappop(open_set)

        if problem.is_goal(current_state):
            return reconstruct_path(came_from, current_state)

        for next_state in problem.get_successors(current_state):
            tentative_g_score = g_score[current_state] + 1

            if next_state not in g_score or tentative_g_score < g_score[next_state]:
                came_from[next_state] = current_state
                g_score[next_state] = tentative_g_score
                f_score = tentative_g_score + heuristic_func(next_state, problem)
                counter += 1
                heapq.heappush(open_set, (f_score, counter, next_state))

    return None


# ====================== 3 HEURISTIC (ĐÃ TÁCH RÕ RÀNG) ======================

# Heuristic cho Task 2 (Sokoban)
def heuristic_chebyshev_sokoban(state, problem):
    """Heuristic Task 2: Chebyshev Distance to Nearest Goal"""
    total = 0
    for box in state.boxes:
        distances = [max(abs(box[0] - g[0]), abs(box[1] - g[1])) for g in problem.board.goals]
        if distances:
            total += min(distances)
    return total


# Heuristic 1 cho Task 1 (8-Puzzle)
def heuristic_chebyshev_8puzzle(state, problem):
    """Heuristic 1 Task 1: Chebyshev"""
    total = 0
    goal = problem.goal
    for i in range(9):
        if state[i] == 0:
            continue
        x, y = divmod(i, 3)
        goal_pos = goal.index(state[i])
        gx, gy = divmod(goal_pos, 3)
        total += max(abs(x - gx), abs(y - gy))
    return total


# Heuristic 2 cho Task 1 (8-Puzzle)
def heuristic_misplaced_8puzzle(state, problem):
    """Heuristic 2 Task 1: Misplaced Tiles"""
    count = 0
    goal = problem.goal
    for i in range(9):
        if state[i] != 0 and state[i] != goal[i]:
            count += 1
    return count