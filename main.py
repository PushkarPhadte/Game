import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (255, 0, 0)

# Game variables
gravity = 0.5
bird_movement = 0
score = 0
high_score = 0
game_active = False
paused = False
resuming = False
last_pipe_time = 0
first_launch = True

# Load assets 
# pygame.font.SysFont("Arial", 32)
font = pygame.font.Font(None, 32)
clock = pygame.time.Clock()

# Load bird image
bird_image = pygame.image.load("assets/BirdyMK.png").convert_alpha()
bird_image = pygame.transform.scale(bird_image, (40, 30))

# Initialize
pygame.mixer.init()

# Load flap sound
flap_sound = pygame.mixer.Sound("assets/MK.mp3")

# Load background music
pygame.mixer.music.load("assets/Mk_bg.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Loop indefinitely

# Bird
bird = pygame.Rect(100, HEIGHT // 2, 40, 30)

# Pipes
pipe_width = 70
pipe_gap = 150
pipes = []

# Clouds
clouds = []
cloud_timer = pygame.USEREVENT + 1
pygame.time.set_timer(cloud_timer, 3000)

# Track passed pipes
passed_pipes = []

# Pause button
pause_button = pygame.Rect(WIDTH - 50, 10, 40, 40)

# Start button
start_text = font.render("Start Game", True, WHITE)
start_button = pygame.Rect(WIDTH // 2 - start_text.get_width() // 2 - 20, HEIGHT // 2 - 25, start_text.get_width() + 40, 50)

def countdown():
    for i in range(3, 0, -1):
        draw_game_state()
        count_text = font.render(str(i), True, RED)
        screen.blit(count_text, (WIDTH // 2 - count_text.get_width() // 2, HEIGHT // 2))
        pygame.display.update()
        time.sleep(1)

def create_pipe():
    height = random.randint(100, 400)
    top_pipe = pygame.Rect(WIDTH, 0, pipe_width, height)
    bottom_pipe = pygame.Rect(WIDTH, height + pipe_gap, pipe_width, HEIGHT - height - pipe_gap)
    return top_pipe, bottom_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 3
    return [pipe for pipe in pipes if pipe.right > 0]

def check_collision(pipes):
    for pipe in pipes:
        if bird.colliderect(pipe):
            return False
    if bird.top <= 0 or bird.bottom >= HEIGHT:
        return False
    return True

def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, GREEN, pipe)

def update_score(pipes, score):
    global passed_pipes
    for pipe in pipes:
        if pipe.centerx < bird.centerx and pipe not in passed_pipes:
            score += 0.5  # Each pair counts as one point
            passed_pipes.append(pipe)
    return int(score)

def create_cloud():
    y_pos = random.randint(50, HEIGHT // 2)
    cloud = pygame.Rect(WIDTH, y_pos, 60, 30)
    return cloud

def move_clouds(clouds):
    for cloud in clouds:
        cloud.centerx -= 1
    return [cloud for cloud in clouds if cloud.right > 0]

def draw_clouds(clouds):
    for cloud in clouds:
        pygame.draw.ellipse(screen, WHITE, cloud)

def death_screen():
    screen.fill(BLUE)
    death_text = font.render("Game Over", True, RED)
    score_text = font.render(f"Score: {score}", True, BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
    restart_text = font.render("Press SPACE or Tap to Restart", True, BLACK)
    screen.blit(death_text, (WIDTH // 2 - death_text.get_width() // 2, HEIGHT // 3))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 40))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))
    pygame.display.update()

def draw_pause_button():
    if paused:
        pygame.draw.polygon(screen, BLACK, [(pause_button.x + 10, pause_button.y + 10), (pause_button.x + 30, pause_button.y + 20), (pause_button.x + 10, pause_button.y + 30)])
    else:
        pygame.draw.line(screen, BLACK, (pause_button.x + 10, pause_button.y + 10), (pause_button.x + 10, pause_button.y + 30), 5)
        pygame.draw.line(screen, BLACK, (pause_button.x + 25, pause_button.y + 10), (pause_button.x + 25, pause_button.y + 30), 5)

def draw_start_screen():
    screen.fill(BLUE)
    title_text = font.render("Flappy Bird", True, BLACK)
    pygame.draw.rect(screen, DARK_GREEN, start_button, border_radius=12)
    pygame.draw.rect(screen, GREEN, start_button.inflate(-10, -10), border_radius=12)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
    screen.blit(start_text, (start_button.x + 20, start_button.y + 10))
    pygame.display.update()

def draw_game_state():
    screen.fill(BLUE)
    draw_clouds(clouds)
    screen.blit(bird_image, bird)
    draw_pipes(pipes)
    score_text = font.render(f"Score: {score}", True, BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 50))
    draw_pause_button()

def reset_game():
    global bird, bird_movement, pipes, score, passed_pipes, game_active
    bird = pygame.Rect(100, HEIGHT // 2, 40, 30)
    bird_movement = 0
    pipes.clear()
    passed_pipes.clear()
    score = 0
    game_active = True

# Game loop
pipe_timer = pygame.USEREVENT
pygame.time.set_timer(pipe_timer, 1200)
running = True

while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if first_launch and start_button.collidepoint(event.pos):
                game_active = True
                first_launch = False
            elif pause_button.collidepoint(event.pos) and game_active:
                if paused:
                    pygame.mixer.music.unpause()
                    resuming = True
                    countdown()
                    resuming = False
                    paused = False
                    last_pipe_time = pygame.time.get_ticks()
                else:
                    pygame.mixer.music.pause()
                    paused = True
            elif game_active and not paused:
                bird_movement = -8
                flap_sound.play()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_active:
                    reset_game()
                elif not paused and not resuming:
                    bird_movement = -8
                    flap_sound.play()
        if event.type == pipe_timer and game_active and not paused:
            if current_time - last_pipe_time >= 1200:
                pipes.extend(create_pipe())
                last_pipe_time = current_time
        if event.type == cloud_timer and not paused:
            clouds.append(create_cloud())

    if first_launch:
        draw_start_screen()
    elif game_active:
        if not paused and not resuming:
            screen.fill(BLUE)
            clouds = move_clouds(clouds)
            draw_clouds(clouds)
            bird_movement += gravity
            bird.y += int(bird_movement)
            screen.blit(bird_image, bird)
            pipes = move_pipes(pipes)
            draw_pipes(pipes)
            score = update_score(pipes, score)
            if not check_collision(pipes):
                game_active = False
                paused = False
                high_score = max(high_score, score)
            score_text = font.render(f"Score: {score}", True, BLACK)
            high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
            screen.blit(score_text, (10, 10))
            screen.blit(high_score_text, (10, 50))
        elif paused:
            draw_game_state()
            pause_text = font.render("Paused", True, RED)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
        draw_pause_button()
    else:
        death_screen()

    pygame.display.update()
    clock.tick(60)