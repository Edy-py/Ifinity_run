from config import (
    STATE_MENU,
    STATE_PLAYING,
    STATE_PAUSED,
    STATE_GAME_OVER,
    INITIAL_WEIGHT,
    MIN_WEIGHT,
    MAX_WEIGHT,
    WEIGHT_GAIN_BAD,
    WEIGHT_LOSS_GOOD,
    BASE_ITEM_SPEED,
    MAX_ITEM_SPEED,
    SPEED_INCREMENT_PER_LEVEL,
    BASE_SPAWN_INTERVAL_MS,
    MIN_SPAWN_INTERVAL_MS,
    SPAWN_DECREMENT_PER_LEVEL,
    POINTS_PER_DIFFICULTY_LEVEL,
    SECONDS_PER_DIFFICULTY_LEVEL,
    MENU_SCROLL_SPEED,
)


class GameState:
    """Armazena e gerencia os estados do jogo (MENU, PLAYING, PAUSED, GAME_OVER), peso e pontuação."""

    def __init__(self):
        self.running = True
        self.state = STATE_MENU
        self.road_scroll_y = 0.0
        self.menu_time = 0.0
        self.reset_run_data()

    @property
    def game_over(self) -> bool:
        return self.state == STATE_GAME_OVER

    @property
    def paused(self) -> bool:
        return self.state == STATE_PAUSED

    def reset_run_data(self):
        """Reinicia os dados de partida sem alterar obrigatoriamente o estado atual."""
        self.good_food_count = 0
        self.bad_food_count = 0
        self.weight = INITIAL_WEIGHT
        self.elapsed_time = 0.0
        self.difficulty_level = 0
        self.current_item_speed = BASE_ITEM_SPEED
        self.current_spawn_interval_ms = BASE_SPAWN_INTERVAL_MS

    def start_game(self):
        """Inicia uma nova partida a partir do menu ou reinicia após Game Over."""
        self.reset_run_data()
        self.state = STATE_PLAYING

    def pause_game(self):
        """Pausa a partida ativa."""
        if self.state == STATE_PLAYING:
            self.state = STATE_PAUSED
            print("Jogo pausado", flush=True)

    def resume_game(self):
        """Retoma a partida pausada."""
        if self.state == STATE_PAUSED:
            self.state = STATE_PLAYING
            print("Jogo retomado", flush=True)

    def toggle_pause(self):
        """Alterna entre PLAYING e PAUSED."""
        if self.state == STATE_PLAYING:
            self.pause_game()
        elif self.state == STATE_PAUSED:
            self.resume_game()

    def return_to_menu(self):
        """Reseta dados da partida e retorna ao Menu Inicial."""
        self.reset_run_data()
        self.state = STATE_MENU

    def reset(self):
        """Reinicia a partida diretamente para PLAYING."""
        self.start_game()

    def update(self, dt: float):
        """Atualiza o estado ativo (rolagem cinematográfica no menu ou partida ativa)."""
        if self.state == STATE_MENU:
            self.menu_time += dt
            self.road_scroll_y += MENU_SCROLL_SPEED * dt
            return

        if self.state != STATE_PLAYING:
            return

        self.elapsed_time += dt
        self.update_difficulty()
        self.road_scroll_y += self.current_item_speed * dt

    def update_difficulty(self):
        """Calcula o nível de dificuldade com base nos pontos e no tempo decorrido."""
        level_by_points = self.good_food_count // POINTS_PER_DIFFICULTY_LEVEL
        level_by_time = int(self.elapsed_time // SECONDS_PER_DIFFICULTY_LEVEL)
        self.difficulty_level = level_by_points + level_by_time

        self.current_item_speed = min(
            MAX_ITEM_SPEED,
            BASE_ITEM_SPEED + (self.difficulty_level * SPEED_INCREMENT_PER_LEVEL),
        )
        self.current_spawn_interval_ms = max(
            MIN_SPAWN_INTERVAL_MS,
            BASE_SPAWN_INTERVAL_MS - (self.difficulty_level * SPAWN_DECREMENT_PER_LEVEL),
        )

    def register_good_food(self):
        """Soma 1 ponto de comida boa e reduz levemente o peso."""
        if self.state != STATE_PLAYING:
            return

        self.good_food_count += 1
        self.weight = max(MIN_WEIGHT, round(self.weight - WEIGHT_LOSS_GOOD, 1))
        self.update_difficulty()
        print(
            f"Pegou comida boa | Pontos: {self.good_food_count} | Peso: {self.weight:.1f} kg",
            flush=True,
        )

    def register_bad_food(self):
        """Aumenta o peso e verifica se atingiu o limite de Game Over."""
        if self.state != STATE_PLAYING:
            return

        self.bad_food_count += 1
        self.weight = min(MAX_WEIGHT, round(self.weight + WEIGHT_GAIN_BAD, 1))
        print(
            f"Pegou comida ruim | Peso: {self.weight:.1f} kg / {MAX_WEIGHT:.1f} kg",
            flush=True,
        )

        if self.weight >= MAX_WEIGHT:
            self.weight = MAX_WEIGHT
            self.state = STATE_GAME_OVER
            print(
                f"GAME OVER! Pontuação Final: {self.good_food_count}",
                flush=True,
            )

    def get_weight_ratio(self) -> float:
        """Retorna a proporção de excesso de peso entre 0.0 (<= 75kg) e 1.0 (95kg)."""
        if self.weight <= INITIAL_WEIGHT:
            return 0.0
        ratio = (self.weight - INITIAL_WEIGHT) / (MAX_WEIGHT - INITIAL_WEIGHT)
        return max(0.0, min(1.0, ratio))
