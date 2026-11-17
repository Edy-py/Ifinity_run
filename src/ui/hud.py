import pygame
from config import (
    COLOR_TEXT,
    COLOR_TEXT_SHADOW,
    COLOR_GOLD,
    MAX_WEIGHT,
    STATE_PLAYING,
    STATE_PAUSED,
    STATE_GAME_OVER,
)
from game_state import GameState
from ui.menu import MenuButton


class HUD:
    """Renderiza o cabeçalho polido (com cache de barra e botão de pausa), Pausa e Game Over."""

    def __init__(self):
        pygame.font.init()
        self.font_small = pygame.font.SysFont("Segoe UI", 17, bold=True)
        self.font_pause_btn = pygame.font.SysFont("Segoe UI", 15, bold=True)
        self.font_main = pygame.font.SysFont("Segoe UI", 21, bold=True)
        self.font_pause_title = pygame.font.SysFont("Segoe UI", 40, bold=True)
        self.font_pause_menu_btn = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.font_score_val = pygame.font.SysFont("Segoe UI", 29, bold=True)
        self.font_game_over = pygame.font.SysFont("Segoe UI", 54, bold=True)
        self.font_restart = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.font_hint = pygame.font.SysFont("Segoe UI", 15, bold=False)

        self.top_bar_height = 88
        self._cached_size: tuple[int, int] | None = None
        self.top_bar_surface: pygame.Surface | None = None
        self.overlay_surface: pygame.Surface | None = None

        self._cached_bar_dims: tuple[int, int] | None = None
        self._gradient_bar_surface: pygame.Surface | None = None
        self._cached_bar_state: tuple[int, int, int] | None = None
        self._cached_bar_render: pygame.Surface | None = None

        # Botão de pausa no cabeçalho do HUD e botões do Menu de Pausa
        self.btn_hud_pause = MenuButton(
            text="|| PAUSAR (P)",
            base_color=(52, 73, 94),
            hover_color=(72, 102, 132),
            border_color=(220, 230, 245),
            width=148,
            height=40,
        )
        self.btn_resume = MenuButton(
            text="CONTINUAR (P)",
            base_color=(46, 204, 113),
            hover_color=(62, 224, 130),
            border_color=(255, 255, 255),
            width=310,
            height=58,
        )
        self.btn_restart = MenuButton(
            text="REINICIAR",
            base_color=(52, 152, 219),
            hover_color=(72, 172, 239),
            border_color=(255, 255, 255),
            width=310,
            height=54,
        )
        self.btn_menu = MenuButton(
            text="MENU INICIAL",
            base_color=(230, 126, 34),
            hover_color=(245, 146, 54),
            border_color=(255, 255, 255),
            width=310,
            height=54,
        )

    def _ensure_surfaces(self, size: tuple[int, int]):
        """Recria as superfícies translúcidas quando a resolução muda."""
        if self._cached_size != size:
            self._cached_size = size
            w, h = size
            self.top_bar_surface = pygame.Surface((w, self.top_bar_height), pygame.SRCALPHA)
            self.top_bar_surface.fill((16, 20, 30, 215))

            self.overlay_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            self.overlay_surface.fill((10, 12, 18, 200))

    def _ensure_gradient_bar(self, width: int, height: int):
        """Pré-renderiza o gradiente suave Verde -> Amarelo -> Vermelho da barra de peso."""
        if self._cached_bar_dims == (width, height) and self._gradient_bar_surface is not None:
            return

        self._cached_bar_dims = (width, height)
        grad = pygame.Surface((width, height), pygame.SRCALPHA)
        green = (46, 204, 113)
        yellow = (241, 196, 15)
        red = (231, 76, 60)

        for x in range(width):
            t = x / max(1, width - 1)
            if t < 0.5:
                col = self._lerp_color(green, yellow, t * 2.0)
            else:
                col = self._lerp_color(yellow, red, (t - 0.5) * 2.0)
            pygame.draw.line(grad, col, (x, 0), (x, height - 1))

        self._gradient_bar_surface = grad

    @staticmethod
    def _lerp_color(
        c1: tuple[int, int, int], c2: tuple[int, int, int], t: float
    ) -> tuple[int, int, int]:
        """Interpola linearmente entre duas cores RGB."""
        t = max(0.0, min(1.0, t))
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        )

    def get_weight_bar_color(self, ratio: float) -> tuple[int, int, int]:
        """Transiciona do verde (0.0) -> amarelo (0.5) -> vermelho (1.0)."""
        green = (46, 204, 113)
        yellow = (241, 196, 15)
        red = (231, 76, 60)
        if ratio < 0.5:
            return self._lerp_color(green, yellow, ratio * 2.0)
        return self._lerp_color(yellow, red, (ratio - 0.5) * 2.0)

    def update(
        self,
        screen_size: tuple[int, int],
        mouse_pos: tuple[int, int],
        game_state: GameState,
    ):
        """Atualiza o posicionamento e hover do botão de pausa e dos botões do menu de pausa."""
        w, h = screen_size
        cx = w // 2
        cy = h // 2

        if game_state.state == STATE_PLAYING:
            self.btn_hud_pause.update((cx, self.top_bar_height // 2), mouse_pos)
        elif game_state.state == STATE_PAUSED:
            self.btn_resume.update((cx, cy - 20), mouse_pos)
            self.btn_restart.update((cx, cy + 54), mouse_pos)
            self.btn_menu.update((cx, cy + 124), mouse_pos)

    def handle_event(
        self, event: pygame.event.Event, game_state: GameState
    ) -> str | None:
        """Processa cliques e atalhos relacionados à pausa durante o jogo."""
        if game_state.state == STATE_PLAYING:
            if self.btn_hud_pause.is_clicked(event):
                return "PAUSE"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                return "PAUSE"

        elif game_state.state == STATE_PAUSED:
            if self.btn_resume.is_clicked(event):
                return "RESUME"
            if self.btn_restart.is_clicked(event):
                return "RESTART"
            if self.btn_menu.is_clicked(event):
                return "MENU"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_p, pygame.K_SPACE):
                    return "RESUME"
                if event.key == pygame.K_r:
                    return "RESTART"
                if event.key == pygame.K_m:
                    return "MENU"

        return None

    def _draw_text_with_shadow(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        pos: tuple[int, int],
        align: str = "topleft",
    ):
        """Desenha texto com sombra para máxima legibilidade."""
        text_surf = font.render(text, True, color)
        shadow_surf = font.render(text, True, COLOR_TEXT_SHADOW)

        rect = text_surf.get_rect()
        setattr(rect, align, pos)

        shadow_rect = rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2

        surface.blit(shadow_surf, shadow_rect)
        surface.blit(text_surf, rect)

    def _draw_weight_icon(
        self, surface: pygame.Surface, cx: int, cy: int, color: tuple[int, int, int]
    ):
        """Desenha um ícone vetorial estilizado de coração de saúde/balança."""
        pygame.draw.circle(surface, (28, 34, 48), (cx, cy), 18)
        pygame.draw.circle(surface, color, (cx, cy), 18, width=2)

        pygame.draw.circle(surface, color, (cx - 4, cy - 2), 5)
        pygame.draw.circle(surface, color, (cx + 4, cy - 2), 5)
        pygame.draw.polygon(
            surface,
            color,
            [(cx - 9, cy), (cx + 9, cy), (cx, cy + 10)],
        )
        pygame.draw.lines(
            surface,
            (255, 255, 255),
            False,
            [(cx - 7, cy + 1), (cx - 2, cy + 1), (cx, cy - 4), (cx + 2, cy + 4), (cx + 6, cy + 1)],
            2,
        )

    def _draw_apple_icon(self, surface: pygame.Surface, cx: int, cy: int):
        """Desenha um ícone vetorial estilizado de maçã verde/dourada brilhante."""
        pygame.draw.circle(surface, (28, 34, 48), (cx, cy), 18)
        pygame.draw.circle(surface, (255, 215, 0), (cx, cy), 18, width=2)

        pygame.draw.circle(surface, (46, 204, 113), (cx - 4, cy + 2), 7)
        pygame.draw.circle(surface, (46, 204, 113), (cx + 4, cy + 2), 7)
        pygame.draw.circle(surface, (125, 255, 140), (cx - 4, cy), 3)
        pygame.draw.line(surface, (180, 120, 60), (cx, cy - 4), (cx + 1, cy - 10), 2)
        pygame.draw.polygon(
            surface, (255, 215, 0), [(cx + 1, cy - 9), (cx + 9, cy - 11), (cx + 7, cy - 4)]
        )

    def _draw_gradient_weight_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        ratio: float,
    ):
        """Desenha a barra de peso usando cache por (width, height, fill_width)."""
        self._ensure_gradient_bar(width, height)

        visual_ratio = max(0.14, min(1.0, ratio))
        fill_width = max(16, min(width, int(width * visual_ratio)))
        state_key = (width, height, fill_width)

        if self._cached_bar_state != state_key or self._cached_bar_render is None:
            self._cached_bar_state = state_key
            pad = 4
            bar_surf = pygame.Surface((width + pad * 2, height + pad * 2), pygame.SRCALPHA)
            bg_rect = pygame.Rect(pad, pad, width, height)

            # Sombra 3D e fundo escuro
            pygame.draw.rect(bar_surf, (8, 10, 16), bg_rect.move(0, 3), border_radius=12)
            pygame.draw.rect(bar_surf, (36, 40, 54), bg_rect, border_radius=12)

            # Máscara arredondada para o gradiente
            fill_surf = pygame.Surface((fill_width, height), pygame.SRCALPHA)
            pygame.draw.rect(
                fill_surf,
                (255, 255, 255, 255),
                pygame.Rect(0, 0, fill_width, height),
                border_radius=10,
            )
            grad_slice = self._gradient_bar_surface.subsurface((0, 0, fill_width, height))
            fill_surf.blit(grad_slice, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            bar_surf.blit(fill_surf, (pad, pad))

            # Reflexo superior branco translúcido (glossy)
            gloss_rect = pygame.Rect(
                pad + 4, pad + 3, max(8, fill_width - 8), max(4, height // 3)
            )
            gloss_surf = pygame.Surface(gloss_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                gloss_surf, (255, 255, 255, 65), gloss_surf.get_rect(), border_radius=6
            )
            bar_surf.blit(gloss_surf, gloss_rect.topleft)

            # Contorno escuro externo + borda grossa clara
            pygame.draw.rect(
                bar_surf, (15, 18, 26), bg_rect.inflate(4, 4), width=2, border_radius=13
            )
            pygame.draw.rect(bar_surf, (235, 240, 250), bg_rect, width=3, border_radius=12)

            self._cached_bar_render = bar_surf

        surface.blit(self._cached_bar_render, (x - 4, y - 4))

    def draw(self, surface: pygame.Surface, game_state: GameState):
        """Renderiza o HUD superior, botão de pausa, menu de pausa e tela de Game Over."""
        w, h = surface.get_size()
        self._ensure_surfaces((w, h))

        # 1. Fundo do cabeçalho
        surface.blit(self.top_bar_surface, (0, 0))
        pygame.draw.line(
            surface,
            (95, 110, 140),
            (0, self.top_bar_height),
            (w, self.top_bar_height),
            2,
        )

        margin_x = max(20, int(w * 0.025))

        # 2. Canto Superior Esquerdo: Ícone + Texto de Peso + Barra em Gradiente
        ratio = game_state.get_weight_ratio()
        accent_color = self.get_weight_bar_color(ratio)

        icon_x = margin_x + 18
        icon_y = 44
        self._draw_weight_icon(surface, icon_x, icon_y, accent_color)

        bar_x = margin_x + 46
        bar_y = 46
        bar_width = min(250, max(175, int(w * 0.19)))
        bar_height = 24

        weight_label = f"Peso: {game_state.weight:.1f} / {MAX_WEIGHT:.0f} kg"
        self._draw_text_with_shadow(
            surface,
            weight_label,
            self.font_main,
            COLOR_TEXT,
            (bar_x, 12),
            align="topleft",
        )

        self._draw_gradient_weight_bar(
            surface, bar_x, bar_y, bar_width, bar_height, ratio
        )

        # 3. Centro do Cabeçalho: Botão de Pausa quando em jogo ativo
        if game_state.state == STATE_PLAYING:
            self.btn_hud_pause.draw(surface, self.font_pause_btn)

        # 4. Canto Superior Direito: Ícone de Maçã + Pontos de Comida Boa
        right_edge = w - margin_x
        apple_icon_cx = right_edge - 18
        apple_icon_cy = 44
        self._draw_apple_icon(surface, apple_icon_cx, apple_icon_cy)

        text_right_x = right_edge - 46
        self._draw_text_with_shadow(
            surface,
            "Pontos de Comida Boa",
            self.font_small,
            COLOR_TEXT,
            (text_right_x, 12),
            align="topright",
        )
        self._draw_text_with_shadow(
            surface,
            f"{game_state.good_food_count}",
            self.font_score_val,
            (46, 204, 113),
            (text_right_x, 36),
            align="topright",
        )

        # 5. Overlays de estado (Pausa ou Game Over)
        if game_state.state == STATE_PAUSED:
            self._draw_pause_menu(surface, game_state)
        elif game_state.state == STATE_GAME_OVER:
            self._draw_game_over(surface, game_state)

    def _draw_pause_menu(self, surface: pygame.Surface, game_state: GameState):
        """Renderiza o overlay de pausa estilizado com botões interativos."""
        w, h = surface.get_size()
        surface.blit(self.overlay_surface, (0, 0))

        cx = w // 2
        cy = h // 2

        card_width = min(430, w - 40)
        card_height = 380
        card_rect = pygame.Rect(0, 0, card_width, card_height)
        card_rect.center = (cx, cy + 16)

        pygame.draw.rect(surface, (26, 30, 44), card_rect, border_radius=20)
        pygame.draw.rect(surface, COLOR_GOLD, card_rect, width=3, border_radius=20)

        self._draw_text_with_shadow(
            surface,
            "JOGO PAUSADO",
            self.font_pause_title,
            COLOR_GOLD,
            (cx, cy - 128),
            align="center",
        )

        summary = f"Pontos: {game_state.good_food_count}  •  Peso: {game_state.weight:.1f} kg"
        self._draw_text_with_shadow(
            surface,
            summary,
            self.font_small,
            (220, 232, 245),
            (cx, cy - 80),
            align="center",
        )

        self.btn_resume.draw(surface, self.font_pause_menu_btn)
        self.btn_restart.draw(surface, self.font_pause_menu_btn)
        self.btn_menu.draw(surface, self.font_pause_menu_btn)

        hint_text = "Atalhos: P / ESPAÇO para Continuar  •  ESC para Sair"
        self._draw_text_with_shadow(
            surface,
            hint_text,
            self.font_hint,
            (195, 208, 225),
            (cx, cy + 178),
            align="center",
        )

    def _draw_game_over(self, surface: pygame.Surface, game_state: GameState):
        """Renderiza o overlay centralizado de Game Over."""
        w, h = surface.get_size()
        surface.blit(self.overlay_surface, (0, 0))

        center_x = w // 2
        center_y = h // 2

        card_width = min(460, w - 40)
        card_height = 260
        card_rect = pygame.Rect(0, 0, card_width, card_height)
        card_rect.center = (center_x, center_y)

        pygame.draw.rect(surface, (28, 30, 42), card_rect, border_radius=18)
        pygame.draw.rect(surface, (231, 76, 60), card_rect, width=3, border_radius=18)

        self._draw_text_with_shadow(
            surface,
            "GAME OVER",
            self.font_game_over,
            (231, 76, 60),
            (center_x, center_y - 70),
            align="center",
        )

        self._draw_text_with_shadow(
            surface,
            f"Pontuação Final: {game_state.good_food_count}",
            self.font_score_val,
            COLOR_TEXT,
            (center_x, center_y + 4),
            align="center",
        )

        self._draw_text_with_shadow(
            surface,
            "Pressione ESPAÇO para reiniciar",
            self.font_restart,
            (241, 196, 15),
            (center_x, center_y + 70),
            align="center",
        )
