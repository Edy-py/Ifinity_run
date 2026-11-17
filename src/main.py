import sys
import pygame
from config import (
    FULLSCREEN,
    FALLBACK_WIDTH,
    FALLBACK_HEIGHT,
    FPS,
    WINDOW_TITLE,
    STATE_MENU,
    STATE_PLAYING,
    STATE_PAUSED,
    STATE_GAME_OVER,
    COLOR_BG_CITY,
    COLOR_BG_GRASS,
    COLOR_SIDEWALK,
    COLOR_ASPHALT,
    COLOR_LANE_LINE,
    LANE_COUNT,
    ScreenLayout,
    compute_layout,
)
from game_state import GameState
from entities.player import Player
from entities.spawner import Spawner
from ui.hud import HUD
from ui.menu import Menu
from ui.effects import VisualEffectsManager


# Paleta vibrante urbana para os prédios em Parallax (cor principal, borda do telhado, detalhe)
BUILDING_STYLES = [
    ((46, 134, 193), (84, 169, 224), (241, 196, 15)),   # Azul urbano + destaque amarelo
    ((142, 68, 173), (175, 108, 204), (118, 215, 196)), # Roxo vibrante + ciano
    ((203, 67, 53), (231, 106, 92), (249, 231, 159)),   # Terracota + creme
    ((40, 116, 166), (72, 149, 199), (245, 176, 65)),   # Azul-petróleo + âmbar
    ((52, 73, 94), (86, 108, 130), (46, 204, 113)),     # Cinza-azulado + verde
]

# Caches globais de superfícies estáticas e props para alta performance
_STATIC_TRACK_CACHE: dict[tuple[int, int, int, int, int], tuple[pygame.Surface, pygame.Surface, int]] = {}
_LAMP_HALO_SURF: pygame.Surface | None = None
_TREE_SURF_CACHE: dict[int, pygame.Surface] = {}


def create_display() -> pygame.Surface:
    """Inicializa a janela em Tela Cheia na resolução nativa do monitor."""
    if FULLSCREEN:
        try:
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        except pygame.error:
            pass
    return pygame.display.set_mode((FALLBACK_WIDTH, FALLBACK_HEIGHT), pygame.RESIZABLE)


def _get_static_track_surfaces(
    layout: ScreenLayout, sidewalk_width: int, grass_pad: int
) -> tuple[pygame.Surface, pygame.Surface, int]:
    """Pré-renderiza o fundo urbano e a faixa central estática (grama, calçadas, asfalto)."""
    w = layout.screen_width
    h = layout.screen_height
    key = (w, h, layout.road_left, layout.road_right, layout.lane_width)
    cached = _STATIC_TRACK_CACHE.get(key)
    if cached is not None:
        return cached

    grass_left = max(0, layout.road_left - sidewalk_width - grass_pad)
    grass_right = min(w, layout.road_right + sidewalk_width + grass_pad)
    strip_w = max(1, grass_right - grass_left)

    city_bg = pygame.Surface((w, h))
    city_bg.fill(COLOR_BG_CITY)

    road_strip = pygame.Surface((strip_w, h))
    road_strip.fill(COLOR_BG_GRASS)

    left_sw_local = (layout.road_left - sidewalk_width) - grass_left
    right_sw_local = layout.road_right - grass_left
    pygame.draw.rect(road_strip, COLOR_SIDEWALK, (left_sw_local, 0, sidewalk_width, h))
    pygame.draw.rect(road_strip, COLOR_SIDEWALK, (right_sw_local, 0, sidewalk_width, h))

    road_local_x = layout.road_left - grass_left
    pygame.draw.rect(road_strip, COLOR_ASPHALT, (road_local_x, 0, layout.road_width, h))
    pygame.draw.rect(
        road_strip,
        (49, 54, 66),
        (road_local_x + layout.lane_width, 0, layout.lane_width, h),
    )

    result = (city_bg, road_strip, grass_left)
    _STATIC_TRACK_CACHE[key] = result
    return result


