import pygame
import random
import math
import sys

# -------- Configuration --------
WIDTH, HEIGHT = 900, 520
FPS = 60
PLAYER_W, PLAYER_H = 60, 14
PLAYER_SPEED = 380  # pixels per second
INITIAL_SPAWN_INTERVAL = 1000  # milliseconds
MIN_SPAWN_INTERVAL = 300
DIFFICULTY_STEP_MS = 5000

# Colors
BG = (7, 16, 36)
STAR = (223, 239, 255, 40)
PLAYER_COLOR = (88, 214, 141)
METEOR_COLOR = (191, 191, 191)
HUD_COLOR = (230, 240, 255)
OVERLAY = (2, 6, 23, 160)

# -------- Helper functions --------

def clamp(v, a, b):
    return max(a, min(b, v))


def circle_rect_collide(cx, cy, cr, rx, ry, rw, rh):
    # Find closest point on rect to circle center
    closest_x = clamp(cx, rx, rx + rw)
    closest_y = clamp(cy, ry, ry + rh)
    dx = cx - closest_x
    dy = cy - closest_y
    return (dx * dx + dy * dy) <= cr * cr


# -------- Game classes --------
class Player:
    def __init__(self, x, y):
        self.w = PLAYER_W
        self.h = PLAYER_H
        self.x = x
        self.y = y
        self.vx = 0
        self.speed = PLAYER_SPEED

    def update(self, dt, keys):
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
        self.x += self.vx * dt
        self.x = clamp(self.x, 6, WIDTH - self.w - 6)

    def draw(self, surf):
        # draw a simple triangular ship
        p1 = (int(self.x + self.w / 2), int(self.y))
        p2 = (int(self.x + self.w + 6), int(self.y + self.h + 6))
        p3 = (int(self.x - 6), int(self.y + self.h + 6))
        pygame.draw.polygon(surf, PLAYER_COLOR, (p1, p2, p3))
        # thruster
        if self.vx != 0:
            thr = pygame.Rect(int(self.x + self.w/2 - 6), int(self.y + self.h + 6), 12, 8)
            pygame.draw.rect(surf, (255, 217, 122), thr)


class Meteor:
    def __init__(self):
        self.r = random.randint(18, 54)
        self.x = random.uniform(0, WIDTH - self.r)
        self.y = -self.r
        self.vy = random.uniform(70, 250) / 1.0
        # for rotation animation (optional)
        self.angle = random.uniform(0, math.pi * 2)
        self.vr = random.uniform(-2, 2)

    def update(self, dt):
        self.y += self.vy * dt
        self.angle += self.vr * dt

    def draw(self, surf):
        # draw as circle for simplicity
        pygame.draw.circle(surf, METEOR_COLOR, (int(self.x + self.r/2), int(self.y + self.r/2)), int(self.r/2))


# -------- Main game logic --------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Space Dodger (Pygame)')
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 24)
    big_font = pygame.font.SysFont(None, 48)

    # starfield
    stars = [(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), random.uniform(0.2, 1.6)) for _ in range(120)]

    def draw_stars(surface):
        for x, y, s in stars:
            rect = pygame.Rect(int(x), int(y), int(s), int(s))
            surface.fill((223, 239, 255), rect)

    # game state
    running = True
    playing = False
    paused = False
    score = 0

    player = Player(WIDTH/2 - PLAYER_W/2, HEIGHT - 60)
    meteors = []

    spawn_interval = INITIAL_SPAWN_INTERVAL
    spawn_acc = 0
    difficulty_acc = 0

    last_time = pygame.time.get_ticks()

    def reset_game():
        nonlocal score, meteors, spawn_interval, spawn_acc, difficulty_acc, player, playing
        score = 0
        meteors = []
        spawn_interval = INITIAL_SPAWN_INTERVAL
        spawn_acc = 0
        difficulty_acc = 0
        player = Player(WIDTH/2 - PLAYER_W/2, HEIGHT - 60)
        playing = True

    # Start automatically
    reset_game()

    while running:
        dt_ms = clock.tick(FPS)
        dt = dt_ms / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if not playing and event.key == pygame.K_SPACE:
                    reset_game()
                if event.key == pygame.K_p:
                    paused = not paused

        keys = pygame.key.get_pressed()

        if playing and not paused:
            # update player
            player.update(dt, keys)

            # spawn meteors
            spawn_acc += dt_ms
            difficulty_acc += dt_ms
            if spawn_acc >= spawn_interval:
                meteors.append(Meteor())
                spawn_acc = 0

            # difficulty
            if difficulty_acc >= DIFFICULTY_STEP_MS:
                difficulty_acc = 0
                spawn_interval = max(MIN_SPAWN_INTERVAL, spawn_interval - 60)

            # update meteors
            for m in meteors[:]:
                m.update(dt)
                # collision
                cx = m.x + m.r/2
                cy = m.y + m.r/2
                cr = m.r/2
                if circle_rect_collide(cx, cy, cr, player.x, player.y, player.w, player.h):
                    playing = False
                # off-screen -> increase score
                if m.y - m.r > HEIGHT:
                    meteors.remove(m)
                    score += 1

        # Draw
        screen.fill(BG)
        draw_stars(screen)

        for m in meteors:
            m.draw(screen)

        player.draw(screen)

        # HUD
        score_surf = font.render(f'Score: {score}', True, HUD_COLOR)
        screen.blit(score_surf, (12, 8))

        if not playing:
            # overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((2, 6, 23, 180))
            screen.blit(overlay, (0, 0))

            text = big_font.render('Game Over', True, (255, 255, 255))
            sub = font.render('Press Space to play again or Esc to quit', True, (210, 220, 255))
            screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - 40))
            screen.blit(sub, (WIDTH/2 - sub.get_width()/2, HEIGHT/2 + 10))

        # pause indicator
        if paused:
            p = font.render('Paused (press P to resume)', True, HUD_COLOR)
            screen.blit(p, (WIDTH/2 - p.get_width()/2, 40))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
