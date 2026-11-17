import random
import pygame
from config import LANE_COUNT, BASE_SPAWN_INTERVAL_MS, STATE_PLAYING, ScreenLayout
from entities.item import Item
from game_state import GameState


class Spawner:
    """Gerencia a criação periódica, atualização dos itens e disparo de efeitos na colisão."""

    def __init__(self, layout: ScreenLayout):
        self.layout = layout
        self.items: list[Item] = []
        self.timer_ms = 0.0
        self.spawn_interval_ms = BASE_SPAWN_INTERVAL_MS

    def reset(self):
        """Limpa todos os itens ativos da tela e reinicia o cronômetro."""
        self.items.clear()
        self.timer_ms = 0.0
        self.spawn_interval_ms = BASE_SPAWN_INTERVAL_MS

    def spawn_item(self, speed: float):
        """Instancia um item em uma faixa aleatória (bom ou ruim) com a velocidade atual."""
        lane = random.randint(0, LANE_COUNT - 1)
        lane_x = self.layout.lane_centers[lane]
        is_good = random.choice([True, False])
        self.items.append(
            Item(
                lane=lane,
                lane_x=lane_x,
                is_good=is_good,
                speed=speed,
                lane_width=self.layout.lane_width,
            )
        )

    def update(self, dt: float, game_state: GameState):
        """Atualiza o cronômetro de spawn e movimenta os itens se o jogo estiver ativo."""
        if game_state.state != STATE_PLAYING:
            return

        self.spawn_interval_ms = game_state.current_spawn_interval_ms
        self.timer_ms += dt * 1000.0

        if self.timer_ms >= self.spawn_interval_ms:
            self.timer_ms -= self.spawn_interval_ms
            self.spawn_item(speed=game_state.current_item_speed)

        for item in self.items:
            item.update(dt, current_speed=game_state.current_item_speed)

        self.items = [
            item for item in self.items if not item.is_off_screen(self.layout.screen_height)
        ]

    def check_collisions(
        self, player_rect: pygame.Rect, game_state: GameState, effects=None
    ):
        """Verifica colisão AABB entre o jogador e os itens ativos e dispara efeitos visuais."""
        if game_state.state != STATE_PLAYING:
            return

        remaining_items = []
        for item in self.items:
            if player_rect.colliderect(item.rect):
                if item.is_good:
                    game_state.register_good_food()
                    if effects is not None:
                        effects.spawn_good_effect(item.x, item.y)
                else:
                    game_state.register_bad_food()
                    if effects is not None:
                        effects.trigger_bad_effect(item.x, item.y)
            else:
                remaining_items.append(item)

        self.items = remaining_items

    def draw(self, surface: pygame.Surface):
        """Desenha todos os itens ativos."""
        for item in self.items:
            item.draw(surface)
