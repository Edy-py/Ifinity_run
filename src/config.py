from dataclasses import dataclass

# Configurações globais do jogo "Corrida da Boa Alimentação"

# Display
FULLSCREEN = True
FALLBACK_WIDTH = 1280
FALLBACK_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "Corrida da Boa Alimentação"

# Estados do Jogo
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_PAUSED = "PAUSED"
STATE_GAME_OVER = "GAME_OVER"

# Cores (R, G, B) - Paleta vibrante urbana (estilo Subway Surfers)
COLOR_BG_GRASS = (39, 174, 96)        # Verde vibrante lateral
COLOR_BG_CITY = (30, 39, 56)          # Azul urbano profundo nas extremidades
COLOR_SIDEWALK = (149, 165, 166)      # Calçada nas bordas da pista
COLOR_ASPHALT = (44, 48, 58)          # Asfalto escuro estilizado
COLOR_ROAD_BORDER = (241, 196, 15)    # Meio-fio amarelo vibrante
COLOR_LANE_LINE = (236, 240, 241)     # Linhas divisórias brancas

COLOR_PLAYER = (41, 128, 185)         # Azul vibrante para o jogador
COLOR_PLAYER_OUTLINE = (255, 255, 255)

COLOR_ITEM_GOOD = (46, 204, 113)      # Verde para alimentos saudáveis
COLOR_ITEM_BAD = (231, 76, 60)        # Vermelho para alimentos prejudiciais
COLOR_TEXT = (255, 255, 255)
COLOR_TEXT_SHADOW = (15, 18, 25)
COLOR_GOLD = (255, 215, 0)
COLOR_DANGER = (231, 76, 60)

# Configuração base das faixas
LANE_COUNT = 3
MAX_ROAD_WIDTH = 540
MIN_ROAD_WIDTH = 390

# Configurações do Jogador
PLAYER_WIDTH = 66
PLAYER_HEIGHT = 86
PLAYER_LERP_SPEED = 18.0  # Velocidade da transição suave e responsiva entre faixas

# Sistema de Peso / Saúde
INITIAL_WEIGHT = 75.0     # Peso ideal inicial (kg)
MIN_WEIGHT = 70.0         # Piso mínimo saudável
MAX_WEIGHT = 95.0         # Limite máximo de peso -> Game Over
WEIGHT_GAIN_BAD = 2.5     # +2.5 kg ao pegar comida ruim
WEIGHT_LOSS_GOOD = 0.5    # -0.5 kg ao pegar comida boa

# Configurações Base dos Itens, Spawner e Dificuldade Progressiva
ITEM_SIZE = 54
BASE_ITEM_SPEED = 340.0         # Velocidade inicial (px/s)
MAX_ITEM_SPEED = 780.0          # Velocidade máxima (px/s)
SPEED_INCREMENT_PER_LEVEL = 28.0

BASE_SPAWN_INTERVAL_MS = 880.0  # Intervalo inicial de spawn (ms)
MIN_SPAWN_INTERVAL_MS = 300.0   # Intervalo mínimo de spawn (ms)
SPAWN_DECREMENT_PER_LEVEL = 45.0

POINTS_PER_DIFFICULTY_LEVEL = 5
SECONDS_PER_DIFFICULTY_LEVEL = 10.0

MENU_SCROLL_SPEED = 240.0       # Velocidade cinematográfica da pista no menu


@dataclass
class ScreenLayout:
    """Calcula e armazena dimensões adaptativas da pista e elementos para qualquer resolução."""

    screen_width: int
    screen_height: int
    road_width: int
    road_left: int
    road_right: int
    lane_width: int
    lane_centers: list[int]
    player_y: int


def compute_layout(screen_width: int, screen_height: int) -> ScreenLayout:
    """Centraliza a pista e posiciona faixas e jogador proporcionalmente à tela."""
    road_width = max(MIN_ROAD_WIDTH, min(MAX_ROAD_WIDTH, int(screen_width * 0.45)))
    # Garante divisibilidade exata pelas 3 faixas
    lane_width = road_width // LANE_COUNT
    road_width = lane_width * LANE_COUNT

    road_left = (screen_width - road_width) // 2
    road_right = road_left + road_width

    lane_centers = [
        road_left + (lane_width * i) + (lane_width // 2)
        for i in range(LANE_COUNT)
    ]

    player_y = screen_height - max(120, int(screen_height * 0.16))

    return ScreenLayout(
        screen_width=screen_width,
        screen_height=screen_height,
        road_width=road_width,
        road_left=road_left,
        road_right=road_right,
        lane_width=lane_width,
        lane_centers=lane_centers,
        player_y=player_y,
    )
