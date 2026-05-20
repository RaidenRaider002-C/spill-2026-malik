import pygame
import random
import math

pygame.init()

# =========================
# SETTINGS
# =========================
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Survival")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BRIGHT_RED = (220, 20, 60)
GREEN = (50, 205, 50)
BLACK = (15, 15, 25)
GOLD = (255, 215, 0)
GRAY = (50, 50, 50)
CYAN = (0, 255, 255)

# Fonts
font_small = pygame.font.SysFont("Segoe UI", 24, bold=True)
font_large = pygame.font.SysFont("Segoe UI", 72, bold=True)

MAX_WAVE = 20
BOSS_WAVE = MAX_WAVE + 1

# =========================
# MENU
# =========================
game_started = False

start_button = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 40, 240, 60)
quit_button = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 120, 240, 60)

def draw_menu():
    screen.fill(BLACK)

    # Background grid
    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, (30, 30, 40), (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, (30, 30, 40), (0, y), (WIDTH, y))

    title = font_large.render("WAVE SURVIVAL", True, GOLD)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))

    subtitle = font_small.render(
        "Kill bugs. Survive waves. Upgrade gear.",
        True,
        WHITE
    )
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 220))

    # START BUTTON
    pygame.draw.rect(screen, GREEN, start_button, border_radius=12)

    start_txt = font_small.render("START GAME", True, BLACK)

    screen.blit(
        start_txt,
        (
            start_button.centerx - start_txt.get_width()//2,
            start_button.centery - start_txt.get_height()//2
        )
    )

    # QUIT BUTTON
    pygame.draw.rect(screen, BRIGHT_RED, quit_button, border_radius=12)

    quit_txt = font_small.render("QUIT", True, WHITE)

    screen.blit(
        quit_txt,
        (
            quit_button.centerx - quit_txt.get_width()//2,
            quit_button.centery - quit_txt.get_height()//2
        )
    )

# =========================
# LOAD IMAGES
# =========================
def load_image(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill(GREEN if "guy" in path else BRIGHT_RED)
        return surf

player_image = load_image("guy with spray.png", (50, 50))
base_enemy_image = load_image("bugs.png", (1000, 1000)) # Skaleres per fiende

# =========================
# PARTICLES
# =========================
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.lifetime = 25
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, surface, offset=(0, 0)):
        if self.lifetime > 0:
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.x + offset[0]), int(self.y + offset[1])),
                self.size
            )

# =========================
# PLAYER
# =========================
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = 40
        self.speed = 5.5
        self.hp = 100
        self.max_hp = 100
        self.coins = 100
        self.damage = 30
        self.score = 0
        self.shoot_delay = 400
        self.last_shot = 0
        self.shake_intensity = 0

    def move(self, keys):
        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        if dx != 0 and dy != 0:
            factor = self.speed / math.sqrt(2)
            self.x += dx * factor
            self.y += dy * factor
        else:
            self.x += dx * self.speed
            self.y += dy * self.speed

        self.x = max(0, min(WIDTH - self.size, self.x))
        self.y = max(0, min(HEIGHT - self.size, self.y))

    def draw(self, offset=(0, 0)):
        draw_x = self.x + offset[0]
        draw_y = self.y + offset[1]

        pygame.draw.rect(
            screen,
            WHITE,
            (draw_x - 2, draw_y - 2, self.size + 4, self.size + 4),
            2
        )

        screen.blit(player_image, (draw_x, draw_y))

        # HP BAR
        pygame.draw.rect(screen, GRAY, (20, 20, 200, 20))

        hp_width = 200 * (max(0, self.hp) / self.max_hp)

        pygame.draw.rect(screen, BRIGHT_RED, (20, 20, hp_width, 20))
        pygame.draw.rect(screen, WHITE, (20, 20, 200, 20), 2)

# =========================
# BULLET
# =========================
class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y

        angle = math.atan2(target_y - y, target_x - x)

        self.dx = math.cos(angle) * 14

        self.dy = math.sin(angle) * 14

        self.size = 7

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, offset=(0, 0)):
        pygame.draw.circle(
            screen,
            GOLD,
            (int(self.x + offset[0]), int(self.y + offset[1])),
            self.size
        )

