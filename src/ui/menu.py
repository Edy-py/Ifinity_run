import math
import pygame
from config import COLOR_TEXT, COLOR_TEXT_SHADOW, COLOR_GOLD


class MenuButton:
    """Botão interativo estilizado com estado hover e clique."""

    def __init__(
        self,
        text: str,
        base_color: tuple[int, int, int],
        hover_color: tuple[int, int, int],
        border_color: tuple[int, int, int],
        width: int = 280,
        height: int = 64,
    ):
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.width = width
        self.height = height
        self.rect = pygame.Rect(0, 0, width, height)
        self.is_hovered = False

    def update(self, center: tuple[int, int], mouse_pos: tuple[int, int]):
        """Atualiza posição centralizada e estado de hover do botão."""
        self.rect.center = center
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """Retorna True se o botão esquerdo do mouse clicou sobre este botão."""
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Desenha o botão com sombra 3D, bordas arredondadas e feedback de hover."""
        draw_rect = self.rect.copy()
        if self.is_hovered:
            draw_rect.inflate_ip(12, 6)

        # Sombra sólida abaixo do botão (efeito arcade 3D)
        shadow_rect = draw_rect.move(0, 6)
        pygame.draw.rect(surface, (15, 18, 25), shadow_rect, border_radius=16)

        # Corpo principal
        fill_color = self.hover_color if self.is_hovered else self.base_color
        pygame.draw.rect(surface, fill_color, draw_rect, border_radius=16)

        # Brilho superior interno
        highlight_rect = pygame.Rect(
            draw_rect.x + 6, draw_rect.y + 4, draw_rect.width - 12, draw_rect.height // 3
        )
        highlight_surf = pygame.Surface(highlight_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            highlight_surf, (255, 255, 255, 45), highlight_surf.get_rect(), border_radius=10
        )
        surface.blit(highlight_surf, highlight_rect.topleft)

        # Borda externa
        border_col = (255, 255, 255) if self.is_hovered else self.border_color
        pygame.draw.rect(surface, border_col, draw_rect, width=3, border_radius=16)

        # Texto centralizado com sombra
        text_surf = font.render(self.text, True, COLOR_TEXT)
        shadow_text = font.render(self.text, True, COLOR_TEXT_SHADOW)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(shadow_text, text_rect.move(2, 2))
        surface.blit(text_surf, text_rect)


class Menu:
    """Tela de Menu Inicial sobre a pista em movimento cinematográfico."""

    def __init__(self):
        pygame.font.init()
        self.font_title_top = pygame.font.SysFont("Segoe UI", 56, bold=True)
        self.font_title_bottom = pygame.font.SysFont("Segoe UI", 46, bold=True)
        self.font_subtitle = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.font_button = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.font_hint = pygame.font.SysFont("Segoe UI", 16, bold=False)

        self.btn_play = MenuButton(
            text="JOGAR",
            base_color=(46, 204, 113),
            hover_color=(62, 224, 130),
            border_color=(255, 255, 255),
            width=300,
            height=68,
        )
        self.btn_exit = MenuButton(
            text="SAIR",
            base_color=(231, 76, 60),
            hover_color=(245, 96, 80),
            border_color=(255, 220, 220),
            width=260,
            height=58,
        )

        self._overlay_size: tuple[int, int] | None = None
        self._overlay_surface: pygame.Surface | None = None

    def _ensure_overlay(self, size: tuple[int, int]):
        if self._overlay_size != size:
            self._overlay_size = size
            self._overlay_surface = pygame.Surface(size, pygame.SRCALPHA)
            self._overlay_surface.fill((12, 16, 26, 145))

    def _draw_outlined_title(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        outline_color: tuple[int, int, int],
        center: tuple[int, int],
    ):
        """Desenha texto grande com contorno grosso e sombra projetada."""
        base_surf = font.render(text, True, color)
        outline_surf = font.render(text, True, outline_color)
        shadow_surf = font.render(text, True, (10, 12, 18))

        rect = base_surf.get_rect(center=center)

        # Sombra profunda
        surface.blit(shadow_surf, rect.move(5, 6))

        # Contorno em 8 direções
        for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, -2), (-2, 2), (2, 2)]:
            surface.blit(outline_surf, rect.move(dx, dy))

        surface.blit(base_surf, rect)

    def update(self, screen_size: tuple[int, int], mouse_pos: tuple[int, int]):
        """Atualiza o layout dos botões de acordo com a resolução da tela."""
        w, h = screen_size
        cx = w // 2
        cy = h // 2

        self.btn_play.update((cx, cy + 40), mouse_pos)
        self.btn_exit.update((cx, cy + 128), mouse_pos)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Retorna 'PLAY', 'EXIT' ou None conforme interação no menu."""
        if self.btn_play.is_clicked(event):
            return "PLAY"
        if self.btn_exit.is_clicked(event):
            return "EXIT"
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "PLAY"
        return None

    def draw(self, surface: pygame.Surface, menu_time: float):
        """Renderiza o overlay, título estilizado animado e botões do menu."""
        w, h = surface.get_size()
        self._ensure_overlay((w, h))
        surface.blit(self._overlay_surface, (0, 0))

        cx = w // 2
        cy = h // 2
        bob = int(math.sin(menu_time * 3.0) * 6)

        # Painel decorativo atrás do título
        banner_rect = pygame.Rect(0, 0, min(640, w - 40), 175)
        banner_rect.center = (cx, cy - 125 + bob)
        banner_surf = pygame.Surface(banner_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            banner_surf, (20, 28, 45, 200), banner_surf.get_rect(), border_radius=24
        )
        pygame.draw.rect(
            banner_surf, (*COLOR_GOLD, 220), banner_surf.get_rect(), width=3, border_radius=24
        )
        surface.blit(banner_surf, banner_rect.topleft)

        # Título estilizado em 2 linhas
        self._draw_outlined_title(
            surface,
            "CORRIDA DA",
            self.font_title_top,
            COLOR_GOLD,
            (25, 30, 48),
            (cx, cy - 160 + bob),
        )
        self._draw_outlined_title(
            surface,
            "BOA ALIMENTAÇÃO",
            self.font_title_bottom,
            (46, 204, 113),
            (18, 24, 38),
            (cx, cy - 105 + bob),
        )

        # Subtítulo
        sub_surf = self.font_subtitle.render(
            "Desvie das tentações e conquiste saúde na pista!", True, (235, 242, 250)
        )
        sub_shadow = self.font_subtitle.render(
            "Desvie das tentações e conquiste saúde na pista!", True, (12, 15, 22)
        )
        sub_rect = sub_surf.get_rect(center=(cx, cy - 40))
        surface.blit(sub_shadow, sub_rect.move(2, 2))
        surface.blit(sub_surf, sub_rect)

        # Botões
        self.btn_play.draw(surface, self.font_button)
        self.btn_exit.draw(surface, self.font_button)

        # Dica de controles no rodapé
        hint_text = "Controles: Setas (← →) ou A / D  •  ENTER para Jogar  •  ESC para Sair"
        hint_surf = self.font_hint.render(hint_text, True, (200, 210, 225))
        hint_rect = hint_surf.get_rect(center=(cx, h - 36))
        surface.blit(hint_surf, hint_rect)
