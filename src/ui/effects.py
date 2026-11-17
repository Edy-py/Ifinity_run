import math
import random
import pygame


class Particle:
    """Partícula visual com decaimento suave para feedback de colisão."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        radius: float,
        color: tuple[int, int, int],
        max_lifetime: float,
        shape: str = "circle",
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.age = 0.0
        self.max_lifetime = max(0.05, max_lifetime)
        self.shape = shape

    @property
    def alive(self) -> bool:
        return self.age < self.max_lifetime

    def update(self, dt: float):
        """Movimenta a partícula com desaceleração e avança o tempo de vida."""
        damping = 0.94 ** (dt * 60.0)
        self.vx *= damping
        self.vy *= damping
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt

    def draw(self, surface: pygame.Surface):
        """Desenha a partícula reduzindo o raio proporcionalmente ao tempo restante."""
        life_ratio = max(0.0, 1.0 - (self.age / self.max_lifetime))
        current_radius = max(1, int(self.radius * life_ratio))
        cx, cy = int(self.x), int(self.y)

        if self.shape == "diamond":
            points = [
                (cx, cy - current_radius),
                (cx + current_radius, cy),
                (cx, cy + current_radius),
                (cx - current_radius, cy),
            ]
            pygame.draw.polygon(surface, self.color, points)
        else:
            pygame.draw.circle(surface, self.color, (cx, cy), current_radius)
            if current_radius >= 3:
                pygame.draw.circle(
                    surface, (255, 255, 255), (cx, cy), max(1, current_radius // 2)
                )


class FloatingText:
    """Texto flutuante que sobe e desaparece após uma coleta ou impacto."""

    def __init__(
        self,
        x: float,
        y: float,
        text: str,
        color: tuple[int, int, int],
        max_lifetime: float = 0.7,
    ):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.age = 0.0
        self.max_lifetime = max_lifetime
        self.vy = -75.0

    @property
    def alive(self) -> bool:
        return self.age < self.max_lifetime

    def update(self, dt: float):
        self.y += self.vy * dt
        self.age += dt

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        alpha = int(255 * max(0.0, 1.0 - (self.age / self.max_lifetime)))
        if alpha <= 0:
            return

        text_surf = font.render(self.text, True, self.color)
        shadow_surf = font.render(self.text, True, (15, 18, 25))
        text_surf.set_alpha(alpha)
        shadow_surf.set_alpha(alpha)

        rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(shadow_surf, rect.move(2, 2))
        surface.blit(text_surf, rect)


class VisualEffectsManager:
    """Gerencia partículas, textos flutuantes, tremor de tela (Screen Shake) e flash vermelho."""

    GOOD_COLORS = [
        (46, 204, 113),   # Verde-esmeralda
        (125, 255, 100),  # Verde-limão
        (255, 215, 0),    # Amarelo-ouro
        (255, 255, 255),  # Branco brilhante
    ]

    BAD_COLORS = [
        (231, 76, 60),    # Vermelho
        (255, 95, 45),    # Laranja forte
        (180, 25, 25),    # Vermelho escuro
    ]

    def __init__(self):
        pygame.font.init()
        self.font_floating = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.particles: list[Particle] = []
        self.floating_texts: list[FloatingText] = []
        self.shake_timer = 0.0
        self.shake_max_time = 0.28
        self.shake_magnitude = 0.0
        self.flash_alpha = 0.0
        self._flash_size: tuple[int, int] | None = None
        self._flash_surface: pygame.Surface | None = None

    def reset(self):
        """Limpa todos os efeitos ativos."""
        self.particles.clear()
        self.floating_texts.clear()
        self.shake_timer = 0.0
        self.shake_magnitude = 0.0
        self.flash_alpha = 0.0

    def spawn_good_effect(self, x: float, y: float):
        """Gera explosão de partículas verdes/douradas e texto flutuante positivo."""
        for _ in range(22):
            angle = random.uniform(0.0, math.tau)
            speed = random.uniform(90.0, 260.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            radius = random.uniform(4.0, 8.5)
            color = random.choice(self.GOOD_COLORS)
            lifetime = random.uniform(0.32, 0.62)
            shape = random.choice(["circle", "diamond"])
            self.particles.append(
                Particle(x, y, vx, vy, radius, color, lifetime, shape=shape)
            )

        self.floating_texts.append(
            FloatingText(x, y - 16, "+1", (255, 230, 80), max_lifetime=0.7)
        )

    def trigger_bad_effect(self, x: float, y: float):
        """Inicia Screen Shake, flash vermelho, partículas de impacto e texto de peso."""
        self.shake_timer = 0.28
        self.shake_max_time = 0.28
        self.shake_magnitude = 11.0
        self.flash_alpha = 120.0

        for _ in range(14):
            angle = random.uniform(0.0, math.tau)
            speed = random.uniform(80.0, 220.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            radius = random.uniform(4.5, 8.0)
            color = random.choice(self.BAD_COLORS)
            lifetime = random.uniform(0.28, 0.52)
            self.particles.append(
                Particle(x, y, vx, vy, radius, color, lifetime, shape="diamond")
            )

        self.floating_texts.append(
            FloatingText(x, y - 16, "+2.5 kg", (255, 90, 90), max_lifetime=0.7)
        )

    def update(self, dt: float):
        """Atualiza partículas, textos flutuantes, Screen Shake e flash vermelho."""
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        for ftext in self.floating_texts:
            ftext.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.alive]

        if self.shake_timer > 0.0:
            self.shake_timer = max(0.0, self.shake_timer - dt)

        if self.flash_alpha > 0.0:
            self.flash_alpha = max(0.0, self.flash_alpha - 420.0 * dt)

    def get_screen_offset(self) -> tuple[int, int]:
        """Retorna o deslocamento (dx, dy) amortecido do Screen Shake."""
        if self.shake_timer <= 0.0 or self.shake_max_time <= 0.0:
            return (0, 0)
        strength = (self.shake_timer / self.shake_max_time) * self.shake_magnitude
        dx = int(round(random.uniform(-strength, strength)))
        dy = int(round(random.uniform(-strength, strength)))
        return (dx, dy)

    def draw_world_effects(self, surface: pygame.Surface):
        """Desenha partículas e textos flutuantes na camada do mundo."""
        for particle in self.particles:
            particle.draw(surface)
        for ftext in self.floating_texts:
            ftext.draw(surface, self.font_floating)

    def draw_screen_flash(self, surface: pygame.Surface):
        """Desenha o overlay e borda de alerta vermelho pré-renderizados ao colidir com comida ruim."""
        if self.flash_alpha <= 1.0:
            return

        size = surface.get_size()
        if self._flash_size != size or self._flash_surface is None:
            self._flash_size = size
            w, h = size
            self._flash_surface = pygame.Surface(size, pygame.SRCALPHA)
            self._flash_surface.fill((231, 40, 40, 120))
            pygame.draw.rect(
                self._flash_surface,
                (255, 50, 50, 220),
                pygame.Rect(0, 0, w, h),
                width=12,
            )

        self._flash_surface.set_alpha(int(min(255, self.flash_alpha * 2.0)))
        surface.blit(self._flash_surface, (0, 0))
