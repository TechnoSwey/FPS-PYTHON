import pygame
import math
import numpy as np
from typing import List, Tuple, Optional

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
YELLOW = (255, 255, 0)
SEMI_TRANSPARENT = (100, 100, 100, 128)

MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

TILE_SIZE = 64
MAP_WIDTH = len(MAP[0])
MAP_HEIGHT = len(MAP)
MAX_DEPTH = 20
FPS = 60

class DisplayConfig:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.fov = math.pi / 3
        self.num_rays = self.width
        self.delta_angle = self.fov / self.num_rays
        self.is_portrait = False
        
    def update(self, width, height):
        self.width = width
        self.height = height
        self.is_portrait = height > width
        self.num_rays = min(width, 800)
        self.delta_angle = self.fov / self.num_rays

class TouchControl:
    def __init__(self):
        self.left_stick_active = False
        self.left_stick_pos = (0, 0)
        self.left_stick_delta = (0, 0)
        self.left_touch_id = None
        
        self.right_stick_active = False
        self.right_stick_pos = (0, 0)
        self.right_stick_delta = (0, 0)
        self.right_touch_id = None
        
        self.shoot_button_pressed = False
        
    def update(self, events, display):
        self.shoot_button_pressed = False
        
        for event in events:
            if event.type == pygame.FINGERDOWN:
                x = event.x * display.width
                y = event.y * display.height
                
                if x < display.width / 2:
                    self.left_stick_active = True
                    self.left_stick_pos = (x, y)
                    self.left_touch_id = event.finger_id
                else:
                    if self.is_shoot_button(x, y, display):
                        self.shoot_button_pressed = True
                    else:
                        self.right_stick_active = True
                        self.right_stick_pos = (x, y)
                        self.right_touch_id = event.finger_id
                        
            elif event.type == pygame.FINGERUP:
                if event.finger_id == self.left_touch_id:
                    self.left_stick_active = False
                    self.left_stick_delta = (0, 0)
                    self.left_touch_id = None
                elif event.finger_id == self.right_touch_id:
                    self.right_stick_active = False
                    self.right_stick_delta = (0, 0)
                    self.right_touch_id = None
                    
            elif event.type == pygame.FINGERMOTION:
                x = event.x * display.width
                y = event.y * display.height
                
                if event.finger_id == self.left_touch_id and self.left_stick_active:
                    dx = x - self.left_stick_pos[0]
                    dy = y - self.left_stick_pos[1]
                    max_dist = 50
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist > max_dist:
                        dx = dx / dist * max_dist
                        dy = dy / dist * max_dist
                    self.left_stick_delta = (dx, dy)
                    
                elif event.finger_id == self.right_touch_id and self.right_stick_active:
                    dx = x - self.right_stick_pos[0]
                    dy = y - self.right_stick_pos[1]
                    max_dist = 50
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist > max_dist:
                        dx = dx / dist * max_dist
                        dy = dy / dist * max_dist
                    self.right_stick_delta = (dx, dy)
    
    def is_shoot_button(self, x, y, display):
        button_size = 80
        button_x = display.width - button_size - 20
        button_y = display.height - button_size - 20
        return button_x <= x <= button_x + button_size and button_y <= y <= button_y + button_size
    
    def draw(self, screen, display):
        if self.left_stick_active:
            center = self.left_stick_pos
            pygame.draw.circle(screen, (100, 100, 100, 100), center, 60, 2)
            stick_pos = (center[0] + self.left_stick_delta[0], 
                        center[1] + self.left_stick_delta[1])
            pygame.draw.circle(screen, (200, 200, 200, 150), stick_pos, 30)
        else:
            center = (80, display.height - 80)
            pygame.draw.circle(screen, (80, 80, 80, 80), center, 60, 2)
            
        if self.right_stick_active:
            center = self.right_stick_pos
            pygame.draw.circle(screen, (100, 100, 100, 100), center, 60, 2)
            stick_pos = (center[0] + self.right_stick_delta[0], 
                        center[1] + self.right_stick_delta[1])
            pygame.draw.circle(screen, (200, 200, 200, 150), stick_pos, 30)
        
        button_size = 80
        button_x = display.width - button_size - 20
        button_y = display.height - button_size - 20
        color = RED if self.shoot_button_pressed else (150, 0, 0)
        pygame.draw.circle(screen, color, 
                          (button_x + button_size // 2, button_y + button_size // 2), 
                          button_size // 2)
        font = pygame.font.Font(None, 36)
        text = font.render("FIRE", True, WHITE)
        text_rect = text.get_rect(center=(button_x + button_size // 2, button_y + button_size // 2))
        screen.blit(text, text_rect)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.health = 100
        self.ammo = 100
        self.speed = 0.05
        self.rotation_speed = 0.03
        
    def move(self, keys, enemies, touch_control=None):
        new_x, new_y = self.x, self.y
        
        move_vector = [0.0, 0.0]
        
        if keys[pygame.K_w]:
            move_vector[0] += math.cos(self.angle)
            move_vector[1] += math.sin(self.angle)
        if keys[pygame.K_s]:
            move_vector[0] -= math.cos(self.angle)
            move_vector[1] -= math.sin(self.angle)
        if keys[pygame.K_a]:
            move_vector[0] += math.cos(self.angle - math.pi/2)
            move_vector[1] += math.sin(self.angle - math.pi/2)
        if keys[pygame.K_d]:
            move_vector[0] += math.cos(self.angle + math.pi/2)
            move_vector[1] += math.sin(self.angle + math.pi/2)
        
        if touch_control and touch_control.left_stick_active:
            dx, dy = touch_control.left_stick_delta
            length = math.sqrt(dx**2 + dy**2)
            if length > 0:
                norm_dx = dx / length
                norm_dy = dy / length
                move_vector[0] += norm_dx
                move_vector[1] += norm_dy
        
        if move_vector[0] != 0 or move_vector[1] != 0:
            new_x += move_vector[0] * self.speed
            new_y += move_vector[1] * self.speed
            
        map_x = int(new_x)
        map_y = int(new_y)
        
        if 0 <= map_x < MAP_WIDTH and 0 <= map_y < MAP_HEIGHT:
            if MAP[map_y][map_x] == 0:
                collision = False
                for enemy in enemies:
                    if enemy.alive:
                        dist = math.sqrt((new_x - enemy.x)**2 + (new_y - enemy.y)**2)
                        if dist < 0.3:
                            collision = True
                            break
                if not collision:
                    self.x = new_x
                    self.y = new_y
    
    def rotate(self, mouse_dx=0, touch_control=None):
        if mouse_dx != 0:
            self.angle += mouse_dx * self.rotation_speed
        
        if touch_control and touch_control.right_stick_active:
            dx = touch_control.right_stick_delta[0]
            self.angle += dx * 0.001
        
        self.angle %= 2 * math.pi

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 50
        self.alive = True
        self.speed = 0.02
        self.damage = 10
        self.attack_cooldown = 0
        
    def move_towards_player(self, player, enemies):
        if not self.alive:
            return
            
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0.3:
            new_x = self.x + (dx / dist) * self.speed
            new_y = self.y + (dy / dist) * self.speed
            
            map_x = int(new_x)
            map_y = int(new_y)
            
            if 0 <= map_x < MAP_WIDTH and 0 <= map_y < MAP_HEIGHT:
                if MAP[map_y][map_x] == 0:
                    collision = False
                    for other_enemy in enemies:
                        if other_enemy != self and other_enemy.alive:
                            other_dist = math.sqrt((new_x - other_enemy.x)**2 + (new_y - other_enemy.y)**2)
                            if other_dist < 0.3:
                                collision = True
                                break
                    if not collision:
                        self.x = new_x
                        self.y = new_y
        else:
            if self.attack_cooldown <= 0:
                player.health -= self.damage
                self.attack_cooldown = 60
                
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False

def cast_ray(player, angle, display):
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    
    for depth in range(1, int(MAX_DEPTH * TILE_SIZE)):
        x = player.x + depth * cos_a / TILE_SIZE
        y = player.y + depth * sin_a / TILE_SIZE
        
        map_x = int(x)
        map_y = int(y)
        
        if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
            return MAX_DEPTH, None
            
        if MAP[map_y][map_x] == 1:
            return depth / TILE_SIZE, (map_x, map_y)
    
    return MAX_DEPTH, None

def render_3d(screen, player, enemies, display):
    screen.fill(BLACK)
    
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, display.width, display.height // 2))
    pygame.draw.rect(screen, GRAY, (0, display.height // 2, display.width, display.height // 2))
    
    ray_angle = player.angle - display.fov / 2
    
    for ray in range(display.num_rays):
        depth, wall_pos = cast_ray(player, ray_angle, display)
        
        depth *= math.cos(player.angle - ray_angle)
        
        if depth < 0.1:
            depth = 0.1
            
        wall_height = min(int(TILE_SIZE * display.height / (depth * TILE_SIZE)), display.height * 2)
        
        brightness = max(0, min(255, 255 - int(depth * 25)))
        color = (brightness, brightness // 2, brightness // 2)
        
        ray_width = max(1, display.width // display.num_rays)
        pygame.draw.rect(screen, color, 
                        (ray * (display.width // display.num_rays), 
                         (display.height - wall_height) // 2, 
                         ray_width + 1, 
                         wall_height))
        
        ray_angle += display.delta_angle
    
    enemy_distances = []
    for enemy in enemies:
        if enemy.alive:
            dx = enemy.x - player.x
            dy = enemy.y - player.y
            distance = math.sqrt(dx**2 + dy**2)
            angle = math.atan2(dy, dx) - player.angle
            
            while angle < -math.pi:
                angle += 2 * math.pi
            while angle > math.pi:
                angle -= 2 * math.pi
                
            if abs(angle) < display.fov / 2 + 0.5:
                enemy_distances.append((distance, enemy, angle))
    
    enemy_distances.sort(reverse=True)
    
    for distance, enemy, angle in enemy_distances:
        screen_x = (display.fov / 2 + angle) / display.fov * display.width
        
        if distance < 0.1:
            distance = 0.1
            
        enemy_height = min(int(TILE_SIZE * display.height / (distance * TILE_SIZE)), display.height)
        enemy_width = enemy_height
        
        enemy_x = int(screen_x - enemy_width // 2)
        enemy_y = int((display.height - enemy_height) // 2)
        
        brightness = max(0, min(255, 255 - int(distance * 30)))
        enemy_color = (brightness, 0, 0)
        
        pygame.draw.rect(screen, enemy_color, 
                        (enemy_x, enemy_y, enemy_width, enemy_height))
        
        head_size = enemy_height // 4
        pygame.draw.circle(screen, (brightness, brightness // 2, 0), 
                          (int(screen_x), enemy_y + head_size), 
                          head_size)

def draw_minimap(screen, player, enemies, display):
    if display.is_portrait:
        minimap_size = min(display.width - 20, 120)
        minimap_x = (display.width - minimap_size) // 2
        minimap_y = 10
    else:
        minimap_size = 150
        minimap_x = display.width - minimap_size - 10
        minimap_y = 10
    
    minimap_scale = minimap_size / max(MAP_WIDTH, MAP_HEIGHT)
    
    pygame.draw.rect(screen, BLACK, (minimap_x - 2, minimap_y - 2, minimap_size + 4, minimap_size + 4))
    
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if MAP[y][x] == 1:
                pygame.draw.rect(screen, WHITE, 
                               (minimap_x + x * minimap_scale, 
                                minimap_y + y * minimap_scale, 
                                minimap_scale, minimap_scale))
    
    player_minimap_x = minimap_x + player.x * minimap_scale
    player_minimap_y = minimap_y + player.y * minimap_scale
    pygame.draw.circle(screen, GREEN, 
                      (int(player_minimap_x), int(player_minimap_y)), 3)
    
    line_length = 10
    end_x = player_minimap_x + math.cos(player.angle) * line_length
    end_y = player_minimap_y + math.sin(player.angle) * line_length
    pygame.draw.line(screen, GREEN, 
                    (player_minimap_x, player_minimap_y), 
                    (end_x, end_y), 2)
    
    for enemy in enemies:
        if enemy.alive:
            enemy_x = minimap_x + enemy.x * minimap_scale
            enemy_y = minimap_y + enemy.y * minimap_scale
            pygame.draw.circle(screen, RED, (int(enemy_x), int(enemy_y)), 2)

def draw_hud(screen, player, enemies, display):
    font_size = min(36, display.width // 20)
    small_font_size = min(24, display.width // 30)
    font = pygame.font.Font(None, font_size)
    small_font = pygame.font.Font(None, small_font_size)
    
    if display.is_portrait:
        y_offset = display.height - 150
        health_text = font.render(f"HP: {player.health}", True, GREEN if player.health > 30 else RED)
        screen.blit(health_text, (10, y_offset))
        
        ammo_text = font.render(f"Ammo: {player.ammo}", True, YELLOW)
        screen.blit(ammo_text, (10, y_offset + 40))
        
        enemies_alive = sum(1 for e in enemies if e.alive)
        enemy_text = small_font.render(f"Enemies: {enemies_alive}", True, WHITE)
        screen.blit(enemy_text, (10, y_offset + 80))
    else:
        health_text = font.render(f"HP: {player.health}", True, GREEN if player.health > 30 else RED)
        screen.blit(health_text, (10, 10))
        
        ammo_text = font.render(f"Ammo: {player.ammo}", True, YELLOW)
        screen.blit(ammo_text, (10, 50))
        
        enemies_alive = sum(1 for e in enemies if e.alive)
        enemy_text = small_font.render(f"Enemies: {enemies_alive}", True, WHITE)
        screen.blit(enemy_text, (10, 90))
    
    crosshair_size = 10
    pygame.draw.rect(screen, WHITE, 
                    (display.width // 2 - 2, display.height // 2 - crosshair_size, 4, crosshair_size * 2))
    pygame.draw.rect(screen, WHITE, 
                    (display.width // 2 - crosshair_size, display.height // 2 - 2, crosshair_size * 2, 4))

def has_line_of_sight(player, enemy):
    dx = enemy.x - player.x
    dy = enemy.y - player.y
    distance = math.sqrt(dx**2 + dy**2)
    
    steps = int(distance * TILE_SIZE)
    
    for i in range(1, steps):
        t = i / steps
        check_x = player.x + dx * t
        check_y = player.y + dy * t
        
        map_x = int(check_x)
        map_y = int(check_y)
        
        if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
            return False
            
        if MAP[map_y][map_x] == 1:
            return False
    
    return True

def shoot(player, enemies):
    if player.ammo <= 0:
        return False
        
    player.ammo -= 1
    
    closest_enemy = None
    closest_distance = float('inf')
    
    for enemy in enemies:
        if not enemy.alive:
            continue
            
        dx = enemy.x - player.x
        dy = enemy.y - player.y
        distance = math.sqrt(dx**2 + dy**2)
        
        angle_to_enemy = math.atan2(dy, dx)
        angle_diff = angle_to_enemy - player.angle
        
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        
        if abs(angle_diff) < 0.1 and distance < closest_distance:
            if has_line_of_sight(player, enemy):
                closest_distance = distance
                closest_enemy = enemy
    
    if closest_enemy and closest_distance < 10:
        closest_enemy.take_damage(25)
        return True
    
    return False

def main():
    display = DisplayConfig()
    screen = pygame.display.set_mode((display.width, display.height), pygame.RESIZABLE)
    pygame.display.set_caption("FPS - Mobile Optimized")
    clock = pygame.time.Clock()
    
    player = Player(1.5, 1.5)
    
    enemies = [
        Enemy(8.5, 8.5),
        Enemy(5.5, 3.5),
        Enemy(3.5, 7.5),
        Enemy(7.5, 5.5),
        Enemy(2.5, 5.5),
    ]
    
    touch_control = TouchControl()
    
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    running = True
    game_over = False
    victory = False
    
    while running:
        clock.tick(FPS)
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and not game_over:
                    shoot(player, enemies)
            elif event.type == pygame.MOUSEMOTION and not game_over:
                mouse_dx = event.rel[0]
                player.rotate(mouse_dx=mouse_dx)
            elif event.type == pygame.VIDEORESIZE:
                display.update(event.w, event.h)
                screen = pygame.display.set_mode((display.width, display.height), pygame.RESIZABLE)
        
        touch_control.update(events, display)
        
        if touch_control.shoot_button_pressed and not game_over:
            shoot(player, enemies)
        
        if not game_over and not victory:
            keys = pygame.key.get_pressed()
            player.move(keys, enemies, touch_control)
            player.rotate(touch_control=touch_control)
            
            for enemy in enemies:
                enemy.move_towards_player(player, enemies)
            
            if player.health <= 0:
                game_over = True
            
            enemies_alive = sum(1 for e in enemies if e.alive)
            if enemies_alive == 0:
                victory = True
        
        render_3d(screen, player, enemies, display)
        draw_minimap(screen, player, enemies, display)
        draw_hud(screen, player, enemies, display)
        touch_control.draw(screen, display)
        
        if game_over:
            font_size = min(72, display.width // 10)
            font = pygame.font.Font(None, font_size)
            text = font.render("GAME OVER", True, RED)
            text_rect = text.get_rect(center=(display.width // 2, display.height // 2))
            screen.blit(text, text_rect)
            
            small_font_size = min(36, display.width // 20)
            small_font = pygame.font.Font(None, small_font_size)
            restart_text = small_font.render("Press ESC to exit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(display.width // 2, display.height // 2 + 60))
            screen.blit(restart_text, restart_rect)
        
        if victory:
            font_size = min(72, display.width // 10)
            font = pygame.font.Font(None, font_size)
            text = font.render("VICTORY!", True, GREEN)
            text_rect = text.get_rect(center=(display.width // 2, display.height // 2))
            screen.blit(text, text_rect)
            
            small_font_size = min(36, display.width // 20)
            small_font = pygame.font.Font(None, small_font_size)
            restart_text = small_font.render("Press ESC to exit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(display.width // 2, display.height // 2 + 60))
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
