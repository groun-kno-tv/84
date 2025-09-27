"""A simple Tank Battle game using pygame.
Controls:
- Arrow keys: move
- Space: fire
"""
import pygame
import random
import sys

# Game settings
WIDTH, HEIGHT = 800, 600
PLAYER_SPEED = 4
BULLET_SPEED = 8
ENEMY_SPEED = 2
ENEMY_FIRE_CHANCE = 0.01  # per frame

# Colors
BG = (30, 30, 30)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
YELLOW = (240, 240, 80)
WHITE = (255, 255, 255)

class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls=False):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, 40, 40))
        # barrel
        pygame.draw.rect(self.image, (20,20,20), (18, -6, 4, 20))
        self.orig_image = self.image
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = pygame.math.Vector2(0, -1)
        self.speed = PLAYER_SPEED if controls else ENEMY_SPEED
        self.controls = controls
        self.cooldown = 0

    def update(self, keys=None):
        if self.controls and keys:
            dx = dy = 0
            if keys[pygame.K_LEFT]:
                dx = -self.speed
                self.direction = pygame.math.Vector2(-1, 0)
            if keys[pygame.K_RIGHT]:
                dx = self.speed
                self.direction = pygame.math.Vector2(1, 0)
            if keys[pygame.K_UP]:
                dy = -self.speed
                self.direction = pygame.math.Vector2(0, -1)
            if keys[pygame.K_DOWN]:
                dy = self.speed
                self.direction = pygame.math.Vector2(0, 1)
            self.rect.x += dx
            self.rect.y += dy
        else:
            # simple random patrol for enemy
            if random.random() < 0.02:
                self.direction = random.choice([pygame.math.Vector2(1,0), pygame.math.Vector2(-1,0),
                                                pygame.math.Vector2(0,1), pygame.math.Vector2(0,-1)])
            self.rect.x += int(self.direction.x * self.speed)
            self.rect.y += int(self.direction.y * self.speed)

        # keep inside screen
        self.rect.left = max(0, self.rect.left)
        self.rect.top = max(0, self.rect.top)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)
        if self.cooldown > 0:
            self.cooldown -= 1

    def fire(self, group, color=YELLOW):
        if self.cooldown == 0:
            bx = self.rect.centerx + int(self.direction.x * 24)
            by = self.rect.centery + int(self.direction.y * 24)
            vel = (int(self.direction.x * BULLET_SPEED), int(self.direction.y * BULLET_SPEED))
            bullet = Bullet(bx, by, vel, color)
            group.add(bullet)
            self.cooldown = 15  # frames cooldown


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vel, color):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (4,4), 4)
        self.rect = self.image.get_rect(center=(x,y))
        self.vx, self.vy = vel

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if (self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tank Battle')
    clock = pygame.time.Clock()

    # groups
    all_sprites = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()

    # player
    player = Tank(WIDTH//2, HEIGHT-80, GREEN, controls=True)
    all_sprites.add(player)

    # enemies
    for i in range(4):
        e = Tank(100 + i*150, 80, RED, controls=False)
        all_sprites.add(e)
        enemy_group.add(e)

    score = 0
    running = True

    font = pygame.font.SysFont(None, 36)

    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.fire(player_bullets)

        # enemy fire randomly
        for e in enemy_group:
            if random.random() < ENEMY_FIRE_CHANCE:
                e.fire(enemy_bullets, color=WHITE)

        # update
        all_sprites.update(keys)
        player_bullets.update()
        enemy_bullets.update()

        # collisions
        for b in player_bullets:
            hit = pygame.sprite.spritecollideany(b, enemy_group)
            if hit:
                b.kill()
                hit.kill()
                score += 100

        for b in enemy_bullets:
            if pygame.sprite.collide_rect(b, player):
                b.kill()
                running = False  # player hit -> game over

        # draw
        screen.fill(BG)
        all_sprites.draw(screen)
        player_bullets.draw(screen)
        enemy_bullets.draw(screen)

        score_surf = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_surf, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    # game over screen
    screen.fill(BG)
    over = font.render('Game Over', True, (200,0,0))
    scr = font.render(f'Final Score: {score}', True, WHITE)
    screen.blit(over, (WIDTH//2 - over.get_width()//2, HEIGHT//2 - 20))
    screen.blit(scr, (WIDTH//2 - scr.get_width()//2, HEIGHT//2 + 20))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()


if __name__ == '__main__':
    main()
