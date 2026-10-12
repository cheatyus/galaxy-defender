import math
import pygame
from src.infrastructure.settings import SCREEN_WIDTH, SCREEN_HEIGHT, LASER_PLAYER_SPEED, LASER_ENEMY_SPEED
from src.infrastructure.utils import load_image


class Laser(pygame.sprite.Sprite):

    def __init__(
        self,
        x: float,
        y: float,
        is_player: bool = True,
        speed_x: float | None = None,
        speed_y: float = 0.0,
        damage: int | None = None,
    ):
        super().__init__()
        self.is_player = is_player

        if self.is_player:
            self.image = load_image("asset/Player1Shot.png", (22, 8))
            self.speed_x = LASER_PLAYER_SPEED if speed_x is None else speed_x
            self.speed_y = speed_y
            self.damage = 25 if damage is None else damage
            self.hitbox = pygame.Rect(0, 0, 20, 6)
            if self.speed_y != 0:
                angle_deg = -math.degrees(math.atan2(self.speed_y, self.speed_x))
                self.image = pygame.transform.rotate(self.image, angle_deg)
        else:
            self.image = load_image("asset/Enemy1Shot.png", (20, 16))
            self.speed_x = -LASER_ENEMY_SPEED if speed_x is None else speed_x
            self.speed_y = speed_y
            self.damage = 15 if damage is None else damage
            self.hitbox = pygame.Rect(0, 0, 16, 12)

            if self.speed_y != 0:
                angle_deg = -math.degrees(math.atan2(self.speed_y, self.speed_x)) - 180
                self.image = pygame.transform.rotate(self.image, angle_deg)

        self.rect = self.image.get_rect()
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.rect.center = (int(self.pos_x), int(self.pos_y))
        self.hitbox.center = self.rect.center
        self.mask = pygame.mask.from_surface(self.image)

    def update(self) -> None:
        self.pos_x += self.speed_x
        self.pos_y += self.speed_y
        self.rect.center = (int(self.pos_x), int(self.pos_y))
        self.hitbox.center = self.rect.center

        if (
            self.rect.left > SCREEN_WIDTH + 60
            or self.rect.right < -60
            or self.rect.top > SCREEN_HEIGHT + 60
            or self.rect.bottom < -60
        ):
            self.kill()