# =========================
# ENEMY
# =========================
class Enemy:
    def __init__(self, wave, is_boss=False):
        side = random.randint(0, 3)

        if side == 0:
            self.x, self.y = random.randint(0, WIDTH), -50
        elif side == 1:
            self.x, self.y = random.randint(0, WIDTH), HEIGHT + 50
        elif side == 2:
            self.x, self.y = -50, random.randint(0, HEIGHT)
        else:
            self.x, self.y = WIDTH + 50, random.randint(0, HEIGHT)

        self.is_boss = is_boss

        if self.is_boss:
            # Make the boss much tougher and slightly faster
            self.speed = 5.0
            self.max_hp = 2000 + (wave * 100)
            self.size = 200
        else:
            self.speed = 1.4 + (wave * 0.2)
            self.max_hp = 20 + (wave * 10)
            self.size = 50 + min(wave, 10)
        
        self.hp = self.max_hp

        self.image = pygame.transform.scale(
            base_enemy_image,
            (self.size, self.size)
        )

    def update(self, player):
        angle = math.atan2(
            (player.y + player.size/2) - self.y,
            (player.x + player.size/2) - self.x
        )

        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def draw(self, offset=(0, 0)):
        draw_x = self.x + offset[0]
        draw_y = self.y + offset[1]

        screen.blit(self.image, (draw_x, draw_y))

        if self.is_boss:
            label = font_small.render("BOSS", True, GOLD)
            screen.blit(
                label,
                (draw_x + self.size//2 - label.get_width()//2, draw_y - 30)
            )
            bar_y = draw_y - 18
            bar_height = 8
            hp_color = BRIGHT_RED
        else:
            bar_y = draw_y - 10
            bar_height = 5
            hp_color = GREEN

        hp_pct = max(0, self.hp / self.max_hp)

        pygame.draw.rect(
            screen,
            GRAY,
            (draw_x, bar_y, self.size, bar_height)
        )

        pygame.draw.rect(
            screen,
            hp_color,
            (draw_x, bar_y, self.size * hp_pct, bar_height)
        )

# =========================
# GAME FUNCTIONS
# =========================
def spawn_wave():
    global enemies

    if wave == BOSS_WAVE:
        enemies = [Enemy(wave, is_boss=True)]
    else:
        num_enemies = 5 + (wave * 4)
        enemies = [Enemy(wave) for _ in range(num_enemies)]

def reset_game():
    global player
    global bullets
    global enemies
    global particles
    global wave
    global show_shop
    global game_over
    global game_won

    player = Player()

    bullets = []
    enemies = []
    particles = []

    wave = 21

    show_shop = False
    game_over = False
    game_won = False

    spawn_wave()

# =========================
# START GAME
# =========================
reset_game()

button_rect = pygame.Rect(
    WIDTH//2 - 100,
    HEIGHT//2 + 80,
    200,
    50
)

running = True

while running:

    clock.tick(60)

    # =========================
    # MENU
    # =========================
    if not game_started:

        draw_menu()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if start_button.collidepoint(event.pos):
                    reset_game()
                    game_started = True

                if quit_button.collidepoint(event.pos):
                    running = False

        pygame.display.flip()
        continue

    # =========================
    # GAME
    # =========================
    offset_x = 0
    offset_y = 0

    if player.shake_intensity > 0:
        offset_x = random.randint(
            -player.shake_intensity,
            player.shake_intensity
        )

        offset_y = random.randint(
            -player.shake_intensity,
            player.shake_intensity
        )

        player.shake_intensity -= 1
    
    screen.fill(BLACK)

    # EVENTS
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_b and not (game_over or game_won):
                show_shop = not show_shop

            if show_shop:

                if event.key == pygame.K_1 and player.coins >= 25:
                    player.max_hp += 25
                    player.hp = player.max_hp
                    player.coins -= 25

                if event.key == pygame.K_2 and player.coins >= 30:
                    player.damage += 10
                    player.coins -= 30

                if event.key == pygame.K_3 and player.coins >= 40:
                    player.speed += 0.8
                    player.coins -= 40

                if event.key == pygame.K_4 and player.coins >= 50:
                    player.shoot_delay = max(
                        100,
                        player.shoot_delay - 40
                    )

                    player.coins -= 50

        if event.type == pygame.MOUSEBUTTONDOWN:

            if (game_over or game_won):

                if button_rect.collidepoint(event.pos):
                    game_started = False

    # =========================
    # GAMEPLAY
    # =========================
    if not show_shop and not game_over and not game_won:

        keys = pygame.key.get_pressed()

        player.move(keys)

        # SHOOTING
        if pygame.mouse.get_pressed()[0]:

            now = pygame.time.get_ticks()

            if now - player.last_shot > player.shoot_delay:

                mx, my = pygame.mouse.get_pos()

                bullets.append(
                    Bullet(
                        player.x + player.size//2,
                        player.y + player.size//2,
                        mx,
                        my
                    )
                )

                player.last_shot = now

        # BULLETS
        for b in bullets[:]:

            b.update()

            if not (0 <= b.x <= WIDTH and 0 <= b.y <= HEIGHT):
                bullets.remove(b)

        # PARTICLES
        for p in particles[:]:

            p.update()

            if p.lifetime <= 0:
                particles.remove(p)

        # ENEMIES
        for e in enemies[:]:

            e.update(player)

            # PLAYER HIT
            if pygame.Rect(
                e.x,
                e.y,
                e.size,
                e.size
            ).colliderect(
                pygame.Rect(
                    player.x,
                    player.y,
                    player.size,
                    player.size
                )
            ):

                player.hp -= 0.6
                player.shake_intensity = 8

                if player.hp <= 0:
                    game_over = True

            # BULLET HIT
            for b in bullets[:]:

                if pygame.Rect(
                    e.x,
                    e.y,
                    e.size,
                    e.size
                ).collidepoint(b.x, b.y):

                    e.hp -= player.damage

                    if b in bullets:
                        bullets.remove(b)

                    if e.hp <= 0:

                        for _ in range(10):

                            particles.append(
                                Particle(
                                    e.x + e.size/2,
                                    e.y + e.size/2,
                                    BRIGHT_RED
                                )
                            )

                        if e in enemies:
                            enemies.remove(e)

                        player.coins += 4
                        player.score += 20

                    break

        # NEXT WAVE
        if not enemies:

            wave += 1

            if wave > BOSS_WAVE:
                game_won = True
            else:
                spawn_wave()

    # =========================
    # BACKGROUND
    # =========================
    for x in range(0, WIDTH + 50, 50):

        pygame.draw.line(
            screen,
            (30, 30, 40),
            (x + offset_x, 0),
            (x + offset_x, HEIGHT)
        )

    for y in range(0, HEIGHT + 50, 50):

        pygame.draw.line(
            screen,
            (30, 30, 40),
            (0, y + offset_y),
            (WIDTH, y + offset_y)
        )

    # =========================
    # DRAW GAME
    # =========================
    if not game_over and not game_won:

        current_offset = (offset_x, offset_y)

        mx, my = pygame.mouse.get_pos()

        pygame.draw.line(
            screen,
            (40, 40, 40),
            (
                player.x + player.size//2 + offset_x,
                player.y + player.size//2 + offset_y
            ),
            (mx, my),
            1
        )

        for p in particles:
            p.draw(screen, current_offset)

        for b in bullets:
            b.draw(current_offset)

        for e in enemies:
            e.draw(current_offset)

        player.draw(current_offset)

        screen.blit(
            font_small.render(
                f"Coins: {player.coins}",
                True,
                GOLD
            ),
            (20, 50)
        )

        screen.blit(
            font_small.render(
                f"Wave: {'BOSS' if wave == BOSS_WAVE else wave}/{BOSS_WAVE}",
                True,
                WHITE
            ),
            (20, 80)
        )

        screen.blit(
            font_small.render(
                f"Score: {player.score}",
                True,
                CYAN
            ),
            (20, 110)
        )

        screen.blit(
            font_small.render(
                "[B] Shop",
                True,
                GOLD
            ),
            (WIDTH - 120, 20)
        )

    # =========================
    # SHOP
    # =========================
    if show_shop:

        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))

        screen.blit(s, (0, 0))

        shop_x = WIDTH // 2 - 150

        screen.blit(
            font_large.render(
                "UPGRADES",
                True,
                GOLD
            ),
            (WIDTH//2 - 180, 80)
        )

        upgrades = [
            ("1: +25 HP", "25 Coins"),
            ("2: +10 Damage", "30 Coins"),
            ("3: +0.8 Speed", "40 Coins"),
            ("4: Fire Rate", "50 Coins")
        ]

        for i, (text, price) in enumerate(upgrades):

            screen.blit(
                font_small.render(
                    f"{text} ({price})",
                    True,
                    WHITE
                ),
                (shop_x, 220 + i*50)
            )

        screen.blit(
            font_small.render(
                "Press B to Resume",
                True,
                GREEN
            ),
            (WIDTH//2 - 120, 480)
        )

    # =========================
    # GAME OVER / WIN
    # =========================
    if game_over or game_won:

        screen.fill(BLACK)

        title = (
            "MISSION FAILED"
            if game_over
            else "MISSION COMPLETE"
        )

        color = BRIGHT_RED if game_over else GOLD

        msg = font_large.render(title, True, color)

        screen.blit(
            msg,
            (
                WIDTH//2 - msg.get_width()//2,
                HEIGHT//2 - 100
            )
        )

        sc = font_small.render(
            f"Final Score: {player.score}",
            True,
            WHITE
        )

        screen.blit(
            sc,
            (
                WIDTH//2 - sc.get_width()//2,
                HEIGHT//2
            )
        )

        pygame.draw.rect(
            screen,
            GRAY,
            button_rect,
            border_radius=10
        )

        txt = font_small.render(
            "Back To Menu",
            True,
            WHITE
        )

        screen.blit(
            txt,
            (
                button_rect.centerx - txt.get_width()//2,
                button_rect.centery - txt.get_height()//2
          )
        )

    pygame.display.flip()

pygame.quit()