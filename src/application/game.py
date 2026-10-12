import math
import random
import pygame
from src.infrastructure.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    TITLE,
    COLOR_WHITE,
    COLOR_GREEN,
    COLOR_YELLOW,
    COLOR_RED,
    COLOR_CYAN,
    COLLISION_DAMAGE,
)
from src.infrastructure.utils import load_image, play_music
from src.domain.player import Player
from src.domain.enemy import ScoutEnemy, CruiserEnemy
from src.domain.boss import DreadnoughtBoss
from src.domain.levels import get_level_info
from src.application.shop import Shop
from src.infrastructure.database import DatabaseManager
from src.ui.explosion import ParticleSystem, AnimatedExplosion
from src.ui.menu import MenuRenderer


class Game:

    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_PAUSED = "paused"
    STATE_SHOP = "shop"
    STATE_LEVEL_COMPLETE = "level_complete"
    STATE_VICTORY = "victory"
    STATE_GAME_OVER = "game_over"

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.db = DatabaseManager("data/savegame.db")
        self.player_data = self.db.load_save()

        self.menu_renderer = MenuRenderer()
        self.shop = Shop()

        self.font_hud = pygame.font.SysFont("Arial", 17, bold=True)
        self.font_hud_small = pygame.font.SysFont("Arial", 14)
        self.font_hud_tiny = pygame.font.SysFont("Arial", 11, bold=True)

        self.particles = ParticleSystem()
        self.explosions = pygame.sprite.Group()

        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_lasers = pygame.sprite.Group()
        self.enemy_lasers = pygame.sprite.Group()

        self.player = Player()
        self.player.apply_upgrades(self.player_data)

        self.boss: DreadnoughtBoss | None = None

        self.current_level = self.player_data.get("current_level", 1)
        self.completed_level = max(0, self.current_level - 1)
        self.score = self.player_data.get("score", 0)
        self.enemies_killed = self.player_data.get("enemies_killed", 0)
        self.credits = self.player_data.get("credits", 0)

        self.level_kills = 0
        self.last_enemy_spawn = 0
        self.state = self.STATE_MENU
        self.show_hitboxes = False

        self.bg_base = load_image("asset/Level1Bg0.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg_overlay = None
        self.bg_base_x = 0.0
        self.bg_overlay_x = 0.0
        self.bg_base_speed = 0.8
        self.bg_overlay_speed = 1.8

        play_music("asset/Menu.mp3", loop=-1, volume=0.5)

    def save_current_progress(self) -> None:
        self.player_data["current_level"] = self.current_level
        self.player_data["credits"] = self.credits
        self.player_data["score"] = self.score
        self.player_data["enemies_killed"] = self.enemies_killed

        self.db.save_game(
            current_level=self.current_level,
            credits=self.credits,
            score=self.score,
            enemies_killed=self.enemies_killed,
            damage_level=self.player_data.get("damage_level", 1),
            health_level=self.player_data.get("health_level", 1),
            shield_level=self.player_data.get("shield_level", 0),
            firerate_level=self.player_data.get("firerate_level", 1),
            speed_level=self.player_data.get("speed_level", 1),
            double_cannon=self.player_data.get("double_cannon", False),
            triple_cannon=self.player_data.get("triple_cannon", False),
            magnet_level=self.player_data.get("magnet_level", 0),
        )

    def reset_campaign(self) -> None:
        self.db.reset_save()
        self.player_data = self.db.load_save()
        self.current_level = 1
        self.completed_level = 0
        self.score = 0
        self.credits = 0
        self.enemies_killed = 0
        self.player.apply_upgrades(self.player_data)

    def load_level(self, level_num: int) -> None:
        self.current_level = max(1, min(10, level_num))
        level_info = get_level_info(self.current_level)

        self.bg_base = load_image(level_info.get("bg_base", "asset/Level1Bg0.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
        if level_info.get("bg_overlay"):
            self.bg_overlay = load_image(level_info["bg_overlay"], (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.bg_overlay = None

        self.bg_base_x = 0.0
        self.bg_overlay_x = 0.0
        self.level_kills = 0
        self.last_enemy_spawn = pygame.time.get_ticks()

        self.enemies.empty()
        self.player_lasers.empty()
        self.enemy_lasers.empty()
        self.explosions.empty()
        self.all_sprites.empty()
        self.particles.clear()

        self.player.reset()
        self.player.apply_upgrades(self.player_data)
        self.all_sprites.add(self.player)

        if level_info["is_boss_level"]:
            self.boss = DreadnoughtBoss()
            self.enemies.add(self.boss)
            self.all_sprites.add(self.boss)
            play_music("asset/Level2.mp3", loop=-1, volume=0.55)
        else:
            self.boss = None
            bg_music = "asset/Level1.mp3" if self.current_level <= 5 else "asset/Level2.mp3"
            play_music(bg_music, loop=-1, volume=0.5)

        self.state = self.STATE_PLAYING

    def switch_to_menu(self) -> None:
        self.save_current_progress()
        self.state = self.STATE_MENU
        play_music("asset/Menu.mp3", loop=-1, volume=0.5)

    def spawn_enemies(self) -> None:
        now = pygame.time.get_ticks()
        level_info = get_level_info(self.current_level)

        if now - self.last_enemy_spawn >= level_info["spawn_interval"]:
            self.last_enemy_spawn = now

            if random.random() < level_info["cruiser_prob"]:
                enemy = CruiserEnemy(level_info=level_info, level_num=self.current_level)
            else:
                enemy = ScoutEnemy(level_info=level_info)

            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def trigger_explosion(self, x: int, y: int, is_large: bool = False) -> None:
        self.explosions.add(AnimatedExplosion(x, y))
        count = 32 if is_large else 18
        self.particles.create_explosion(x, y, count=count)

    def handle_collisions(self) -> None:
        level_info = get_level_info(self.current_level)

        for laser in list(self.player_lasers):
            for enemy in list(self.enemies):
                if laser.hitbox.colliderect(enemy.hitbox):
                    laser.kill()
                    self.particles.create_explosion(
                        laser.rect.right,
                        laser.rect.centery,
                        count=8,
                        color_palette=[(255, 200, 50), (255, 100, 20)],
                    )
                    destroyed = enemy.take_damage(laser.damage)
                    if destroyed:
                        self.score += enemy.points
                        self.enemies_killed += 1

                        bonus_pct = getattr(self.player, "magnet_bonus_pct", 0)

                        if isinstance(enemy, DreadnoughtBoss):
                            base_rew = enemy.credits_reward
                            earned = base_rew + int(base_rew * (bonus_pct / 100.0))
                            self.credits += earned
                            self.trigger_explosion(enemy.rect.centerx, enemy.rect.centery, is_large=True)
                            self.save_current_progress()
                            self.state = self.STATE_VICTORY
                            play_music("asset/Score.mp3", loop=-1, volume=0.6)
                            return
                        else:
                            base_rew = level_info["credits_reward"]
                            earned = base_rew + int(base_rew * (bonus_pct / 100.0))
                            self.credits += earned
                            self.level_kills += 1
                            self.trigger_explosion(enemy.rect.centerx, enemy.rect.centery, is_large=False)

                            if not level_info["is_boss_level"] and self.level_kills >= level_info["kill_target"]:
                                self.completed_level = self.current_level
                                self.current_level = min(10, self.current_level + 1)
                                self.save_current_progress()
                                self.state = self.STATE_LEVEL_COMPLETE
                                play_music("asset/Score.mp3", loop=-1, volume=0.6)
                                return
                    break

        for laser in list(self.enemy_lasers):
            if laser.hitbox.colliderect(self.player.hitbox):
                laser.kill()
                self.particles.create_explosion(
                    laser.rect.left,
                    laser.rect.centery,
                    count=10,
                    color_palette=[(231, 76, 60), (241, 196, 15)],
                )
                player_destroyed = self.player.take_damage(laser.damage)
                if player_destroyed:
                    self.trigger_explosion(self.player.rect.centerx, self.player.rect.centery, is_large=True)
                    self.save_current_progress()
                    self.state = self.STATE_GAME_OVER
                    play_music("asset/Score.mp3", loop=-1, volume=0.6)
                    return

        for enemy in list(self.enemies):
            if self.player.hitbox.colliderect(enemy.hitbox):
                if not isinstance(enemy, DreadnoughtBoss):
                    enemy.kill()
                    self.trigger_explosion(enemy.rect.centerx, enemy.rect.centery, is_large=False)

                player_destroyed = self.player.take_damage(COLLISION_DAMAGE)
                if player_destroyed:
                    self.trigger_explosion(self.player.rect.centerx, self.player.rect.centery, is_large=True)
                    self.save_current_progress()
                    self.state = self.STATE_GAME_OVER
                    play_music("asset/Score.mp3", loop=-1, volume=0.6)
                    return

    def update_playing(self) -> None:
        self.bg_base_x -= self.bg_base_speed
        if self.bg_base_x <= -SCREEN_WIDTH:
            self.bg_base_x = 0.0

        if self.bg_overlay:
            self.bg_overlay_x -= self.bg_overlay_speed
            if self.bg_overlay_x <= -SCREEN_WIDTH:
                self.bg_overlay_x = 0.0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.player.shoot(self.player_lasers)

        player_pos = (self.player.rect.centerx, self.player.rect.centery)
        for enemy in self.enemies:
            if isinstance(enemy, CruiserEnemy):
                enemy.try_shoot(self.enemy_lasers, player_pos)
            elif isinstance(enemy, ScoutEnemy):
                enemy.try_shoot(self.enemy_lasers, player_pos)
            elif isinstance(enemy, DreadnoughtBoss):
                enemy.try_attack(self.enemy_lasers, player_pos)

        self.player.update()
        self.enemies.update()
        self.player_lasers.update()
        self.enemy_lasers.update()
        self.explosions.update()
        self.particles.update()

        self.spawn_enemies()

        self.handle_collisions()

    def draw_hud(self) -> None:
        hud_bar = pygame.Surface((SCREEN_WIDTH, 50), pygame.SRCALPHA)
        hud_bar.fill((8, 14, 25, 230))
        self.screen.blit(hud_bar, (0, 0))
        pygame.draw.line(self.screen, (0, 200, 240), (0, 50), (SCREEN_WIDTH, 50), 2)

        left_x = 18
        gauge_w = 130

        hp_ratio = max(0.0, min(1.0, self.player.health / max(1, self.player.max_health)))
        hp_color = (46, 204, 113) if hp_ratio > 0.5 else ((241, 196, 15) if hp_ratio > 0.25 else (231, 76, 60))

        if self.player.max_shield > 0:
            pygame.draw.rect(self.screen, (25, 35, 50), (left_x, 8, gauge_w, 14), border_radius=3)
            if self.player.health > 0:
                pygame.draw.rect(self.screen, hp_color, (left_x, 8, int(gauge_w * hp_ratio), 14), border_radius=3)
            pygame.draw.rect(self.screen, (90, 110, 140), (left_x, 8, gauge_w, 14), 1, border_radius=3)
            txt_hp = self.font_hud_tiny.render(f"VIDA {self.player.health}/{self.player.max_health}", True, COLOR_WHITE)
            self.screen.blit(txt_hp, (left_x + gauge_w + 8, 8))

            shield_ratio = max(0.0, min(1.0, self.player.shield / max(1, self.player.max_shield)))
            pygame.draw.rect(self.screen, (20, 30, 45), (left_x, 26, gauge_w, 14), border_radius=3)
            if self.player.shield > 0:
                pygame.draw.rect(self.screen, (0, 220, 255), (left_x, 26, int(gauge_w * shield_ratio), 14), border_radius=3)
            pygame.draw.rect(self.screen, (0, 180, 220), (left_x, 26, gauge_w, 14), 1, border_radius=3)
            txt_shield = self.font_hud_tiny.render(f"ESCUDO {self.player.shield}/{self.player.max_shield}", True, (0, 220, 255))
            self.screen.blit(txt_shield, (left_x + gauge_w + 8, 26))
        else:
            pygame.draw.rect(self.screen, (25, 35, 50), (left_x, 12, 140, 22), border_radius=4)
            if self.player.health > 0:
                pygame.draw.rect(self.screen, hp_color, (left_x, 12, int(140 * hp_ratio), 22), border_radius=4)
            pygame.draw.rect(self.screen, (100, 120, 150), (left_x, 12, 140, 22), 1, border_radius=4)
            txt_hp = self.font_hud.render(f"VIDA {self.player.health}/{self.player.max_health}", True, COLOR_WHITE)
            self.screen.blit(txt_hp, (left_x + 150, 12))

        level_info = get_level_info(self.current_level)
        pill_w = 320
        pill_h = 38
        pill_x = (SCREEN_WIDTH - pill_w) // 2
        pill_y = 6

        pill_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pill_surf.fill((16, 26, 42, 220))
        self.screen.blit(pill_surf, (pill_x, pill_y))

        if level_info["is_boss_level"]:
            pygame.draw.rect(self.screen, (231, 76, 60), (pill_x, pill_y, pill_w, pill_h), 1, border_radius=6)
            b_text = self.font_hud.render("SETOR 10 // CONFRONTO FINAL", True, (255, 110, 110))
            self.screen.blit(b_text, (pill_x + (pill_w - b_text.get_width()) // 2, pill_y + 9))
        else:
            pygame.draw.rect(self.screen, (0, 200, 240), (pill_x, pill_y, pill_w, pill_h), 1, border_radius=6)
            sec_text = self.font_hud.render(f"SETOR {self.current_level} // 10", True, COLOR_CYAN)
            self.screen.blit(sec_text, (pill_x + 14, pill_y + 4))

            target = max(1, level_info["kill_target"])
            kills = min(target, self.level_kills)
            kill_ratio = kills / target

            mini_bar_x = pill_x + 14
            mini_bar_y = pill_y + 25
            mini_bar_w = pill_w - 28
            mini_bar_h = 6

            pygame.draw.rect(self.screen, (30, 45, 65), (mini_bar_x, mini_bar_y, mini_bar_w, mini_bar_h), border_radius=2)
            pygame.draw.rect(self.screen, (0, 220, 180), (mini_bar_x, mini_bar_y, int(mini_bar_w * kill_ratio), mini_bar_h), border_radius=2)

            k_text = self.font_hud_tiny.render(f"ALVOS: {kills}/{target}", True, (180, 205, 230))
            self.screen.blit(k_text, (pill_x + pill_w - k_text.get_width() - 14, pill_y + 5))

        if self.player.triple_cannon:
            wp_str = "TRÍPLICE"
            wp_col = (0, 220, 255)
        elif self.player.double_cannon:
            wp_str = "DUPLO"
            wp_col = (46, 204, 113)
        else:
            wp_str = "PADRÃO"
            wp_col = (180, 195, 215)

        wp_badge = self.font_hud_tiny.render(f"CANHÃO: {wp_str}", True, wp_col)
        self.screen.blit(wp_badge, (SCREEN_WIDTH - 290, 10))

        cred_text = self.font_hud.render(f"{self.credits} CR", True, COLOR_YELLOW)
        score_text = self.font_hud_tiny.render(f"PTS: {self.score}", True, (200, 215, 235))
        self.screen.blit(cred_text, (SCREEN_WIDTH - cred_text.get_width() - 18, 8))
        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 18, 28))

        if self.boss and self.boss.alive():
            self.boss.draw_health_bar(self.screen)

        hitbox_status = "LIGADA" if self.show_hitboxes else "DESLIGADA"
        footer_bar = pygame.Surface((SCREEN_WIDTH, 26), pygame.SRCALPHA)
        footer_bar.fill((8, 14, 25, 210))
        self.screen.blit(footer_bar, (0, SCREEN_HEIGHT - 26))

        footer_text = self.font_hud_small.render(
            f"[ WASD / Setas ] Pilotar  |  [ Espaço ] Atirar  |  [ P ] Pausa  |  [ H ] Hitboxes ({hitbox_status})",
            True,
            (160, 175, 200),
        )
        self.screen.blit(footer_text, (20, SCREEN_HEIGHT - 22))

    def render(self) -> None:
        self.screen.fill((10, 14, 26))

        if self.state == self.STATE_MENU:
            self.menu_renderer.draw_main_menu(self.screen, self.current_level, self.credits)

        elif self.state in (self.STATE_PLAYING, self.STATE_PAUSED):
            bx = int(self.bg_base_x)
            self.screen.blit(self.bg_base, (bx, 0))
            self.screen.blit(self.bg_base, (bx + SCREEN_WIDTH, 0))

            if self.bg_overlay:
                ox = int(self.bg_overlay_x)
                self.screen.blit(self.bg_overlay, (ox, 0))
                self.screen.blit(self.bg_overlay, (ox + SCREEN_WIDTH, 0))

            self.player_lasers.draw(self.screen)
            self.enemy_lasers.draw(self.screen)
            self.enemies.draw(self.screen)

            if self.boss and self.boss.alive() and getattr(self.boss, "shield", 0) > 0:
                boss_shield = pygame.Surface((self.boss.rect.width + 36, self.boss.rect.height + 36), pygame.SRCALPHA)
                now_b = pygame.time.get_ticks()
                pulse_b = int(120 + 50 * math.sin(now_b / 120.0))
                pygame.draw.ellipse(boss_shield, (0, 220, 255, pulse_b), boss_shield.get_rect(), 3)
                pygame.draw.ellipse(boss_shield, (140, 70, 240, max(25, pulse_b // 3)), boss_shield.get_rect())
                self.screen.blit(
                    boss_shield,
                    (self.boss.rect.centerx - boss_shield.get_width() // 2, self.boss.rect.centery - boss_shield.get_height() // 2),
                )

            if self.player.shield > 0:
                shield_surf = pygame.Surface((self.player.rect.width + 26, self.player.rect.height + 26), pygame.SRCALPHA)
                now_t = pygame.time.get_ticks()
                pulse = int(110 + 45 * math.sin(now_t / 140.0))
                pygame.draw.ellipse(shield_surf, (0, 220, 255, pulse), shield_surf.get_rect(), 2)
                pygame.draw.ellipse(shield_surf, (0, 180, 240, max(25, pulse // 3)), shield_surf.get_rect())
                self.screen.blit(
                    shield_surf,
                    (self.player.rect.centerx - shield_surf.get_width() // 2, self.player.rect.centery - shield_surf.get_height() // 2),
                )

            self.screen.blit(self.player.image, self.player.rect)
            self.explosions.draw(self.screen)
            self.particles.draw(self.screen)

            if self.show_hitboxes:
                pygame.draw.rect(self.screen, COLOR_GREEN, self.player.hitbox, 2)
                for e in self.enemies:
                    pygame.draw.rect(self.screen, COLOR_RED, e.hitbox, 2)
                for l in self.player_lasers:
                    pygame.draw.rect(self.screen, COLOR_YELLOW, l.hitbox, 1)
                for l in self.enemy_lasers:
                    pygame.draw.rect(self.screen, (255, 140, 0), l.hitbox, 1)

            self.draw_hud()

            if self.state == self.STATE_PAUSED:
                self.menu_renderer.draw_pause_screen(self.screen)

        elif self.state == self.STATE_SHOP:
            self.shop.draw(self.screen, self.player_data, self.current_level)

        elif self.state == self.STATE_LEVEL_COMPLETE:
            completed_info = get_level_info(self.completed_level)
            self.menu_renderer.draw_level_complete_screen(
                self.screen,
                self.completed_level,
                completed_info["credits_reward"],
                self.credits,
            )

        elif self.state == self.STATE_VICTORY:
            self.menu_renderer.draw_victory_screen(self.screen, self.score, self.enemies_killed, self.credits)

        elif self.state == self.STATE_GAME_OVER:
            self.menu_renderer.draw_game_over_screen(self.screen, self.current_level, self.score, self.enemies_killed)

        pygame.display.flip()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif self.state == self.STATE_SHOP:
                action = self.shop.handle_input(
                    event,
                    self.player_data,
                    on_save_callback=self.on_upgrade_purchased,
                )
                if action == "continue":
                    self.load_level(self.current_level)
                elif action == "menu":
                    self.switch_to_menu()

            elif event.type == pygame.KEYDOWN:
                if self.state == self.STATE_MENU:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.load_level(self.current_level)
                    elif event.key == pygame.K_u:
                        self.state = self.STATE_SHOP
                    elif event.key == pygame.K_n:
                        self.reset_campaign()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

                elif self.state == self.STATE_PLAYING:
                    if event.key == pygame.K_p:
                        self.state = self.STATE_PAUSED
                    elif event.key == pygame.K_ESCAPE:
                        self.switch_to_menu()
                    elif event.key == pygame.K_SPACE:
                        self.player.shoot(self.player_lasers)
                    elif event.key == pygame.K_h:
                        self.show_hitboxes = not self.show_hitboxes

                elif self.state == self.STATE_PAUSED:
                    if event.key == pygame.K_p:
                        self.state = self.STATE_PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.switch_to_menu()
                    elif event.key == pygame.K_h:
                        self.show_hitboxes = not self.show_hitboxes

                elif self.state == self.STATE_LEVEL_COMPLETE:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.load_level(self.current_level)
                    elif event.key == pygame.K_u:
                        self.state = self.STATE_SHOP
                    elif event.key == pygame.K_ESCAPE:
                        self.switch_to_menu()

                elif self.state in (self.STATE_VICTORY, self.STATE_GAME_OVER):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.load_level(self.current_level)
                    elif event.key == pygame.K_u:
                        self.state = self.STATE_SHOP
                    elif event.key == pygame.K_ESCAPE:
                        self.switch_to_menu()

    def on_upgrade_purchased(self) -> None:
        self.credits = self.player_data["credits"]
        self.player.apply_upgrades(self.player_data)
        self.save_current_progress()

    def run(self) -> None:
        while self.running:
            self.handle_events()

            if self.state == self.STATE_PLAYING:
                self.update_playing()

            self.render()
            self.clock.tick(FPS)

        self.save_current_progress()
        pygame.quit()
