import math
from pathlib import Path
import pygame
from config import (
    LANE_COUNT,
    PLAYER_LERP_SPEED,
    ScreenLayout,
)


class Player:
    """Representa o jogador correndo nas 3 faixas com sprite PNG escalado, sombra e tilt."""

    def __init__(self, layout: ScreenLayout):
        self.layout = layout
        target_w = max(56, min(92, int(layout.lane_width * 0.52)))
        target_h = int(target_w * 1.25)

        self.width = target_w
        self.height = target_h
        # Hitbox justa centrada no sprite para colisões precisas
        self.rect = pygame.Rect(0, 0, int(target_w * 0.78), int(target_h * 0.78))

        sprite_path = Path(__file__).resolve().parents[2] / "assets" / "images" / "player.png"
        raw_img = pygame.image.load(str(sprite_path))
        if pygame.display.get_surface() is not None:
            raw_img = raw_img.convert_alpha()
        self.sprite = pygame.transform.scale(raw_img, (self.width, self.height))

        self.tilt_angle = 0.0
        self.run_time = 0.0

        # Cache de sombra elíptica e de sprites rotacionados por ângulo quantizado
        shadow_w = int(self.width * 0.88)
        shadow_h = int(self.height * 0.34)
        self.shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(
            self.shadow_surf,
            (10, 12, 18, 125),
            pygame.Rect(0, 0, shadow_w, shadow_h),
        )
        self._rotated_cache: dict[float, pygame.Surface] = {0.0: self.sprite}

        self.reset()

    def reset(self):
        """Reposiciona o jogador na faixa central e zera animações."""
        self.current_lane = 1
        self.x = float(self.layout.lane_centers[self.current_lane])
        self.y = float(self.layout.player_y)
        self.tilt_angle = 0.0
        self.run_time = 0.0
        self.rect.center = (int(self.x), int(self.y))

    def move_left(self):
        """Move uma faixa para a esquerda, se não estiver no limite."""
        if self.current_lane > 0:
            self.current_lane -= 1

    def move_right(self):
        """Move uma faixa para a direita, se não estiver no limite."""
        if self.current_lane < LANE_COUNT - 1:
            self.current_lane += 1

    def handle_keydown(self, key: int):
        """Processa os comandos discretos de troca de faixa (Setas ou A/D)."""
        if key in (pygame.K_LEFT, pygame.K_a):
            self.move_left()
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.move_right()

    def update(self, dt: float):
        """Atualiza a posição horizontal, ciclo de corrida e inclinação (tilt)."""
        self.run_time += dt * 12.0

        target_x = float(self.layout.lane_centers[self.current_lane])
        diff = target_x - self.x

        if abs(diff) < 1.0:
            self.x = target_x
        else:
            self.x += diff * min(1.0, PLAYER_LERP_SPEED * dt)

        # Inclinação na direção do movimento (ângulo negativo no Pygame inclina à direita)
        target_tilt = max(-18.0, min(18.0, -diff * 0.22))
        self.tilt_angle += (target_tilt - self.tilt_angle) * min(1.0, 20.0 * dt)

        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface: pygame.Surface):
        """Desenha a sombra elíptica em cache e o sprite rotacionado com cache de ângulo."""
        bob = int(abs(math.sin(self.run_time)) * 4)

        # 1. Sombra elíptica projetada no asfalto (pré-renderizada)
        shadow_rect = self.shadow_surf.get_rect(
            center=(int(self.x) + 4, int(self.y) + int(self.height * 0.36))
        )
        surface.blit(self.shadow_surf, shadow_rect)

        # 2. Sprite rotacionado quantizado em passos de 0.5 grau com cache
        q_angle = (
            0.0 if abs(self.tilt_angle) < 0.25 else round(self.tilt_angle * 2.0) / 2.0
        )
        rotated_surf = self._rotated_cache.get(q_angle)
        if rotated_surf is None:
            rotated_surf = pygame.transform.rotozoom(self.sprite, q_angle, 1.0)
            self._rotated_cache[q_angle] = rotated_surf

        rotated_rect = rotated_surf.get_rect(center=(int(self.x), int(self.y) - bob))
        surface.blit(rotated_surf, rotated_rect)
