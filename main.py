from Board import Board
from State import State
from Astar import general_a_star, heuristic_chebyshev_sokoban
import pygame
import sys
import ast
import os

from SelfPlay import run_self_play

CELL_SIZE = 50
FPS = 60
MOVE_DELAY = 300 

IMG_PATHS = {
    "menu_bg": "assets/menu_background.jpg", 
    "game_bg": "assets/background.png", #
    "wall": "assets/wall.png",
    "player": "assets/sato.png",
    "box": "assets/balls.png",
    "box_on_goal": "assets/ball.png"
}

GOAL_IMG_PATHS = [
    "assets/ngua.png", 
    "assets/pinky.png",
    "assets/eve.png",
    "assets/pkachu.png",
    "assets/Piplup.png",
]

class SokobanProblem:
    def __init__(self, board):
        self.board = board

    def is_goal(self, state):
        return set(state.boxes) == set(self.board.goals)

    def get_successors(self, state):
        from Astar import get_next_states
        return get_next_states(state, self.board)

def main_function():
    walls, goals, boxes, player_pos, _, _ = load_map()
    if player_pos is None:
        print("error: missing important component in the map!")
        return False
    
    board = Board(walls, goals)
    start_state = State(player_pos, tuple(sorted(boxes)))

    print("AI is solving...")
    problem = SokobanProblem(board)
    path = general_a_star(problem, start_state, heuristic_chebyshev_sokoban)

    if path:
        print(f"found a solution with {len(path) - 1} steps!")
        moves = []
        for i in range(1, len(path)):
            prev = path[i-1].player_pos
            curr = path[i].player_pos
            dx = curr[0] - prev[0]
            dy = curr[1] - prev[1]
            moves.append((dx, dy))

        with open("output.txt", "w", encoding="utf-8") as f:
            f.write("[\n")
            for i, move in enumerate(moves):
                f.write(f"    {move},\n" if i < len(moves)-1 else f"    {move}\n")
            f.write("]")
        print("solution saved in 'output.txt'")
        return True
    else:
        print("cant find solution!")
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write("[]")
        return False

def load_map(filename="input.txt"):
    walls, boxes = set(), set()
    goals = [] 
    player_pos = None
    max_x, max_y = 0, 0

    with open(filename, "r", encoding="utf-8") as f:
        grid = [list(line.rstrip("\n")) for line in f]

    for y, row in enumerate(grid):
        max_y = max(max_y, y)
        for x, char in enumerate(row):
            max_x = max(max_x, x)
            if char == '%':
                walls.add((x, y))
            elif char in ('C', 'D', '+'):
                goals.append((x, y))
            if char in ('A', '+'):
                player_pos = (x, y)
            if char in ('B', 'C'):
                boxes.add((x, y))

    return walls, goals, boxes, player_pos, max_x + 1, max_y + 1

def load_moves(filename="output.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            moves = ast.literal_eval(content)
            return moves
    except Exception as e:
        print(f"Không thể đọc file {filename}. Lỗi: {e}")
        return []

def load_and_scale_image(path, size, default_color=(0,0,0)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surface = pygame.Surface(size)
        surface.fill(default_color)
        return surface

def run_ai_animation(screen, walls, goals, boxes, player_pos, moves, images):
    clock = pygame.time.Clock()
    move_index = 0
    last_move_time = pygame.time.get_ticks()
    is_finished = False
    game_started = False
    running = True

    boxes = set(boxes)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_started = True

        current_time = pygame.time.get_ticks()
        if game_started and current_time - last_move_time > MOVE_DELAY and move_index < len(moves):
            dx, dy = moves[move_index]
            new_player_pos = (player_pos[0] + dx, player_pos[1] + dy)

            if new_player_pos in boxes:
                new_box_pos = (new_player_pos[0] + dx, new_player_pos[1] + dy)
                boxes.remove(new_player_pos)
                boxes.add(new_box_pos)

            player_pos = new_player_pos
            move_index += 1
            last_move_time = current_time

            if move_index == len(moves):
                is_finished = True

        screen.blit(images['bg'], (0, 0))

        for wx, wy in walls:
            screen.blit(images['wall'], (wx * CELL_SIZE, wy * CELL_SIZE))

        for i, (gx, gy) in enumerate(goals):
            goal_img = images['goals'][i % len(images['goals'])]
            screen.blit(goal_img, (gx * CELL_SIZE, gy * CELL_SIZE))

        for bx, by in boxes:
            if (bx, by) in goals:
                screen.blit(images['box_on_goal'], (bx * CELL_SIZE, by * CELL_SIZE))
            else:
                screen.blit(images['box'], (bx * CELL_SIZE, by * CELL_SIZE))

        px, py = player_pos
        screen.blit(images['player'], (px * CELL_SIZE, py * CELL_SIZE))

        if not game_started:
            font = pygame.font.SysFont(None, 48)
            text = font.render("Press SPACE to start AI", True, (168, 168, 168))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2))

        if is_finished:
            font = pygame.font.SysFont(None, 48)
            text = font.render("SOLVED!", True, (168, 168, 168))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 10))

        pygame.display.flip()
        clock.tick(FPS)

def main():
    pygame.init()
    
    walls, goals, boxes, player_pos, cols, rows = load_map()
    if player_pos is None:
        print("cannot find player position.")
        return

    width = cols * CELL_SIZE
    height = rows * CELL_SIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Sokoban Menu")

    images = {
        'menu_bg': load_and_scale_image(IMG_PATHS["menu_bg"], (width, height), (40, 44, 52)),
        'bg': load_and_scale_image(IMG_PATHS["game_bg"], (width, height), (40, 44, 52)),
        'wall': load_and_scale_image(IMG_PATHS["wall"], (CELL_SIZE, CELL_SIZE), (100, 100, 100)),
        'player': load_and_scale_image(IMG_PATHS["player"], (CELL_SIZE, CELL_SIZE), (231, 76, 60)),
        'box': load_and_scale_image(IMG_PATHS["box"], (CELL_SIZE, CELL_SIZE), (243, 156, 18)),
        'box_on_goal': load_and_scale_image(IMG_PATHS["box_on_goal"], (CELL_SIZE, CELL_SIZE), (155, 89, 182)),
        'goals': [load_and_scale_image(path, (CELL_SIZE, CELL_SIZE), (46, 204, 113)) for path in GOAL_IMG_PATHS]
    }
    
    if not images['goals']:
        images['goals'].append(pygame.Surface((CELL_SIZE, CELL_SIZE)))
        images['goals'][0].fill((46, 204, 113))

    font = pygame.font.SysFont(None, 40)
    
    while True:
        screen.blit(images['menu_bg'], (0, 0))
        
        opt1_text = font.render("1. Self Play", True, (0, 50, 100))
        opt2_text = font.render("2. Auto-Solver", True, (0, 100, 50))
        
        screen.blit(opt1_text, (width//2 - opt1_text.get_width()//2, height//2+150))
        screen.blit(opt2_text, (width//2 - opt2_text.get_width()//2, height//2 + 180))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    run_self_play(screen, walls, goals, set(boxes), player_pos, cols, rows, CELL_SIZE, FPS, images)
                elif event.key == pygame.K_2:
                    if main_function(): 
                        moves = load_moves()
                        run_ai_animation(screen, walls, goals, set(boxes), player_pos, moves, images)

if __name__ == "__main__":
    main()