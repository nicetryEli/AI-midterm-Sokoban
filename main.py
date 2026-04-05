from Board import Board
from State import State
from Astar import a_star
import pygame
import sys
import ast

# ==========================================
# 1. CẤU HÌNH THÔNG SỐ CƠ BẢN
# ==========================================
CELL_SIZE = 50
FPS = 60
MOVE_DELAY = 300  # Thời gian chờ giữa mỗi bước đi (milliseconds)

# Màu sắc (R, G, B)
COLOR_BG = (40, 44, 52)         # Nền tối
COLOR_WALL = (100, 100, 100)    # Tường xám
COLOR_GOAL = (46, 204, 113)     # Đích màu xanh lá
COLOR_PLAYER = (231, 76, 60)    # Người chơi màu đỏ
COLOR_BOX = (243, 156, 18)      # Thùng màu cam
COLOR_BOX_ON_GOAL = (155, 89, 182) # Thùng đã vào đích màu tím

def main_function():
    # Dùng lại hàm load_map để tránh lặp code
    walls, goals, boxes, player_pos, _, _ = load_map()

    if player_pos is None:
        print("error: missing important component in the map!")
        return

    # Khởi tạo đối tượng từ các class đã import
    board = Board(walls, goals)
    start_state = State(player_pos, tuple(sorted(boxes)))

    print("solving...")
    path = a_star(start_state, board)

    # In ra kết quả
    if path:
        print(f"found the solution in {len(path) - 1} steps!")
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
                if i < len(moves) - 1:
                    f.write(f"{move},\n")
                else:
                    f.write(f"{move}\n")
            f.write("]")
                
        print("the solution has been saved in 'output.txt'.")    
    else:
        print("\n cannot find the solution!")
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write("[]")
# ==========================================
# 2. HÀM ĐỌC DỮ LIỆU TỪ FILE
# ==========================================
def load_map(filename="input.txt"):
    walls, goals, boxes = set(), set(), set()
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
                goals.add((x, y))
            if char in ('A', '+'):
                player_pos = (x, y)
            if char in ('B', 'C'):
                boxes.add((x, y))

    return walls, goals, boxes, player_pos, max_x + 1, max_y + 1

def load_moves(filename="output.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            # Dùng ast.literal_eval để chuyển chuỗi "[(1,0),...]" thành mảng Python an toàn
            moves = ast.literal_eval(content)
            return moves
    except Exception as e:
        print(f"Không thể đọc file {filename} hoặc file trống. Lỗi: {e}")
        return []

# ==========================================
# 3. VÒNG LẶP PYGAME CHÍNH
# ==========================================
def main():
    # Khởi tạo dữ liệu
    walls, goals, boxes, player_pos, cols, rows = load_map()
    moves = load_moves()

    if player_pos is None:
        print("Lỗi: Không tìm thấy nhân vật trên bản đồ.")
        return

    # Khởi tạo cửa sổ Pygame
    pygame.init()
    width = cols * CELL_SIZE
    height = rows * CELL_SIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Sokoban Auto-Solver Animation")
    clock = pygame.time.Clock()

    # Biến điều khiển
    move_index = 0
    last_move_time = pygame.time.get_ticks()
    is_finished = False
    game_started = False

    running = True
    while running:
        # 1. EVENT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Nhấn SPACE để bắt đầu
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_started = True

        # 2. UPDATE
        current_time = pygame.time.get_ticks()

        if game_started and current_time - last_move_time > MOVE_DELAY and move_index < len(moves):
            dx, dy = moves[move_index]

            new_player_pos = (player_pos[0] + dx, player_pos[1] + dy)

            # xử lý đẩy thùng
            if new_player_pos in boxes:
                new_box_pos = (new_player_pos[0] + dx, new_player_pos[1] + dy)
                boxes.remove(new_player_pos)
                boxes.add(new_box_pos)

            player_pos = new_player_pos
            move_index += 1
            last_move_time = current_time

            if move_index == len(moves):
                is_finished = True

        # 3. DRAW
        screen.fill(COLOR_BG)

        # Vẽ goal
        for gx, gy in goals:
            rect = pygame.Rect(gx * CELL_SIZE + 10, gy * CELL_SIZE + 10, CELL_SIZE - 20, CELL_SIZE - 20)
            pygame.draw.circle(screen, COLOR_GOAL, rect.center, 10)

        # Vẽ wall
        for wx, wy in walls:
            rect = pygame.Rect(wx * CELL_SIZE, wy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, COLOR_WALL, rect)
            pygame.draw.rect(screen, (50, 50, 50), rect, 2)

        # Vẽ box
        for bx, by in boxes:
            rect = pygame.Rect(bx * CELL_SIZE + 5, by * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10)
            if (bx, by) in goals:
                pygame.draw.rect(screen, COLOR_BOX_ON_GOAL, rect)
            else:
                pygame.draw.rect(screen, COLOR_BOX, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        # Vẽ player
        px, py = player_pos
        player_rect = pygame.Rect(px * CELL_SIZE + 5, py * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10)
        pygame.draw.ellipse(screen, COLOR_PLAYER, player_rect)

        # Màn hình chờ
        if not game_started:
            font = pygame.font.SysFont(None, 48)
            text = font.render("Press SPACE to start", True, (255, 255, 255))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2))

        # Hiện khi xong
        if is_finished:
            font = pygame.font.SysFont(None, 48)
            text = font.render("SOLVED!", True, (255, 255, 255))
            screen.blit(text, (width // 2 - text.get_width() // 2, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main_function()
    main()