def _get_lamp_halo_surface() -> pygame.Surface:
    """Retorna o halo luminoso amarelo pré-renderizado dos postes."""
    global _LAMP_HALO_SURF
    if _LAMP_HALO_SURF is None:
        halo = pygame.Surface((76, 76), pygame.SRCALPHA)
        pygame.draw.circle(halo, (255, 230, 120, 48), (38, 38), 36)
        pygame.draw.circle(halo, (255, 240, 160, 85), (38, 38), 18)
        _LAMP_HALO_SURF = halo
    return _LAMP_HALO_SURF


def _get_tree_surface(tree_radius: int) -> pygame.Surface:
    """Pré-renderiza árvore estilizada com sombra e 3 camadas de copa por raio."""
    cached = _TREE_SURF_CACHE.get(tree_radius)
    if cached is not None:
        return cached

    pad = 8
    size = (tree_radius + pad) * 2
    tree_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    center = tree_radius + pad

    pygame.draw.circle(
        tree_surf,
        (16, 65, 34, 125),
        (center + 2, center + 4),
        tree_radius,
    )
    pygame.draw.circle(tree_surf, (30, 132, 73), (center, center), tree_radius)
    pygame.draw.circle(
        tree_surf,
        (46, 204, 113),
        (center - 3, center - 3),
        max(8, tree_radius - 6),
    )
    pygame.draw.circle(
        tree_surf,
        (125, 235, 150),
        (center - 6, center - 6),
        max(4, tree_radius // 3),
    )

    _TREE_SURF_CACHE[tree_radius] = tree_surf
    return tree_surf


def _draw_parallax_buildings(
    surface: pygame.Surface,
    x_start: int,
    x_end: int,
    screen_height: int,
    scroll_y: float,
    is_left_side: bool,
):
    """Desenha prédios Top-Down 2.5D nas faixas externas rolando a 0.55x (Parallax)."""
    area_width = x_end - x_start
    if area_width < 40:
        return

    parallax_y = scroll_y * 0.55
    block_step = 260

    pad_x = 18
    building_w = min(220, max(48, area_width - pad_x * 2))

    offset = parallax_y % block_step
    base_tile = int(parallax_y // block_step)

    for slot in range(-1, (screen_height // block_step) + 2):
        tile_id = base_tile - slot
        y_top = int(slot * block_step + offset)
        style = BUILDING_STYLES[abs(tile_id) % len(BUILDING_STYLES)]
        main_col, roof_col, accent_col = style

        b_height = 190 + (abs(tile_id * 37) % 45)
        w_var = building_w - (abs(tile_id * 19) % max(1, min(36, building_w // 4)))

        if is_left_side:
            bx = x_end - pad_x - w_var
        else:
            bx = x_start + pad_x

        building_rect = pygame.Rect(bx, y_top + 14, w_var, b_height)

        shadow_rect = building_rect.move(10 if is_left_side else -10, 14)
        pygame.draw.rect(surface, (16, 22, 34), shadow_rect, border_radius=14)
        pygame.draw.rect(surface, main_col, building_rect, border_radius=12)

        roof_rect = building_rect.inflate(-14, -14)
        pygame.draw.rect(surface, roof_col, roof_rect, border_radius=10)
        pygame.draw.rect(surface, (235, 242, 250), roof_rect, width=2, border_radius=10)

        if roof_rect.width > 56 and roof_rect.height > 80:
            skylight = pygame.Rect(
                0, 0, max(20, roof_rect.width // 3), max(24, roof_rect.height // 4)
            )
            skylight.center = (roof_rect.centerx, roof_rect.centery - 22)
            pygame.draw.rect(surface, accent_col, skylight, border_radius=6)
            pygame.draw.rect(surface, (255, 255, 255), skylight, width=2, border_radius=6)

            ac_box = pygame.Rect(roof_rect.x + 12, roof_rect.bottom - 38, 22, 22)
            pygame.draw.rect(surface, (44, 62, 80), ac_box, border_radius=4)
            pygame.draw.circle(surface, (189, 195, 199), ac_box.center, 6)

        win_x = building_rect.right - 9 if is_left_side else building_rect.left + 4
        for wy in range(building_rect.top + 22, building_rect.bottom - 24, 28):
            pygame.draw.rect(surface, accent_col, (win_x, wy, 5, 14), border_radius=2)


def _draw_roadside_props(
    surface: pygame.Surface,
    layout: ScreenLayout,
    sidewalk_width: int,
    scroll_y: float,
):
    """Desenha árvores e postes de luz em cache na camada rápida (1.0x)."""
    h = layout.screen_height
    step = 220
    offset = scroll_y % step
    base_tile = int(scroll_y // step)

    left_grass_x = layout.road_left - sidewalk_width - 36
    right_grass_x = layout.road_right + sidewalk_width + 36
    left_pole_x = layout.road_left - sidewalk_width // 2
    right_pole_x = layout.road_right + sidewalk_width // 2

    halo_surf = _get_lamp_halo_surface()

    for slot in range(-1, (h // step) + 2):
        tile_id = base_tile - slot
        py = int(slot * step + offset)

        # Postes de iluminação urbana nas calçadas com halo amarelo pré-renderizado
        for px, is_left in ((left_pole_x, True), (right_pole_x, False)):
            arm_dir = 1 if is_left else -1
            lamp_x = px + arm_dir * 16
            lamp_y = py + 24

            surface.blit(halo_surf, (lamp_x - 38, lamp_y - 38))
            pygame.draw.line(surface, (90, 100, 115), (px, py + 24), (lamp_x, lamp_y), 4)
            pygame.draw.circle(surface, (60, 68, 80), (px, py + 24), 6)
            pygame.draw.circle(surface, (255, 240, 150), (lamp_x, lamp_y), 6)

        # Árvores pré-renderizadas no gramado lateral
        tree_radius = 22 + (abs(tile_id * 13) % 8)
        tree_surf = _get_tree_surface(tree_radius)
        ty = py + 120
        for tx in (left_grass_x, right_grass_x):
            if tx < 16 or tx > layout.screen_width - 16:
                continue
            surface.blit(tree_surf, tree_surf.get_rect(center=(tx, ty)))


def draw_track(surface: pygame.Surface, layout: ScreenLayout, scroll_y: float):
    """Desenha a pista com camadas estáticas em cache, detalhes móveis e Parallax urbano."""
    w = layout.screen_width
    h = layout.screen_height
    sidewalk_width = 28
    grass_pad = 78

    city_bg, road_strip, grass_left = _get_static_track_surfaces(
        layout, sidewalk_width, grass_pad
    )
    grass_right = min(w, layout.road_right + sidewalk_width + grass_pad)

    # 1. Fundo urbano estático em cache + Prédios Parallax (0.55x)
    surface.blit(city_bg, (0, 0))
    _draw_parallax_buildings(surface, 0, grass_left, h, scroll_y, is_left_side=True)
    _draw_parallax_buildings(surface, grass_right, w, h, scroll_y, is_left_side=False)

    # 2. Faixa central estática em cache (gramado + calçadas + asfalto + faixa central)
    surface.blit(road_strip, (grass_left, 0))

    # 3. Ladrilhos das calçadas rolando em 1.0x
    left_sw_x = layout.road_left - sidewalk_width
    right_sw_x = layout.road_right
    tile_step = 55
    tile_offset = int(scroll_y) % tile_step
    for y in range(-tile_step + tile_offset, h, tile_step):
        pygame.draw.line(
            surface, (120, 135, 140), (left_sw_x, y), (left_sw_x + sidewalk_width, y), 2
        )
        pygame.draw.line(
            surface, (120, 135, 140), (right_sw_x, y), (right_sw_x + sidewalk_width, y), 2
        )

    # 4. Juntas horizontais sutis no asfalto
    joint_step = 140
    joint_offset = int(scroll_y) % joint_step
    for y in range(-joint_step + joint_offset, h, joint_step):
        pygame.draw.line(
            surface, (36, 40, 48), (layout.road_left + 8, y), (layout.road_right - 8, y), 2
        )

    # 5. Meio-fio listrado (amarelo e cinza-escuro intercalados)
    curb_len = 44
    curb_offset = scroll_y % curb_len
    base_curb = int(scroll_y // curb_len)

    for slot in range(-1, (h // curb_len) + 2):
        tile_id = base_curb - slot
        y = int(slot * curb_len + curb_offset)
        col = (241, 196, 15) if (tile_id % 2 == 0) else (52, 58, 70)
        pygame.draw.rect(surface, col, (layout.road_left - 6, y, 8, curb_len))
        pygame.draw.rect(surface, col, (layout.road_right - 2, y, 8, curb_len))

    # 6. Linhas divisórias tracejadas entre as 3 faixas
    dash_height = 48
    gap_height = 36
    step = dash_height + gap_height
    offset = int(scroll_y) % step

    for lane_idx in range(1, LANE_COUNT):
        line_x = layout.road_left + (lane_idx * layout.lane_width)
        for y in range(-step + offset, h, step):
            pygame.draw.line(
                surface,
                COLOR_LANE_LINE,
                (line_x, y),
                (line_x, y + dash_height),
                4,
            )

    # 7. Árvores e postes em cache na camada rápida (1.0x)
    _draw_roadside_props(surface, layout, sidewalk_width, scroll_y)


def main():
    pygame.init()
    screen = create_display()
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    screen_size = screen.get_size()
    world_surface = pygame.Surface(screen_size)

    layout = compute_layout(*screen_size)
    game_state = GameState()
    player = Player(layout)
    spawner = Spawner(layout)
    hud = HUD()
    menu = Menu()
    effects = VisualEffectsManager()

    while game_state.running:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        # 1. Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state.running = False
            elif game_state.state == STATE_MENU:
                action = menu.handle_event(event)
                if action == "PLAY":
                    game_state.start_game()
                    player.reset()
                    spawner.reset()
                    effects.reset()
                elif action == "EXIT":
                    game_state.running = False
            elif game_state.state == STATE_GAME_OVER:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_state.reset()
                    player.reset()
                    spawner.reset()
                    effects.reset()
                    print("Partida reiniciada!", flush=True)
            elif game_state.state in (STATE_PLAYING, STATE_PAUSED):
                hud_action = hud.handle_event(event, game_state)
                if hud_action == "PAUSE":
                    game_state.pause_game()
                elif hud_action == "RESUME":
                    game_state.resume_game()
                elif hud_action == "RESTART":
                    game_state.reset()
                    player.reset()
                    spawner.reset()
                    effects.reset()
                    print("Partida reiniciada!", flush=True)
                elif hud_action == "MENU":
                    game_state.return_to_menu()
                    player.reset()
                    spawner.reset()
                    effects.reset()
                elif game_state.state == STATE_PLAYING and event.type == pygame.KEYDOWN:
                    player.handle_keydown(event.key)

        # 2. Atualização de estado (congelado quando em STATE_PAUSED)
        if game_state.state != STATE_PAUSED:
            game_state.update(dt)
            effects.update(dt)

        if game_state.state == STATE_MENU:
            menu.update(screen.get_size(), mouse_pos)
        else:
            hud.update(screen.get_size(), mouse_pos, game_state)
            if game_state.state == STATE_PLAYING:
                player.update(dt)
                spawner.update(dt, game_state)
                spawner.check_collisions(player.rect, game_state, effects=effects)

        # 3. Renderização no mundo + Screen Shake
        draw_track(world_surface, layout, game_state.road_scroll_y)

        if game_state.state != STATE_MENU:
            spawner.draw(world_surface)
            player.draw(world_surface)
            effects.draw_world_effects(world_surface)

        offset_x, offset_y = (
            (0, 0) if game_state.state == STATE_PAUSED else effects.get_screen_offset()
        )
        if offset_x != 0 or offset_y != 0:
            screen.fill((16, 22, 34))
        screen.blit(world_surface, (offset_x, offset_y))

        # 4. Camada fixa de interface e flash de dano
        if game_state.state == STATE_MENU:
            menu.draw(screen, game_state.menu_time)
        else:
            effects.draw_screen_flash(screen)
            hud.draw(screen, game_state)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
