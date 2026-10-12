import math
import random
import pygame
from src.infrastructure.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ENEMY_SCOUT_SPEED,
    ENEMY_CRUISER_SPEED,
    ENEMY_CRUISER_FIRE_RATE,
    POINTS_SCOUT,
    POINTS_CRUISER,
)
from src.infrastructure.utils import load_image, load_spritesheet
from src.domain.laser import Laser


class Enemy(pygame.sprite.Sprite):

    def __init__(self, frames: list[pygame.Surface], x: int, y: int, health: int, points: int, hitbox_size: tuple[int, int]):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        hw, hh = hitbox_size
        self.hitbox = pygame.Rect(0, 0, hw, hh)
        self.hitbox.center = self.rect.center
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_timer = 0
        self.animation_speed = 100
        self.health = health
        self.points = points

    def update_animation(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.animation_timer >= self.animation_speed:
            self.animation_timer = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.mask = pygame.mask.from_surface(self.image)

        self.hitbox.center = self.rect.center

    def take_damage(self, amount: int) -> bool:
        self.health -= amount
        if self.health <= 0:
            self.kill()
            return True
        return False


class ScoutEnemy(Enemy):

    def __init__(self, level_info: dict | None = None):
        frames = load_spritesheet("asset/scout_sheet.png", 100, 48)
        if not frames:
            frames = [load_image("asset/Enemy1.png", (100, 48))]

        y = random.randint(60, SCREEN_HEIGHT - 80)
        start_x = SCREEN_WIDTH + random.randint(20, 100)

        hp = level_info.get("scout_health", 35) if level_info else 35
        super().__init__(frames, start_x, y, health=hp, points=POINTS_SCOUT, hitbox_size=(70, 28))

        base_speed = level_info.get("scout_speed", ENEMY_SCOUT_SPEED) if level_info else ENEMY_SCOUT_SPEED
        self.speed_x = base_speed + random.uniform(-0.3, 0.7)
        self.initial_y = float(y)
        self.wave_phase = random.uniform(0, math.pi * 2)
        self.wave_frequency = 0.045
        self.wave_amplitude = 26.0

        self.can_shoot = level_info.get("scout_can_shoot", False) if level_info else False
        self.fire_rate = level_info.get("scout_fire_rate", 2500) if level_info else 2500
        self.bullet_speed = level_info.get("bullet_speed", 7.0) if level_info else 7.0
        self.last_shot_time = pygame.time.get_ticks() + random.randint(600, 1800)

    def update(self) -> None:
        self.rect.x -= int(self.speed_x)
        self.wave_phase += self.wave_frequency
        new_y = self.initial_y + math.sin(self.wave_phase) * self.wave_amplitude
        self.rect.y = int(max(50, min(SCREEN_HEIGHT - 60, new_y)))

        self.update_animation()

        if self.rect.right < 0:
            self.kill()

    def try_shoot(self, enemy_lasers: pygame.sprite.Group, player_pos: tuple[int, int] | None = None) -> None:
        if not self.can_shoot:
            return

        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.fire_rate:
            self.last_shot_time = now
            if 80 < self.rect.x < SCREEN_WIDTH - 20:
                speed_y = 0.0
                if player_pos:
                    px, py = player_pos
                    if px < self.rect.x:
                        dy = py - self.rect.centery
                        speed_y = max(-2.2, min(2.2, dy * 0.015))

                laser = Laser(
                    self.rect.left,
                    self.rect.centery,
                    is_player=False,
                    speed_x=-self.bullet_speed,
                    speed_y=speed_y,
                    damage=12,
                )
                enemy_lasers.add(laser)


class CruiserEnemy(Enemy):

    def __init__(self, level_info: dict | None = None, level_num: int = 1):
        frames = load_spritesheet("asset/cruiser_sheet.png", 112, 54)
        if not frames:
            frames = [load_image("asset/Enemy2.png", (112, 54))]

        y = random.randint(60, SCREEN_HEIGHT - 90)
        start_x = SCREEN_WIDTH + random.randint(30, 120)

        hp = level_info.get("cruiser_health", 85) if level_info else 85
        super().__init__(frames, start_x, y, health=hp, points=POINTS_CRUISER, hitbox_size=(82, 36))

        base_speed = level_info.get("cruiser_speed", ENEMY_CRUISER_SPEED) if level_info else ENEMY_CRUISER_SPEED
        self.speed_x = base_speed + random.uniform(-0.2, 0.4)
        self.fire_rate = level_info.get("cruiser_fire_rate", ENEMY_CRUISER_FIRE_RATE) if level_info else ENEMY_CRUISER_FIRE_RATE
        self.bullet_speed = level_info.get("bullet_speed", 7.5) if level_info else 7.5
        self.level_num = level_num
        self.last_shot_time = pygame.time.get_ticks() + random.randint(300, 1200)

    def update(self) -> None:
        self.rect.x -= int(self.speed_x)
        self.update_animation()

        if self.rect.right < 0:
            self.kill()

    def try_shoot(self, enemy_lasers: pygame.sprite.Group, player_pos: tuple[int, int] | None = None) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.fire_rate:
            self.last_shot_time = now
            if 0 < self.rect.x < SCREEN_WIDTH:
                if self.level_num <= 3:
                    laser = Laser(
                        self.rect.left,
                        self.rect.centery,
                        is_player=False,
                        speed_x=-self.bullet_speed,
                        damage=15,
                    )
                    enemy_lasers.add(laser)

                elif self.level_num <= 6:
                    l_top = Laser(
                        self.rect.left + 4,
                        self.rect.top + 14,
                        is_player=False,
                        speed_x=-self.bullet_speed,
                        damage=15,
                    )
                    l_bot = Laser(
                        self.rect.left + 4,
                        self.rect.bottom - 14,
                        is_player=False,
                        speed_x=-self.bullet_speed,
                        damage=15,
                    )
                    enemy_lasers.add(l_top, l_bot)

                else:
                    l_center = Laser(
                        self.rect.left,
                        self.rect.centery,
                        is_player=False,
                        speed_x=-self.bullet_speed,
                        speed_y=0.0,
                        damage=16,
                    )
                    l_up = Laser(
                        self.rect.left,
                        self.rect.centery,
                        is_player=False,
                        speed_x=-self.bullet_speed * 0.95,
                        speed_y=-2.0,
                        damage=16,
                    )
                    l_down = Laser(
                        self.rect.left,
                        self.rect.centery,
                        is_player=False,
                        speed_x=-self.bullet_speed * 0.95,
                        speed_y=2.0,
                        damage=16,
                    )
                    enemy_lasers.add(l_center, l_up, l_down)
