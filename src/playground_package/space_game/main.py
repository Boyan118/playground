import random
import time

import pygame

pygame.font.init()

WIDTH, HEIGHT = 1000, 800

PLAYER_WIDTH, PLAYER_HEIGHT = 40, 60
PLAYER_VELOCITY = 10

STAR_WIDTH, STAR_HEIGHT = (10, 20)
STAR_VELOCITY = 10

FONT = pygame.font.SysFont("comicsans", 30)

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Game")

BG = pygame.transform.scale(
    pygame.image.load("src/playground_package/space_game/assets/bg.jpeg"), (WIDTH, HEIGHT))


def draw(player: pygame.Rect, elapsed_time: float, stars: list[pygame.Rect]):
    WIN.blit(BG, (0, 0))

    pygame.draw.rect(WIN, "red", player)

    time_text = FONT.render(f"time: {round(elapsed_time)}s", 1, "white")
    WIN.blit(time_text, (10, 10))

    for star in stars:
        pygame.draw.rect(WIN, "blue", star)

    pygame.display.update()


def main():
    run = True

    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    start_add_increment = 2000
    star_count = 0

    hit = False

    stars = []

    while run:
        star_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        if star_count > start_add_increment:
            for _ in range(3):
                star_x = random.randint(0, WIDTH-STAR_WIDTH)
                star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)

                stars.append(star)

            start_add_increment = max(200, start_add_increment - 50)
            star_count = 0


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player.x - PLAYER_VELOCITY >= 0:
            player.x -= PLAYER_VELOCITY

        if keys[pygame.K_RIGHT] and player.x + PLAYER_WIDTH + PLAYER_VELOCITY <= WIDTH:
            player.x += PLAYER_VELOCITY

        for star in stars[:]:
            star.y += STAR_VELOCITY

            if star.y > HEIGHT:
                stars.remove(star)
            elif star.y + star.height >= player.y and star.colliderect(player):
                stars.remove(star)
                hit = True

                break

        if hit:
            lost_text = FONT.render("You lost!", 1, "white")
            WIN.blit(lost_text, (WIDTH/2 - lost_text.width, HEIGHT/2 - lost_text.height))
            pygame.display.update()
            pygame.time.delay(4000)
            break

        draw(player, elapsed_time, stars)

    pygame.quit()
    print("Game ended", flush=True)

