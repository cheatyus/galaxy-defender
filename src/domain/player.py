import pygame
from src.infrastructure.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    PLAYER_SPEED,
    PLAYER_MAX_HEALTH,
    PLAYER_FIRE_COOLDOWN,
)
from src.infrastructure.utils import load_image, load_spritesheet
from src.domain.laser import Laser


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.frames = load_spritesheet("asset/player_sheet.png", 80, 40)
        if not self.frames:
            self.frames = [load_image("asset/Player1.png", (80, 40))]

        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()

        self.hitbox = pygame.Rect(0, 0, 50, 20)
        self.mask = pygame.mask.from_surface(self.image)

        self.animation_timer = 0
        self.animation_speed = 90

        self.base_speed = PLAYER_SPEED
        self.speed = self.base_speed
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.fire_cooldown = PLAYER_FIRE_COOLDOWN
        self.laser_damage = 25
        self.double_cannon = False
        self.triple_cannon = False

        self.max_shield = 0
        self.shield = 0
        self.shield_regen_interval = 1200
        self.last_shield_regen_time = 0
        self.last_damage_taken_time = 0

        self.magnet_level = 0
        self.magnet_bonus_pct = 0

        self.last_shot_time = 0
        self.reset()

    def apply_upgrades(self, stats: dict) -> None:
        dmg_values = [25, 40, 60, 85, 120]
        hp_values = [100, 140, 190, 250, 320]
        shield_values = [0, 40, 80, 130]
        cd_values = [200, 160, 125, 95, 70]
        spd_values = [6.0, 7.2, 8.4, 9.6, 11.0]
        magnet_values = [0, 35, 75, 120]

        dmg_lvl = min(len(dmg_values), max(1, stats.get("damage_level", 1)))
        hp_lvl = min(len(hp_values), max(1, stats.get("health_level", 1)))
        shield_lvl = min(len(shield_values) - 1, max(0, stats.get("shield_level", 0)))
        cd_lvl = min(len(cd_values), max(1, stats.get("firerate_level", 1)))
        spd_lvl = min(len(spd_values), max(1, stats.get("speed_level", 1)))
        magnet_lvl = min(len(magnet_values) - 1, max(0, stats.get("magnet_level", 0)))

        self.laser_damage = dmg_values[dmg_lvl - 1]
        self.max_health = hp_values[hp_lvl - 1]
        self.max_shield = shield_values[shield_lvl]
        self.fire_cooldown = cd_values[cd_lvl - 1]
        self.speed = spd_values[spd_lvl - 1]
        self.double_cannon = bool(stats.get("double_cannon", False))
        self.triple_cannon = bool(stats.get("triple_cannon", False))
        self.magnet_level = magnet_lvl
        self.magnet_bonus_pct = magnet_values[magnet_lvl]

        self.health = self.max_health
        self.shield = self.max_shield

    def reset(self) -> None:
        self.health = self.max_health
        self.shield = self.max_shield
        self.rect.x = 80
        self.rect.y = (SCREEN_HEIGHT // 2) - (self.rect.height // 2)
        self.hitbox.center = self.rect.center
        self.last_shot_time = 0
        self.last_damage_taken_time = 0
        self.last_shield_regen_time = 0
        self.current_frame = 0

    def update(self) -> None:
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.rect.x += int(dx)
        self.rect.y += int(dy)

        if self.rect.left < 10:
            self.rect.left = 10
        if self.rect.right > SCREEN_WIDTH - 10:
            self.rect.right = SCREEN_WIDTH - 10
        if self.rect.top < 52:
            self.rect.top = 52
        if self.rect.bottom > SCREEN_HEIGHT - 30:
            self.rect.bottom = SCREEN_HEIGHT - 30

        now = pygame.time.get_ticks()

        if self.max_shield > 0 and self.shield < self.max_shield:
            if now - self.last_damage_taken_time >= 2000:
                if now - self.last_shield_regen_time >= self.shield_regen_interval:
                    self.last_shield_regen_time = now
                    self.shield = min(self.max_shield, self.shield + 5)

        if now - self.animation_timer >= self.animation_speed:
            self.animation_timer = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.mask = pygame.mask.from_surface(self.image)

        self.hitbox.center = self.rect.center

    def shoot(self, laser_group: pygame.sprite.Group) -> bool:
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.fire_cooldown:
            self.last_shot_time = now

            if self.triple_cannon:
                laser_mid = Laser(self.rect.right, self.rect.centery, is_player=True, speed_x=11.0, speed_y=0.0, damage=self.laser_damage)
                laser_up = Laser(self.rect.right, self.rect.centery - 10, is_player=True, speed_x=10.5, speed_y=-1.8, damage=self.laser_damage)
                laser_down = Laser(self.rect.right, self.rect.centery + 10, is_player=True, speed_x=10.5, speed_y=1.8, damage=self.laser_damage)
                laser_group.add(laser_mid, laser_up, laser_down)

            elif self.double_cannon:
                laser1 = Laser(self.rect.right, self.rect.centery - 9, is_player=True, speed_x=10.5, speed_y=0.0, damage=self.laser_damage)
                laser2 = Laser(self.rect.right, self.rect.centery + 9, is_player=True, speed_x=10.5, speed_y=0.0, damage=self.laser_damage)
                laser_group.add(laser1, laser2)

            else:
                laser = Laser(self.rect.right, self.rect.centery, is_player=True, speed_x=10.0, speed_y=0.0, damage=self.laser_damage)
                laser_group.add(laser)

            return True
        return False

    def take_damage(self, amount: int) -> bool:
        self.last_damage_taken_time = pygame.time.get_ticks()

        if self.shield > 0:
            if self.shield >= amount:
                self.shield -= amount
                return False
            else:
                remaining_damage = amount - self.shield
                self.shield = 0
                self.health -= remaining_damage
        else:
            self.health -= amount

        if self.health <= 0:
            self.health = 0
            return True
        return False
