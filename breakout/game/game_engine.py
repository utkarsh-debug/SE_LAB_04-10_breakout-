"""
GameEngine: owns the paddle, ball, and bricks.

Starter version: single brick type, no lives yet, no score/combo yet.
Ball-brick collision also has a known bug (see game/collision.py) that
Task 1 asks you to fix. If the ball falls below the paddle, it just
resets to the starting position with no consequence - that's what
Task 2 builds on.
"""

import pygame

from game.paddle import Paddle
from game.ball import Ball
from game.brick import Brick
from game.collision import handle_ball_brick_collision
from game.renderer import WIDTH, HEIGHT

BRICK_ROWS = 4
BRICK_COLS = 8
BRICK_WIDTH = 68
BRICK_HEIGHT = 22
BRICK_GAP = 6
BRICK_TOP_MARGIN = 50


class GameEngine:
    def __init__(self):
        self.paddle = Paddle(x=WIDTH / 2, y=HEIGHT - 30)
        self.ball = Ball(x=WIDTH / 2, y=HEIGHT - 50)
        self.bricks = self._build_bricks()
        self.lives = 3
        self.game_over = False
        self.score = 0
        self.combo = 1

    def _build_bricks(self):
        bricks = []
        total_width = BRICK_COLS * (BRICK_WIDTH + BRICK_GAP) - BRICK_GAP
        start_x = (WIDTH - total_width) / 2

        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * (BRICK_WIDTH + BRICK_GAP)
                y = BRICK_TOP_MARGIN + row * (BRICK_HEIGHT + BRICK_GAP)

                if row == 0:
                    brick_type = "unbreakable"
                    hits_remaining = 999999
                    color = (100, 100, 100)
                elif row == 1:
                    brick_type = "strong"
                    hits_remaining = 3
                    color = (220, 160, 60)
                else:
                    brick_type = "normal"
                    hits_remaining = 1
                    color = (200, 90, 90)

                bricks.append(
                    Brick(
                        x,
                        y,
                        BRICK_WIDTH,
                        BRICK_HEIGHT,
                        brick_type=brick_type,
                        hits_remaining=hits_remaining,
                        color=color,
                    )
                )

        return bricks

    def _reset_ball(self):
        self.ball = Ball(x=WIDTH / 2, y=HEIGHT - 50)

    def handle_input(self, keys_pressed):
        dx = 0

        if keys_pressed[pygame.K_LEFT]:
            dx -= self.paddle.speed

        if keys_pressed[pygame.K_RIGHT]:
            dx += self.paddle.speed

        self.paddle.move(dx, WIDTH)

    def handle_keydown(self, key):
        if self.game_over and key == pygame.K_r:
            self.lives = 3
            self.game_over = False
            self.score = 0
            self.combo = 1
            self.bricks = self._build_bricks()
            self._reset_ball()

    def update(self):
        if self.game_over:
            return

        self.ball.update()
        self.ball.bounce_off_walls(WIDTH)

        if (
            self.ball.get_rect().colliderect(self.paddle.get_rect())
            and self.ball.vy > 0
        ):
            self.ball.bounce_off_paddle(self.paddle.get_rect())

        for brick in self.bricks[:]:
            if handle_ball_brick_collision(self.ball, brick):

                if brick.brick_type != "unbreakable":
                    brick.hits_remaining -= 1

                    if brick.hits_remaining <= 0:
                        self.bricks.remove(brick)
                        self.score += 10 * self.combo
                        self.combo += 1

                break

        if self.ball.is_below(HEIGHT):
            self.lives -= 1
            self.combo = 1

            if self.lives <= 0:
                self.game_over = True
            else:
                self._reset_ball()

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_scene(
            surface,
            self.paddle,
            self.ball,
            self.bricks
        )

        renderer.draw_text(
            surface,
            font,
            f"Bricks left: {len(self.bricks)}",
            (10, 10)
        )

        renderer.draw_text(
            surface,
            font,
            f"Lives: {self.lives}",
            (10, 35)
        )

        renderer.draw_text(
            surface,
            font,
            f"Score: {self.score}",
            (10, 60)
        )

        renderer.draw_text(
            surface,
            font,
            f"Combo: x{self.combo}",
            (10, 85)
        )

        if self.game_over:
            renderer.draw_banner(
                surface,
                font,
                "GAME OVER - Press R to Restart"
            )
