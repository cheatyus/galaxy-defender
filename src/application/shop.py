import pygame
from src.infrastructure.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_WHITE,
    COLOR_YELLOW,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_CYAN,
    COLOR_BLUE,
    COLOR_BLACK,
    COLOR_GRAY,
)
from src.infrastructure.utils import load_image


UPGRADES_DEFINITION = {
    "damage": {
        "title": "Potência dos Lasers",
        "desc": "Aumenta o dano de impacto de cada disparo de laser.",
        "max_level": 5,
        "costs": {2: 80, 3: 160, 4: 260, 5: 420},
        "values": {1: 25, 2: 40, 3: 60, 4: 85, 5: 120},
        "unit": "Dano",
        "requires": None,
    },
    "health": {
        "title": "Blindagem da Fuselagem",
        "desc": "Aumenta a resistência e os pontos de vida máxima da nave.",
        "max_level": 5,
        "costs": {2: 60, 3: 130, 4: 220, 5: 360},
        "values": {1: 100, 2: 140, 3: 190, 4: 250, 5: 320},
        "unit": "Vida",
        "requires": None,
    },
    "shield": {
        "title": "Escudo de Plasma",
        "desc": "Barreira defletora que absorve danos e regenera fora de combate.",
        "max_level": 3,
        "costs": {1: 120, 2: 240, 3: 400},
        "values": {0: 0, 1: 40, 2: 80, 3: 130},
        "unit": "Escudo",
        "requires": None,
    },
    "firerate": {
        "title": "Cadência dos Canhões",
        "desc": "Reduz o intervalo de recarga para disparos mais frequentes.",
        "max_level": 5,
        "costs": {2: 90, 3: 180, 4: 300, 5: 450},
        "values": {1: 200, 2: 160, 3: 125, 4: 95, 5: 70},
        "unit": "ms",
        "requires": None,
    },
    "speed": {
        "title": "Propulsores Vetoriais",
        "desc": "Aumenta a velocidade de esquiva e manobra da nave.",
        "max_level": 5,
        "costs": {2: 50, 3: 110, 4: 190, 5: 300},
        "values": {1: 6.0, 2: 7.2, 3: 8.4, 4: 9.6, 5: 11.0},
        "unit": "Vel.",
        "requires": None,
    },
    "double_cannon": {
        "title": "Canhão Duplo Paralelo",
        "desc": "Dispara 2 feixes de laser paralelos simultaneamente.",
        "max_level": 1,
        "costs": {1: 320},
        "values": {0: 0, 1: 1},
        "unit": "Duplo",
        "requires": None,
    },
    "triple_cannon": {
        "title": "Canhão Tríplice em Cone",
        "desc": "Dispara 3 lasers com dispersão angular ampla em cone.",
        "max_level": 1,
        "costs": {1: 500},
        "values": {0: 0, 1: 1},
        "unit": "Tríplice",
        "requires": "double_cannon",
    },
    "magnet": {
        "title": "Coletor de Sucata & Bônus",
        "desc": "Converte destroços de naves abatidas em créditos extras.",
        "max_level": 3,
        "costs": {1: 100, 2: 220, 3: 380},
        "values": {0: 0, 1: 35, 2: 75, 3: 120},
        "unit": "% Bônus",
        "requires": None,
    },
}


