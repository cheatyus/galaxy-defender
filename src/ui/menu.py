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


class MenuRenderer:

    def __init__(self):
        self.bg_image = load_image("asset/MenuBg.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.font_title = pygame.font.SysFont("Arial", 44, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_heading = pygame.font.SysFont("Arial", 19, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 17)
        self.font_prompt = pygame.font.SysFont("Arial", 19, bold=True)

    def draw_text(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        center: tuple[int, int],
        shadow: bool = True,
    ) -> None:
        if shadow:
            shadow_surface = font.render(text, True, COLOR_BLACK)
            shadow_rect = shadow_surface.get_rect(center=(center[0] + 2, center[1] + 2))
            surface.blit(shadow_surface, shadow_rect)

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center)
        surface.blit(text_surface, text_rect)

    def draw_main_menu(self, surface: pygame.Surface, current_level: int = 1, credits: int = 0) -> None:
        surface.blit(self.bg_image, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 14, 25, 205))
        surface.blit(overlay, (0, 0))

        self.draw_text(surface, "GALAXY DEFENDER", self.font_title, COLOR_CYAN, (SCREEN_WIDTH // 2, 42))
        self.draw_text(
            surface,
            "Campanha de 10 Fases - Upgrades Avançados - SQLite Local - Projeto LPA",
            self.font_subtitle,
            COLOR_WHITE,
            (SCREEN_WIDTH // 2, 82),
        )

        panel_width = 740
        panel_height = 200
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = 112

        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surf.fill((13, 21, 36, 230))
        surface.blit(panel_surf, (panel_x, panel_y))
        pygame.draw.rect(surface, (0, 180, 230), (panel_x, panel_y, panel_width, panel_height), 2, border_radius=10)

        self.draw_text(
            surface,
            "COMANDOS DE PILOTAGEM E CONTROLE",
            self.font_heading,
            COLOR_YELLOW,
            (SCREEN_WIDTH // 2, panel_y + 18),
        )

        commands = [
            ("W / A / S / D  ou  SETAS", "Manobras direcionais da nave"),
            ("BARRA DE ESPAÇO", "Disparos de laser e canhões"),
            ("TECLA P", "Pausar / Retomar combate"),
            ("TECLA H", "Alternar Hitboxes de depuração"),
            ("TECLA ESC", "Retornar ao Menu Principal"),
        ]

        curr_y = panel_y + 44
        for key_text, desc_text in commands:
            keycap_rect = pygame.Rect(panel_x + 30, curr_y, 230, 24)
            pygame.draw.rect(surface, (22, 34, 56), keycap_rect, border_radius=5)
            pygame.draw.rect(surface, (0, 200, 240), keycap_rect, 1, border_radius=5)

            k_surf = self.font_text.render(key_text, True, COLOR_CYAN)
            surface.blit(k_surf, (keycap_rect.centerx - k_surf.get_width() // 2, keycap_rect.centery - k_surf.get_height() // 2))

            d_surf = self.font_text.render(f">>  {desc_text}", True, COLOR_WHITE)
            surface.blit(d_surf, (panel_x + 280, curr_y + 3))
            curr_y += 29

        info_y = 328
        info_h = 74
        info_surf = pygame.Surface((panel_width, info_h), pygame.SRCALPHA)
        info_surf.fill((13, 21, 36, 220))
        surface.blit(info_surf, (panel_x, info_y))
        pygame.draw.rect(surface, (46, 204, 113), (panel_x, info_y, panel_width, info_h), 1, border_radius=8)

        self.draw_text(
            surface,
            "BANCO DE DADOS LOCAL CARREGADO (data/savegame.db - SQLite 3)",
            self.font_heading,
            COLOR_GREEN,
            (SCREEN_WIDTH // 2, info_y + 18),
        )
        self.draw_text(
            surface,
            f"Setor Atual: Fase {current_level} / 10   |   Créditos Disponíveis: {credits} CR",
            self.font_text,
            COLOR_YELLOW,
            (SCREEN_WIDTH // 2, info_y + 45),
        )

        menu_options_y = 422

        btn1_rect = pygame.Rect(panel_x + 60, menu_options_y, panel_width - 120, 38)
        btn1_surf = pygame.Surface((btn1_rect.width, btn1_rect.height), pygame.SRCALPHA)
        btn1_surf.fill((20, 48, 38, 220))
        surface.blit(btn1_surf, (btn1_rect.x, btn1_rect.y))
        pygame.draw.rect(surface, (46, 204, 113), btn1_rect, 2, border_radius=8)

        btn_continue_text = f"Pressione [ ENTER ] para CONTINUAR (Fase {current_level})" if current_level > 1 else "Pressione [ ENTER ] para INICIAR CAMPANHA (Fase 1)"
        self.draw_text(surface, btn_continue_text, self.font_prompt, (46, 204, 113), btn1_rect.center)

        btn2_rect = pygame.Rect(panel_x + 60, menu_options_y + 48, panel_width - 120, 38)
        btn2_surf = pygame.Surface((btn2_rect.width, btn2_rect.height), pygame.SRCALPHA)
        btn2_surf.fill((45, 40, 20, 220))
        surface.blit(btn2_surf, (btn2_rect.x, btn2_rect.y))
        pygame.draw.rect(surface, (241, 196, 15), btn2_rect, 2, border_radius=8)
        self.draw_text(surface, "Pressione [ U ] para abrir o HANGAR DE UPGRADES", self.font_prompt, COLOR_YELLOW, btn2_rect.center)

        self.draw_text(
            surface,
            "Pressione [ N ] para NOVO JOGO (Resetar Save)   |   [ ESC ] para Sair",
            self.font_text,
            (160, 175, 200),
            (SCREEN_WIDTH // 2, menu_options_y + 104),
        )

    def draw_level_complete_screen(self, surface: pygame.Surface, completed_level: int, credits_reward: int, total_credits: int) -> None:
        surface.blit(self.bg_image, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 18, 30, 220))
        surface.blit(overlay, (0, 0))

        box_w, box_h = 740, 360
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = 130
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((14, 24, 40, 240))
        surface.blit(box_surf, (box_x, box_y))
        pygame.draw.rect(surface, (0, 210, 240), (box_x, box_y, box_w, box_h), 2, border_radius=12)

        self.draw_text(
            surface,
            f"SETOR {completed_level} CONQUISTADO!",
            self.font_title,
            COLOR_CYAN,
            (SCREEN_WIDTH // 2, box_y + 40),
        )
        self.draw_text(
            surface,
            f"+ {credits_reward} Créditos espaciais obtidos nesta missão!",
            self.font_heading,
            COLOR_YELLOW,
            (SCREEN_WIDTH // 2, box_y + 85),
        )
        self.draw_text(
            surface,
            f"Saldo Total no Cofre: {total_credits} CR   |   Progresso salvo no SQLite (data/savegame.db)",
            self.font_text,
            (180, 205, 230),
            (SCREEN_WIDTH // 2, box_y + 122),
        )

        btn_h_rect = pygame.Rect(box_x + 60, box_y + 170, box_w - 120, 38)
        btn_h_surf = pygame.Surface((btn_h_rect.width, btn_h_rect.height), pygame.SRCALPHA)
        btn_h_surf.fill((45, 40, 18, 220))
        surface.blit(btn_h_surf, (btn_h_rect.x, btn_h_rect.y))
        pygame.draw.rect(surface, COLOR_YELLOW, btn_h_rect, 1, border_radius=6)
        self.draw_text(surface, "Pressione [ U ] para Acessar o HANGAR DE UPGRADES", self.font_prompt, COLOR_YELLOW, btn_h_rect.center)

        next_target = completed_level + 1
        next_str = "CONFRONTAR CHEFE FINAL (FASE 10)" if next_target >= 10 else f"AVANÇAR PARA A FASE {next_target}"
        btn_n_rect = pygame.Rect(box_x + 60, box_y + 220, box_w - 120, 40)
        btn_n_surf = pygame.Surface((btn_n_rect.width, btn_n_rect.height), pygame.SRCALPHA)
        btn_n_surf.fill((20, 50, 38, 225))
        surface.blit(btn_n_surf, (btn_n_rect.x, btn_n_rect.y))
        pygame.draw.rect(surface, (46, 204, 113), btn_n_rect, 2, border_radius=6)
        self.draw_text(surface, f"Pressione [ ENTER ] para {next_str}", self.font_prompt, (46, 204, 113), btn_n_rect.center)

        self.draw_text(
            surface,
            "Pressione [ ESC ] para Retornar ao Menu Principal",
            self.font_text,
            (150, 170, 195),
            (SCREEN_WIDTH // 2, box_y + 300),
        )

    def draw_victory_screen(self, surface: pygame.Surface, score: int, enemies_killed: int, credits: int) -> None:
        surface.blit(self.bg_image, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 28, 18, 230))
        surface.blit(overlay, (0, 0))

        box_w, box_h = 760, 390
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = 115
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((14, 34, 24, 245))
        surface.blit(box_surf, (box_x, box_y))
        pygame.draw.rect(surface, (46, 204, 113), (box_x, box_y, box_w, box_h), 2, border_radius=12)

        self.draw_text(
            surface,
            "* VITORIA SUPREMA! *",
            self.font_title,
            COLOR_YELLOW,
            (SCREEN_WIDTH // 2, box_y + 42),
        )
        self.draw_text(
            surface,
            "O DREADNOUGHT MÃE FOI DESTRUÍDO! A GALÁXIA ESTÁ A SALVO!",
            self.font_subtitle,
            (46, 204, 113),
            (SCREEN_WIDTH // 2, box_y + 85),
        )

        self.draw_text(
            surface,
            "Todas as 10 Fases da Campanha foram Concluídas com Sucesso!",
            self.font_heading,
            COLOR_WHITE,
            (SCREEN_WIDTH // 2, box_y + 128),
        )
        self.draw_text(
            surface,
            f"Pontuação Final: {score} pts   |   Inimigos Abatidos: {enemies_killed}   |   Créditos: {credits} CR",
            self.font_text,
            COLOR_CYAN,
            (SCREEN_WIDTH // 2, box_y + 168),
        )

        btn_r = pygame.Rect(box_x + 70, box_y + 225, box_w - 140, 44)
        btn_surf = pygame.Surface((btn_r.width, btn_r.height), pygame.SRCALPHA)
        btn_surf.fill((20, 52, 38, 230))
        surface.blit(btn_surf, (btn_r.x, btn_r.y))
        pygame.draw.rect(surface, (46, 204, 113), btn_r, 2, border_radius=8)
        self.draw_text(surface, "Pressione [ ENTER ] para Iniciar Nova Campanha", self.font_prompt, (46, 204, 113), btn_r.center)

        self.draw_text(
            surface,
            "Pressione [ ESC ] para Retornar ao Menu Principal",
            self.font_text,
            (160, 180, 200),
            (SCREEN_WIDTH // 2, box_y + 320),
        )

    def draw_game_over_screen(self, surface: pygame.Surface, current_level: int, score: int, enemies_killed: int) -> None:
        surface.blit(self.bg_image, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((30, 8, 8, 230))
        surface.blit(overlay, (0, 0))

        box_w, box_h = 740, 370
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = 125
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((34, 14, 16, 245))
        surface.blit(box_surf, (box_x, box_y))
        pygame.draw.rect(surface, (231, 76, 60), (box_x, box_y, box_w, box_h), 2, border_radius=12)

        self.draw_text(
            surface,
            "* GAME OVER *",
            self.font_title,
            COLOR_RED,
            (SCREEN_WIDTH // 2, box_y + 40),
        )
        self.draw_text(
            surface,
            f"SUA NAVE FOI DESTRUÍDA NO SETOR {current_level}!",
            self.font_subtitle,
            COLOR_WHITE,
            (SCREEN_WIDTH // 2, box_y + 82),
        )

        self.draw_text(
            surface,
            f"Pontuação: {score} pontos   |   Inimigos Abatidos: {enemies_killed}",
            self.font_text,
            COLOR_YELLOW,
            (SCREEN_WIDTH // 2, box_y + 126),
        )
        self.draw_text(
            surface,
            "Dica de Piloto: Use o Hangar para desbloquear Escudo de Plasma e Canhões!",
            self.font_text,
            (0, 210, 240),
            (SCREEN_WIDTH // 2, box_y + 158),
        )

        btn1 = pygame.Rect(box_x + 60, box_y + 205, box_w - 120, 38)
        btn1_surf = pygame.Surface((btn1.width, btn1.height), pygame.SRCALPHA)
        btn1_surf.fill((50, 42, 18, 220))
        surface.blit(btn1_surf, (btn1.x, btn1.y))
        pygame.draw.rect(surface, COLOR_YELLOW, btn1, 2, border_radius=6)
        self.draw_text(surface, f"Pressione [ ENTER ] para Repetir a Fase {current_level}", self.font_prompt, COLOR_YELLOW, btn1.center)

        btn2 = pygame.Rect(box_x + 60, box_y + 252, box_w - 120, 36)
        btn2_surf = pygame.Surface((btn2.width, btn2.height), pygame.SRCALPHA)
        btn2_surf.fill((20, 46, 36, 220))
        surface.blit(btn2_surf, (btn2.x, btn2.y))
        pygame.draw.rect(surface, (46, 204, 113), btn2, 1, border_radius=6)
        self.draw_text(surface, "Pressione [ U ] para Abrir o Hangar de Upgrades", self.font_prompt, (46, 204, 113), btn2.center)

        self.draw_text(
            surface,
            "Pressione [ ESC ] para Retornar ao Menu Principal",
            self.font_text,
            (160, 175, 195),
            (SCREEN_WIDTH // 2, box_y + 325),
        )

    def draw_pause_screen(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        surface.blit(overlay, (0, 0))

        box_w, box_h = 500, 220
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2

        p_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        p_surf.fill((12, 18, 30, 230))
        surface.blit(p_surf, (box_x, box_y))
        pygame.draw.rect(surface, (0, 200, 240), (box_x, box_y, box_w, box_h), 2, border_radius=10)

        self.draw_text(surface, "SISTEMA PAUSADO", self.font_title, COLOR_YELLOW, (SCREEN_WIDTH // 2, box_y + 40))
        self.draw_text(
            surface,
            "Pressione [ P ] para Retomar a Missão",
            self.font_prompt,
            (46, 204, 113),
            (SCREEN_WIDTH // 2, box_y + 110),
        )
        self.draw_text(
            surface,
            "Pressione [ ESC ] para Abortar e Voltar ao Menu",
            self.font_text,
            (160, 180, 205),
            (SCREEN_WIDTH // 2, box_y + 155),
        )
