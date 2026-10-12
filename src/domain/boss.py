import math
import random
import pygame
from src.infrastructure.settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_RED, COLOR_YELLOW, COLOR_WHITE, COLOR_GREEN, COLOR_CYAN
from src.infrastructure.utils import load_spritesheet, load_image
from src.domain.laser import Laser


class DreadnoughtBoss(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.frames = load_spritesheet("asset/boss_sheet.png", 170, 92)
        if not self.frames:
            self.frames = [load_image("asset/Enemy2.png", (170, 92))]

        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()

        self.rect.x = SCREEN_WIDTH + 60
        self.rect.y = (SCREEN_HEIGHT // 2) - 46

        self.hitbox = pygame.Rect(0, 0, 135, 58)
        self.hitbox.center = self.rect.center
        self.mask = pygame.mask.from_surface(self.image)

        self.max_health = 6000
        self.health = self.max_health
        self.max_shield = 3000
        self.shield = self.max_shield
        self.points = 5000
        self.credits_reward = 800

        self.target_x = SCREEN_WIDTH - 220
        self.base_speed_y = 3.0
        self.speed_y = self.base_speed_y
        self.move_dir_y = 1
        self.entered_arena = False

        self.last_shot_time = pygame.time.get_ticks() + 1000
        self.attack_pattern_index = 0
        self.animation_timer = 0
        self.animation_speed = 100
        self.hit_flash_timer = 0

    @property
    def current_phase(self) -> int:
        if self.shield > 0 or self.health > 4000:
            return 1
        elif self.health > 2000:
            return 2
        return 3

    def update(self) -> None:
        if not self.entered_arena:
            if self.rect.x > self.target_x:
                self.rect.x -= 3
            else:
                self.rect.x = self.target_x
                self.entered_arena = True
        else:
            phase = self.current_phase
            if phase == 1:
                self.speed_y = 3.0
                desired_x = SCREEN_WIDTH - 220
            elif phase == 2:
                self.speed_y = 4.2
                desired_x = SCREEN_WIDTH - 240
            else:
                self.speed_y = 5.2
                desired_x = SCREEN_WIDTH - 260

            if self.rect.x > desired_x:
                self.rect.x -= 1
            elif self.rect.x < desired_x:
                self.rect.x += 1

            self.rect.y += int(self.speed_y * self.move_dir_y)
            if self.rect.top <= 70:
                self.rect.top = 70
                self.move_dir_y = 1
            elif self.rect.bottom >= SCREEN_HEIGHT - 45:
                self.rect.bottom = SCREEN_HEIGHT - 45
                self.move_dir_y = -1

        now = pygame.time.get_ticks()
        if now - self.animation_timer >= self.animation_speed:
            self.animation_timer = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.mask = pygame.mask.from_surface(self.image)

        self.hitbox.center = self.rect.center

    def try_attack(self, enemy_lasers: pygame.sprite.Group, player_pos: tuple[int, int] | None = None) -> None:
        if not self.entered_arena:
            return

        now = pygame.time.get_ticks()
        phase = self.current_phase

        if phase == 1:
            cooldown = 520
        elif phase == 2:
            cooldown = 360
        else:
            cooldown = 240

        if now - self.last_shot_time < cooldown:
            return

        self.last_shot_time = now

        cx = self.rect.left
        cy = self.rect.centery
        top_y = self.rect.top + 16
        bot_y = self.rect.bottom - 16

        if phase == 1:
            if self.attack_pattern_index % 2 == 0:
                l1 = Laser(cx + 6, top_y, is_player=False, speed_x=-9.0, damage=16)
                l2 = Laser(cx + 2, cy - 16, is_player=False, speed_x=-9.2, damage=16)
                l3 = Laser(cx, cy, is_player=False, speed_x=-9.5, damage=18)
                l4 = Laser(cx + 2, cy + 16, is_player=False, speed_x=-9.2, damage=16)
                l5 = Laser(cx + 6, bot_y, is_player=False, speed_x=-9.0, damage=16)
                enemy_lasers.add(l1, l2, l3, l4, l5)
            else:
                vy = 0.0
                if player_pos:
                    px, py = player_pos
                    dy = py - cy
                    dist_x = max(80, cx - px)
                    vy = (dy / dist_x) * 9.0
                    vy = max(-3.8, min(3.8, vy))

                l1 = Laser(cx, cy - 14, is_player=False, speed_x=-9.5, speed_y=vy, damage=16)
                l2 = Laser(cx, cy + 14, is_player=False, speed_x=-9.5, speed_y=vy, damage=16)
                l_top = Laser(cx + 4, top_y, is_player=False, speed_x=-8.5, speed_y=-1.5, damage=15)
                l_bot = Laser(cx + 4, bot_y, is_player=False, speed_x=-8.5, speed_y=1.5, damage=15)
                enemy_lasers.add(l1, l2, l_top, l_bot)

        elif phase == 2:
            sub = self.attack_pattern_index % 3
            if sub == 0:
                spread_angles = [-3.6, -2.4, -1.2, 0.0, 1.2, 2.4, 3.6]
                for vy in spread_angles:
                    l = Laser(cx, cy, is_player=False, speed_x=-8.8, speed_y=vy, damage=16)
                    enemy_lasers.add(l)
            elif sub == 1:
                l_top1 = Laser(cx, top_y, is_player=False, speed_x=-10.0, speed_y=0.0, damage=16)
                l_top2 = Laser(cx, top_y, is_player=False, speed_x=-9.2, speed_y=-2.2, damage=16)
                l_mid = Laser(cx, cy, is_player=False, speed_x=-10.5, speed_y=0.0, damage=20)
                l_bot1 = Laser(cx, bot_y, is_player=False, speed_x=-10.0, speed_y=0.0, damage=16)
                l_bot2 = Laser(cx, bot_y, is_player=False, speed_x=-9.2, speed_y=2.2, damage=16)
                enemy_lasers.add(l_top1, l_top2, l_mid, l_bot1, l_bot2)
            else:
                vy = 0.0
                if player_pos:
                    px, py = player_pos
                    dy = py - cy
                    dist_x = max(70, cx - px)
                    vy = max(-4.2, min(4.2, (dy / dist_x) * 10.0))

                l_snipe = Laser(cx, cy, is_player=False, speed_x=-10.5, speed_y=vy, damage=20)
                l_hi = Laser(cx, top_y, is_player=False, speed_x=-8.8, speed_y=-2.0, damage=16)
                l_lo = Laser(cx, bot_y, is_player=False, speed_x=-8.8, speed_y=2.0, damage=16)
                enemy_lasers.add(l_snipe, l_hi, l_lo)

        else:
            sub = self.attack_pattern_index % 3
            if sub == 0:
                angles = [-4.4, -3.3, -2.2, -1.1, 0.0, 1.1, 2.2, 3.3, 4.4]
                for vy in angles:
                    l = Laser(cx, cy, is_player=False, speed_x=-9.0, speed_y=vy, damage=16)
                    enemy_lasers.add(l)
            elif sub == 1:
                vy = 0.0
                if player_pos:
                    px, py = player_pos
                    dy = py - cy
                    dist_x = max(60, cx - px)
                    vy = max(-4.8, min(4.8, (dy / dist_x) * 11.0))

                l1 = Laser(cx, cy, is_player=False, speed_x=-11.0, speed_y=vy, damage=20)
                l2 = Laser(cx, cy - 20, is_player=False, speed_x=-10.2, speed_y=vy - 1.2, damage=18)
                l3 = Laser(cx, cy + 20, is_player=False, speed_x=-10.2, speed_y=vy + 1.2, damage=18)
                enemy_lasers.add(l1, l2, l3)
            else:
                l1 = Laser(cx, top_y, is_player=False, speed_x=-9.6, speed_y=-2.2, damage=16)
                l2 = Laser(cx, cy - 14, is_player=False, speed_x=-10.0, speed_y=-0.8, damage=16)
                l3 = Laser(cx, cy, is_player=False, speed_x=-10.5, speed_y=0.0, damage=18)
                l4 = Laser(cx, cy + 14, is_player=False, speed_x=-10.0, speed_y=0.8, damage=16)
                l5 = Laser(cx, bot_y, is_player=False, speed_x=-9.6, speed_y=2.2, damage=16)
                enemy_lasers.add(l1, l2, l3, l4, l5)

        self.attack_pattern_index = (self.attack_pattern_index + 1) % 6

    def take_damage(self, amount: int) -> bool:
        if self.shield > 0:
            if self.shield >= amount:
                self.shield -= amount
                amount = 0
            else:
                amount -= self.shield
                self.shield = 0

        if amount > 0:
            self.health -= amount

        self.hit_flash_timer = pygame.time.get_ticks() + 75
        if self.health <= 0:
            self.health = 0
            self.kill()
            return True
        return False

    def draw_health_bar(self, surface: pygame.Surface) -> None:
        if not self.entered_arena:
            return

        panel_w = 660
        panel_h = 50
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = 56

        phase = self.current_phase

        if self.shield > 0:
            border_color = (0, 200, 240)
            tag_color = (0, 220, 255)
            hp_color = COLOR_GREEN
            title_str = "DREADNOUGHT MAE [FASE 1: ESCUDO ATIVO]"
            stat_str = f"VIDA: {self.health}/{self.max_health}  |  ESCUDO: {self.shield}/{self.max_shield}"
        elif phase == 2:
            border_color = COLOR_YELLOW
            tag_color = COLOR_YELLOW
            hp_color = COLOR_YELLOW
            title_str = "DREADNOUGHT MAE [FASE 2: MODO FURIA]"
            stat_str = f"VIDA: {self.health}/{self.max_health}"
        else:
            flash = (pygame.time.get_ticks() // 200) % 2 == 0
            border_color = COLOR_RED if flash else (255, 120, 30)
            tag_color = COLOR_RED if flash else COLOR_YELLOW
            hp_color = COLOR_RED if flash else (255, 80, 20)
            title_str = "ALERTA MAXIMO: NUCLEO EM SOBRECARGA CRITICA!"
            stat_str = f"VIDA: {self.health}/{self.max_health}"

        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((12, 18, 30, 235))
        surface.blit(panel_surf, (panel_x, panel_y))
        pygame.draw.rect(surface, border_color, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=8)

        font_label = pygame.font.SysFont("Arial", 13, bold=True)
        lbl_title = font_label.render(title_str, True, tag_color)
        lbl_stats = font_label.render(stat_str, True, COLOR_WHITE)
        surface.blit(lbl_title, (panel_x + 14, panel_y + 6))
        surface.blit(lbl_stats, (panel_x + panel_w - lbl_stats.get_width() - 14, panel_y + 6))

        bar_inner_x = panel_x + 14
        bar_inner_w = panel_w - 28
        bar_hp_y = panel_y + 24
        bar_hp_h = 13

        hp_ratio = max(0.0, min(1.0, self.health / self.max_health))
        hp_fill = int(bar_inner_w * hp_ratio)

        pygame.draw.rect(surface, (25, 34, 48), (bar_inner_x, bar_hp_y, bar_inner_w, bar_hp_h), border_radius=3)
        if hp_fill > 0:
            pygame.draw.rect(surface, hp_color, (bar_inner_x, bar_hp_y, hp_fill, bar_hp_h), border_radius=3)
        pygame.draw.rect(surface, (90, 110, 140), (bar_inner_x, bar_hp_y, bar_inner_w, bar_hp_h), 1, border_radius=3)

        if self.max_shield > 0:
            bar_shield_y = panel_y + 39
            bar_shield_h = 5
            shield_ratio = max(0.0, min(1.0, self.shield / max(1, self.max_shield)))
            shield_fill = int(bar_inner_w * shield_ratio)

            pygame.draw.rect(surface, (18, 28, 42), (bar_inner_x, bar_shield_y, bar_inner_w, bar_shield_h), border_radius=2)
            if shield_fill > 0:
                pygame.draw.rect(surface, (0, 220, 255), (bar_inner_x, bar_shield_y, shield_fill, bar_shield_h), border_radius=2)
            pygame.draw.rect(surface, (0, 160, 200), (bar_inner_x, bar_shield_y, bar_inner_w, bar_shield_h), 1, border_radius=2)
