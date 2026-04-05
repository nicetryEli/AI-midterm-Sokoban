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
        new_player_x = current_state.player_pos[0] + dx
        new_player_y = current_state.player_pos[1] + dy
        new_player_pos = (new_player_x, new_player_y)

        if new_player_pos in board.walls:
            continue

        if new_player_pos in current_state.boxes:
            new_box_x = new_player_x + dx
            new_box_y = new_player_y + dy
            new_box_pos = (new_box_x, new_box_y)
            
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


def heuristic(state, board):
    total_distance = 0
    for box in state.boxes:
        # Áp dụng công thức max(|x1 - x2|, |y1 - y2|)
        distances = [max(abs(box[0] - goal[0]), abs(box[1] - goal[1])) for goal in board.goals]
        
        # Chọn đích gần nhất theo Chebyshev để cộng vào tổng
        if distances: 
            total_distance += min(distances)
            
    return total_distance
def reconstruct_path(came_from, current_state):
    path = [current_state]
    while current_state in came_from:
        current_state = came_from[current_state]
        path.append(current_state)
    path.reverse()
    return path

def a_star(start_state, board):
    open_set = []
    counter = 0 

    start_h = heuristic(start_state, board)
    heapq.heappush(open_set, (start_h, counter, start_state))

    came_from = {}
    g_score = {start_state: 0}

    while open_set:
        current_f,_,current_state = heapq.heappop(open_set)

        if set(current_state.boxes) == set(board.goals):
            return reconstruct_path(came_from, current_state)
        
        for next_state in get_next_states(current_state, board):
            tentative_g_score = g_score[current_state] + 1

            if next_state not in g_score or tentative_g_score < g_score[next_state]:
                came_from[next_state] = current_state
                g_score[next_state] = tentative_g_score
                f_score = tentative_g_score + heuristic(next_state, board)
                counter += 1
                heapq.heappush(open_set, (f_score, counter, next_state))

    return None

