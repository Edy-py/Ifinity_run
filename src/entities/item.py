import math
import random
from pathlib import Path
import pygame
from config import BASE_ITEM_SPEED


class Item:
    """Representa um item alimentar com cache de sprites escalados e sombra no asfalto."""

    _RAW_GOOD_IMG: pygame.Surface | None = None
    _RAW_BAD_IMG: pygame.Surface | None = None
    _SHADOW_CACHE: dict[int, pygame.Surface] = {}
    _SCALED_CACHE: dict[tuple[bool, int], pygame.Surface] = {}

    @classmethod
    def _get_raw_sprite(cls, is_good: bool) -> pygame.Surface:
        """Carrega e armazena em cache os sprites de comida boa e comida ruim."""
        images_dir = Path(__file__).resolve().parents[2] / "assets" / "images"
        has_display = pygame.display.get_surface() is not None

        if is_good:
            if cls._RAW_GOOD_IMG is None:
                img = pygame.image.load(str(images_dir / "good_food.png"))
                cls._RAW_GOOD_IMG = img.convert_alpha() if has_display else img
            return cls._RAW_GOOD_IMG
        else:
            if cls._RAW_BAD_IMG is None:
                img = pygame.image.load(str(images_dir / "bad_food.png"))
                cls._RAW_BAD_IMG = img.convert_alpha() if has_display else img
            return cls._RAW_BAD_IMG

    @classmethod
    def _get_shadow(cls, size: int) -> pygame.Surface:
        """Retorna a superfície de sombra elíptica em cache para o tamanho do item."""
        shadow = cls._SHADOW_CACHE.get(size)
        if shadow is None:
            shadow_w = int(size * 0.82)
            shadow_h = int(size * 0.34)
            shadow = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
            pygame.draw.ellipse(
                shadow,
                (10, 12, 18, 120),
                pygame.Rect(0, 0, shadow_w, shadow_h),
            )
            cls._SHADOW_CACHE[size] = shadow
        return shadow

    @classmethod
    def _get_scaled_sprite(cls, is_good: bool, scaled_size: int) -> pygame.Surface:
        """Retorna o sprite escalado do cache para evitar redimensionamentos por frame."""
        key = (is_good, scaled_size)
        sprite = cls._SCALED_CACHE.get(key)
        if sprite is None:
            raw_img = cls._get_raw_sprite(is_good)
            sprite = pygame.transform.scale(raw_img, (scaled_size, scaled_size))
            cls._SCALED_CACHE[key] = sprite
        return sprite

    def __init__(
        self,
        lane: int,
        lane_x: int,
        is_good: bool,
        speed: float = BASE_ITEM_SPEED,
        lane_width: int = 160,
    ):
        self.lane = lane
        self.is_good = is_good
        self.size = max(52, min(84, int(lane_width * 0.46)))

        self.x = float(lane_x)
        self.y = float(-self.size // 2)
        self.speed = speed
        self.age = random.uniform(0.0, 6.28)

        self.sprite = self._get_scaled_sprite(self.is_good, self.size)

        hitbox_size = int(self.size * 0.82)
        self.rect = pygame.Rect(0, 0, hitbox_size, hitbox_size)
        self.rect.center = (int(self.x), int(self.y))

    def update(self, dt: float, current_speed: float | None = None):
        """Move o item verticalmente e atualiza o timer de pulsação."""
        if current_speed is not None:
            self.speed = current_speed
        self.y += self.speed * dt
        self.age += dt
        self.rect.center = (int(self.x), int(self.y))

    def is_off_screen(self, screen_height: int) -> bool:
        """Verifica se o item já passou completamente do fundo da tela."""
        return self.rect.top > screen_height

    def draw(self, surface: pygame.Surface):
        """Desenha a sombra em cache e o sprite pulsante obtido do cache."""
        shadow_surf = self._get_shadow(self.size)
        shadow_rect = shadow_surf.get_rect(
            center=(int(self.x) + 4, int(self.y) + int(self.size * 0.36))
        )
        surface.blit(shadow_surf, shadow_rect)

        freq = 6.5 if self.is_good else 10.0
        scale_factor = 1.0 + 0.08 * math.sin(self.age * freq)
        scaled_w = max(1, int(self.size * scale_factor))
        pulsed_surf = self._get_scaled_sprite(self.is_good, scaled_w)
        pulsed_rect = pulsed_surf.get_rect(center=self.rect.center)
        surface.blit(pulsed_surf, pulsed_rect)
