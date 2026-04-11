import pygame
import sys

def run_self_play(screen, walls, goals, boxes, player_pos, cols, rows, CELL_SIZE, FPS, images):
    clock = pygame.time.Clock()
    running = True
    is_finished = False
    
    def check_win(current_boxes):
        return set(current_boxes) == set(goals)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN and not is_finished:
                dx, dy = 0, 0
                if event.key in (pygame.K_UP, pygame.K_w):
                    dy = -1
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    dy = 1
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    dx = -1
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    dx = 1
                
                if dx != 0 or dy != 0:
                    new_player_pos = (player_pos[0] + dx, player_pos[1] + dy)
                    
                    if new_player_pos in walls:
                        continue
                        
                    if new_player_pos in boxes:
                        new_box_pos = (new_player_pos[0] + dx, new_player_pos[1] + dy)
                        if new_box_pos in walls or new_box_pos in boxes:
                            continue
                        
                        boxes.remove(new_player_pos)
                        boxes.add(new_box_pos)
                    
                    player_pos = new_player_pos
                    
                    if check_win(boxes):
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

        if is_finished:
            font = pygame.font.SysFont(None, 48)
            text = font.render("YOU WIN!", True, (255, 255, 255))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 10))

        pygame.display.flip()
        clock.tick(FPS)