class Shop:

    def __init__(self):
        self.bg_image = load_image("asset/ScoreBg.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font_title = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 14)
        self.font_balance = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_card_title = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_card_desc = pygame.font.SysFont("Arial", 13)
        self.font_card_stat = pygame.font.SysFont("Arial", 13, bold=True)
        self.font_badge = pygame.font.SysFont("Arial", 12, bold=True)
        self.font_btn = pygame.font.SysFont("Arial", 14, bold=True)
        self.font_prompt = pygame.font.SysFont("Arial", 17, bold=True)
        self.font_subprompt = pygame.font.SysFont("Arial", 13)

        self.upgrade_keys = [
            "damage",
            "health",
            "shield",
            "firerate",
            "speed",
            "double_cannon",
            "triple_cannon",
            "magnet",
        ]
        self.selected_index = 0
        self.card_rects = []
        self.continue_btn_rect = pygame.Rect((SCREEN_WIDTH - 540) // 2, 495, 540, 44)

    def get_current_level(self, key: str, player_stats: dict) -> int:
        if key in ("double_cannon", "triple_cannon"):
            return 1 if player_stats.get(key, False) else 0
        default_lvl = 0 if key in ("shield", "magnet") else 1
        return player_stats.get(f"{key}_level", default_lvl)

    def is_locked(self, key: str, player_stats: dict) -> bool:
        req = UPGRADES_DEFINITION[key].get("requires")
        if req:
            return not bool(player_stats.get(req, False))
        return False

    def handle_input(self, event: pygame.event.Event, player_stats: dict, on_save_callback) -> str | None:
        if event.type == pygame.MOUSEMOTION:
            for idx, r in enumerate(self.card_rects):
                if r.collidepoint(event.pos):
                    self.selected_index = idx
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.continue_btn_rect.collidepoint(event.pos):
                return "continue"

            for idx, r in enumerate(self.card_rects):
                if r.collidepoint(event.pos):
                    self.selected_index = idx
                    key = self.upgrade_keys[self.selected_index]
                    self.try_buy_upgrade(key, player_stats, on_save_callback)
                    break

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                col = self.selected_index // 4
                row = self.selected_index % 4
                row = (row - 1) % 4
                self.selected_index = col * 4 + row

            elif event.key in (pygame.K_DOWN, pygame.K_s):
                col = self.selected_index // 4
                row = self.selected_index % 4
                row = (row + 1) % 4
                self.selected_index = col * 4 + row

            elif event.key in (pygame.K_LEFT, pygame.K_a):
                if self.selected_index >= 4:
                    self.selected_index -= 4

            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if self.selected_index < 4:
                    self.selected_index += 4

            elif event.key in (pygame.K_RETURN, pygame.K_e):
                key = self.upgrade_keys[self.selected_index]
                self.try_buy_upgrade(key, player_stats, on_save_callback)

            elif event.key == pygame.K_SPACE:
                return "continue"

            elif event.key == pygame.K_ESCAPE:
                return "menu"

        return None

    def try_buy_upgrade(self, key: str, player_stats: dict, on_save_callback) -> bool:
        info = UPGRADES_DEFINITION[key]

        if self.is_locked(key, player_stats):
            return False

        curr_level = self.get_current_level(key, player_stats)
        if curr_level >= info["max_level"]:
            return False

        next_level = curr_level + 1
        cost = info["costs"].get(next_level, 0)

        if player_stats.get("credits", 0) >= cost:
            player_stats["credits"] -= cost
            if key in ("double_cannon", "triple_cannon"):
                player_stats[key] = True
            else:
                player_stats[f"{key}_level"] = next_level

            if on_save_callback:
                on_save_callback()
            return True

        return False

    def draw(self, surface: pygame.Surface, player_stats: dict, current_level: int) -> None:
        surface.blit(self.bg_image, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 14, 26, 230))
        surface.blit(overlay, (0, 0))

        title_surf = self.font_title.render("HANGAR DE ENGENHARIA & UPGRADES", True, COLOR_CYAN)
        surface.blit(title_surf, ((SCREEN_WIDTH - title_surf.get_width()) // 2, 16))

        sub_surf = self.font_subtitle.render(
            "Aprimore os sistemas de bordo da nave utilizando os créditos obtidos nas missões",
            True,
            (170, 185, 210),
        )
        surface.blit(sub_surf, ((SCREEN_WIDTH - sub_surf.get_width()) // 2, 48))

        credits_val = player_stats.get("credits", 0)
        credits_str = f"CRÉDITOS DISPONÍVEIS: {credits_val} CR"
        pill_text = self.font_balance.render(credits_str, True, COLOR_YELLOW)
        pill_w = pill_text.get_width() + 32
        pill_h = 32
        pill_x = (SCREEN_WIDTH - pill_w) // 2
        pill_y = 68

        pill_bg = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pill_bg.fill((22, 34, 56, 220))
        surface.blit(pill_bg, (pill_x, pill_y))
        pygame.draw.rect(surface, (241, 196, 15), (pill_x, pill_y, pill_w, pill_h), 1, border_radius=16)
        surface.blit(pill_text, (pill_x + 16, pill_y + 5))

        pygame.draw.line(surface, (30, 50, 80), (35, 108), (SCREEN_WIDTH - 35, 108), 1)

        col_w = 460
        card_h = 82
        left_x = 36
        right_x = 528
        start_y = 120
        gap_y = 92

        self.card_rects = []

        for i, key in enumerate(self.upgrade_keys):
            info = UPGRADES_DEFINITION[key]
            col = i // 4
            row = i % 4
            cx = left_x if col == 0 else right_x
            cy = start_y + (row * gap_y)

            card_rect = pygame.Rect(cx, cy, col_w, card_h)
            self.card_rects.append(card_rect)

            is_selected = i == self.selected_index
            locked = self.is_locked(key, player_stats)
            curr_lvl = self.get_current_level(key, player_stats)
            is_max = curr_lvl >= info["max_level"]
            next_lvl = curr_lvl + 1
            cost = info["costs"].get(next_lvl, 0)
            can_afford = (not is_max) and (not locked) and (credits_val >= cost)

            card_surface = pygame.Surface((col_w, card_h), pygame.SRCALPHA)
            if is_selected:
                card_surface.fill((24, 40, 68, 240))
                border_color = (0, 220, 255) if can_afford or is_max else (241, 196, 15)
                border_w = 2
            else:
                card_surface.fill((14, 22, 36, 205))
                border_color = (40, 58, 85)
                border_w = 1

            surface.blit(card_surface, (cx, cy))
            pygame.draw.rect(surface, border_color, card_rect, border_w, border_radius=8)

            title_color = COLOR_WHITE if not is_selected else (255, 255, 140)
            t_surf = self.font_card_title.render(info["title"], True, title_color)
            surface.blit(t_surf, (cx + 12, cy + 8))

            if info["max_level"] > 1:
                pip_w = 10
                pip_h = 6
                pip_gap = 4
                total_pips = info["max_level"]
                pip_start_x = cx + col_w - 12 - (total_pips * (pip_w + pip_gap))
                pip_y = cy + 12

                for p in range(1, total_pips + 1):
                    px = pip_start_x + (p - 1) * (pip_w + pip_gap)
                    p_rect = pygame.Rect(px, pip_y, pip_w, pip_h)
                    if p <= curr_lvl:
                        pygame.draw.rect(surface, (0, 220, 180), p_rect, border_radius=2)
                    else:
                        pygame.draw.rect(surface, (45, 60, 80), p_rect, border_radius=2)
                        pygame.draw.rect(surface, (70, 90, 120), p_rect, 1, border_radius=2)

                lvl_tag = f"LVL {curr_lvl}/{info['max_level']}"
                tag_surf = self.font_badge.render(lvl_tag, True, (160, 185, 215))
                surface.blit(tag_surf, (pip_start_x - tag_surf.get_width() - 8, cy + 9))

            else:
                if curr_lvl == 1:
                    status_str = "INSTALADO"
                    status_col = (46, 204, 113)
                elif locked:
                    status_str = "REQUER DUPLO"
                    status_col = (231, 76, 60)
                else:
                    status_str = "DISPONÍVEL"
                    status_col = (241, 196, 15)

                b_surf = self.font_badge.render(status_str, True, status_col)
                surface.blit(b_surf, (cx + col_w - b_surf.get_width() - 14, cy + 10))

            desc_surf = self.font_card_desc.render(info["desc"], True, (155, 175, 200))
            surface.blit(desc_surf, (cx + 12, cy + 30))

            if locked:
                stat_str = "Necessita de Canhão Duplo prévio instalado."
                stat_col = (220, 90, 90)
                btn_str = "[ BLOQUEADO ]"
                btn_col = COLOR_GRAY
            elif is_max:
                curr_val = info["values"].get(curr_lvl, curr_lvl)
                stat_str = f"Capacidade Máxima: {curr_val} {info['unit']}"
                stat_col = (46, 204, 113)
                btn_str = "[ MAX ]"
                btn_col = (46, 204, 113)
            else:
                curr_val = info["values"].get(curr_lvl, 0)
                next_val = info["values"].get(next_lvl, next_lvl)
                if key in ("double_cannon", "triple_cannon"):
                    stat_str = "Desbloqueia novo padrão de disparo balístico"
                elif key == "firerate":
                    stat_str = f"{curr_val}ms -> {next_val}ms (-{curr_val - next_val}ms recarga)"
                else:
                    diff = next_val - curr_val
                    stat_str = f"{curr_val} -> {next_val} {info['unit']} (+{diff})"
                stat_col = (0, 220, 255)

                if can_afford:
                    btn_str = f"[ COMPRAR: {cost} CR ]"
                    btn_col = COLOR_YELLOW
                else:
                    btn_str = f"[ {cost} CR ]"
                    btn_col = (140, 150, 165)

            s_surf = self.font_card_stat.render(stat_str, True, stat_col)
            surface.blit(s_surf, (cx + 12, cy + 52))

            btn_surf = self.font_btn.render(btn_str, True, btn_col)
            surface.blit(btn_surf, (cx + col_w - btn_surf.get_width() - 12, cy + 50))

        btn_r = self.continue_btn_rect
        btn_surf = pygame.Surface((btn_r.width, btn_r.height), pygame.SRCALPHA)
        btn_surf.fill((20, 48, 38, 230))
        surface.blit(btn_surf, (btn_r.x, btn_r.y))
        pygame.draw.rect(surface, (46, 204, 113), btn_r, 2, border_radius=8)

        if current_level >= 10:
            prompt_str = "CONFRONTAR CHEFE FINAL (FASE 10)"
        else:
            prompt_str = f"DECOLAR PARA O SETOR {current_level}"

        full_prompt = f"Pressione [ ESPAÇO ] ou Clique para {prompt_str}"
        p_surf = self.font_prompt.render(full_prompt, True, (46, 204, 113))
        surface.blit(p_surf, (btn_r.x + (btn_r.width - p_surf.get_width()) // 2, btn_r.y + 11))

        help_str = "[ W/A/S/D ou Setas ] Navegar  |  [ ENTER / Clique ] Comprar  |  [ ESPAÇO ] Decolar  |  [ ESC ] Menu"
        h_surf = self.font_subprompt.render(help_str, True, (150, 170, 195))
        surface.blit(h_surf, ((SCREEN_WIDTH - h_surf.get_width()) // 2, 555))
