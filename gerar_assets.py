import os
import pygame


def create_player_sprite(output_path: str):
    """Gera proceduralmente o sprite do jogador corredor (160x200) com fundo transparente."""
    w, h = 160, 200
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2

    outline = (20, 26, 38)

    # 1. Pernas e tênis esportivos (visíveis à frente e atrás no topo/base)
    left_shoe = pygame.Rect(cx - 38, 18, 28, 38)
    right_shoe = pygame.Rect(cx + 10, 28, 28, 38)
    for shoe in (left_shoe, right_shoe):
        pygame.draw.rect(surf, outline, shoe.inflate(6, 6), border_radius=12)
        pygame.draw.rect(surf, (245, 248, 252), shoe, border_radius=10)
        # Sola e detalhe vermelho esportivo
        pygame.draw.rect(
            surf, (231, 76, 60), (shoe.x + 3, shoe.y + 4, shoe.w - 6, 14), border_radius=6
        )
        pygame.draw.line(
            surf, (52, 152, 219), (shoe.x + 5, shoe.y + 22), (shoe.right - 5, shoe.y + 22), 3
        )

    # 2. Braços flexionados nas laterais (mangas + mãos com munhequeira)
    left_arm = pygame.Rect(14, cy - 34, 28, 56)
    right_arm = pygame.Rect(w - 42, cy - 18, 28, 56)
    for arm, hand_y in ((left_arm, left_arm.top - 8), (right_arm, right_arm.top - 8)):
        pygame.draw.rect(surf, outline, arm.inflate(6, 6), border_radius=12)
        pygame.draw.rect(surf, (41, 128, 185), arm, border_radius=10)
        # Munhequeira amarela
        wrist = pygame.Rect(arm.x + 2, arm.y + 2, arm.w - 4, 12)
        pygame.draw.rect(surf, (241, 196, 15), wrist, border_radius=5)
        # Mão/punho
        pygame.draw.circle(surf, outline, (arm.centerx, hand_y + 4), 13)
        pygame.draw.circle(surf, (245, 198, 165), (arm.centerx, hand_y + 4), 10)

    # 3. Tronco / Camiseta esportiva azul-ciano vibrante
    torso = pygame.Rect(cx - 46, cy - 44, 92, 96)
    pygame.draw.rect(surf, outline, torso.inflate(8, 8), border_radius=26)
    # Sombra base 3D
    pygame.draw.rect(surf, (26, 82, 118), torso, border_radius=24)
    # Parte iluminada principal
    pygame.draw.rect(
        surf, (52, 152, 219), pygame.Rect(torso.x, torso.y, torso.w - 10, torso.h - 6), border_radius=22
    )
    # Faixa esportiva ciano e amarela central
    pygame.draw.rect(
        surf, (46, 204, 213), (cx - 18, torso.y + 6, 36, torso.h - 14), border_radius=10
    )
    pygame.draw.rect(
        surf, (241, 196, 15), (cx - 7, torso.y + 8, 14, torso.h - 18), border_radius=6
    )

    # 4. Mochila laranja/vermelha nas costas (parte inferior do tronco)
    pack = pygame.Rect(cx - 34, torso.bottom - 42, 68, 48)
    pygame.draw.rect(surf, outline, pack.inflate(6, 6), border_radius=16)
    pygame.draw.rect(surf, (230, 126, 34), pack, border_radius=14)
    # Bolso traseiro e alças
    pocket = pygame.Rect(pack.x + 8, pack.bottom - 20, pack.w - 16, 14)
    pygame.draw.rect(surf, (211, 84, 0), pocket, border_radius=6)
    pygame.draw.rect(surf, (255, 220, 140), pack, width=2, border_radius=14)

    # 5. Cabeça, faixa esportiva e boné voltado para frente (topo)
    head_center = (cx, cy - 10)
    # Pescoço / sombra
    pygame.draw.circle(surf, (220, 168, 134), (cx, cy - 16), 24)
    # Aba do boné (voltada para frente/topo)
    brim = pygame.Rect(cx - 24, cy - 58, 48, 28)
    pygame.draw.rect(surf, outline, brim.inflate(6, 6), border_radius=12)
    pygame.draw.rect(surf, (192, 57, 43), brim, border_radius=10)
    pygame.draw.rect(surf, (241, 196, 15), (brim.x + 8, brim.y + 4, brim.w - 16, 5), border_radius=3)

    # Copa do boné
    pygame.draw.circle(surf, outline, head_center, 31)
    pygame.draw.circle(surf, (231, 76, 60), head_center, 27)
    # Painel frontal azul/branco do boné
    pygame.draw.circle(surf, (52, 152, 219), (cx, cy - 16), 16)
    pygame.draw.circle(surf, (255, 255, 255), (cx, cy - 18), 7)
    # Botão no topo do boné
    pygame.draw.circle(surf, (241, 196, 15), (cx, cy - 6), 5)

    pygame.image.save(surf, output_path)


def create_good_food_sprite(output_path: str):
    """Gera proceduralmente o sprite da maçã saudável (140x140) com fundo transparente."""
    w, h = 140, 140
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2 + 6

    # 1. Halo suave verde-dourado translúcido
    pygame.draw.circle(surf, (80, 255, 140, 42), (cx, cy - 2), 62)
    pygame.draw.circle(surf, (255, 225, 90, 58), (cx, cy - 2), 50)

    outline = (22, 55, 28)

    # 2. Contorno externo da maçã (dois lóbulos + base afunilada)
    pygame.draw.circle(surf, outline, (cx - 17, cy - 6), 31)
    pygame.draw.circle(surf, outline, (cx + 17, cy - 6), 31)
    pygame.draw.circle(surf, outline, (cx - 11, cy + 18), 25)
    pygame.draw.circle(surf, outline, (cx + 11, cy + 18), 25)
    pygame.draw.polygon(
        surf,
        outline,
        [(cx - 38, cy + 6), (cx + 38, cy + 6), (cx + 16, cy + 40), (cx - 16, cy + 40)],
    )

    # 3. Sombreamento 3D da base (verde-esmeralda profundo)
    base_green = (27, 145, 74)
    pygame.draw.circle(surf, base_green, (cx - 17, cy - 6), 27)
    pygame.draw.circle(surf, base_green, (cx + 17, cy - 6), 27)
    pygame.draw.circle(surf, base_green, (cx - 11, cy + 18), 21)
    pygame.draw.circle(surf, base_green, (cx + 11, cy + 18), 21)
    pygame.draw.polygon(
        surf,
        base_green,
        [(cx - 34, cy + 6), (cx + 34, cy + 6), (cx + 14, cy + 36), (cx - 14, cy + 36)],
    )

    # 4. Corpo iluminado verde-maçã vibrante
    bright_green = (56, 218, 118)
    pygame.draw.circle(surf, bright_green, (cx - 16, cy - 9), 24)
    pygame.draw.circle(surf, bright_green, (cx + 14, cy - 9), 24)
    pygame.draw.circle(surf, bright_green, (cx - 8, cy + 12), 19)
    pygame.draw.circle(surf, bright_green, (cx + 8, cy + 12), 19)

    # Realce interno amarelo-limão
    pygame.draw.circle(surf, (130, 245, 130), (cx - 17, cy - 13), 14)

    # 5. Brilho especular branco em formato de gota no canto superior esquerdo
    pygame.draw.ellipse(surf, (255, 255, 255, 230), pygame.Rect(cx - 32, cy - 26, 12, 22))
    pygame.draw.circle(surf, (255, 255, 255, 230), (cx - 24, cy + 2), 4)

    # 6. Cavidade do cabinho, cabo marrom e folha verde-limão brilhante
    pygame.draw.ellipse(surf, (22, 110, 54), pygame.Rect(cx - 12, cy - 30, 24, 10))
    stem_pts = [(cx, cy - 25), (cx + 2, cy - 42), (cx + 9, cy - 52)]
    pygame.draw.lines(surf, (70, 42, 20), False, stem_pts, 8)
    pygame.draw.lines(surf, (135, 86, 42), False, stem_pts, 4)

    # Folha com contorno e nervura
    leaf_poly = [(cx + 4, cy - 40), (cx + 26, cy - 54), (cx + 38, cy - 38), (cx + 18, cy - 28)]
    pygame.draw.polygon(surf, outline, leaf_poly)
    leaf_inner = [(cx + 7, cy - 39), (cx + 25, cy - 50), (cx + 33, cy - 39), (cx + 18, cy - 31)]
    pygame.draw.polygon(surf, (165, 245, 65), leaf_inner)
    pygame.draw.line(surf, (230, 255, 160), (cx + 9, cy - 39), (cx + 28, cy - 41), 2)

    pygame.image.save(surf, output_path)


def create_bad_food_sprite(output_path: str):
    """Gera proceduralmente o sprite de hambúrguer fast-food (140x140) com fundo transparente."""
    w, h = 140, 140
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2

    # 1. Halo sutil vermelho/laranja translúcido
    pygame.draw.circle(surf, (235, 60, 45, 48), (cx, cy), 62)
    pygame.draw.circle(surf, (255, 120, 40, 56), (cx, cy), 50)

    outline = (38, 22, 14)

    # 2. Pão inferior dourado-tostado
    bottom_bun = pygame.Rect(cx - 46, cy + 20, 92, 26)
    pygame.draw.rect(surf, outline, bottom_bun.inflate(6, 6), border_radius=14)
    pygame.draw.rect(surf, (212, 138, 52), bottom_bun, border_radius=12)
    pygame.draw.rect(
        surf, (238, 170, 78), (bottom_bun.x + 6, bottom_bun.y + 3, bottom_bun.w - 12, 8), border_radius=5
    )

    # 3. Hambúrguer de carne grelhada suculento
    patty = pygame.Rect(cx - 50, cy + 2, 100, 22)
    pygame.draw.rect(surf, outline, patty.inflate(6, 6), border_radius=12)
    pygame.draw.rect(surf, (105, 48, 28), patty, border_radius=10)
    # Marcas de grelha / textura nas bordas
    for gx in range(patty.x + 12, patty.right - 12, 18):
        pygame.draw.line(surf, (68, 28, 14), (gx, patty.y + 4), (gx + 6, patty.bottom - 4), 3)

    # 4. Queijo cheddar derretendo com pontas triangulares sobre a carne
    cheese_bar = pygame.Rect(cx - 48, cy - 5, 96, 11)
    pygame.draw.rect(surf, (255, 195, 18), cheese_bar, border_radius=4)
    cheese_drops = [
        [(cx - 38, cy + 4), (cx - 24, cy + 19), (cx - 10, cy + 4)],
        [(cx - 6, cy + 4), (cx + 8, cy + 21), (cx + 22, cy + 4)],
        [(cx + 20, cy + 4), (cx + 34, cy + 16), (cx + 44, cy + 4)],
    ]
    for tri in cheese_drops:
        pygame.draw.polygon(surf, outline, [(p[0], p[1] + 2) for p in tri])
        pygame.draw.polygon(surf, (255, 205, 25), tri)

    # 5. Rodelas de tomate vermelho e alface ondulada
    pygame.draw.rect(surf, (220, 42, 42), (cx - 42, cy - 13, 40, 10), border_radius=5)
    pygame.draw.rect(surf, (220, 42, 42), (cx + 2, cy - 13, 40, 10), border_radius=5)
    for lx in range(cx - 44, cx + 45, 14):
        pygame.draw.circle(surf, outline, (lx, cy - 14), 10)
        pygame.draw.circle(surf, (95, 215, 70), (lx, cy - 14), 8)

    # 6. Pão superior abobadado dourado com brilho e sementes de gergelim
    top_bun_rect = pygame.Rect(cx - 48, cy - 48, 96, 44)
    pygame.draw.ellipse(surf, outline, top_bun_rect.inflate(6, 6))
    pygame.draw.ellipse(surf, (226, 150, 56), top_bun_rect)
    # Topo arredondado brilhante
    pygame.draw.ellipse(
        surf,
        (246, 186, 88),
        pygame.Rect(top_bun_rect.x + 8, top_bun_rect.y + 4, top_bun_rect.w - 20, 22),
    )
    # Recorte plano na base do pão superior
    pygame.draw.rect(surf, (214, 138, 48), (cx - 45, cy - 22, 90, 10), border_radius=4)

    # Sementes de gergelim creme espalhadas
    seeds = [
        (cx - 26, cy - 34),
        (cx - 8, cy - 40),
        (cx + 14, cy - 36),
        (cx + 28, cy - 28),
        (cx - 16, cy - 25),
        (cx + 4, cy - 27),
    ]
    for sx, sy in seeds:
        pygame.draw.ellipse(surf, (255, 244, 210), pygame.Rect(sx, sy, 8, 5))

    pygame.image.save(surf, output_path)


def main():
    pygame.init()
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images")
    os.makedirs(out_dir, exist_ok=True)

    player_path = os.path.join(out_dir, "player.png")
    good_path = os.path.join(out_dir, "good_food.png")
    bad_path = os.path.join(out_dir, "bad_food.png")

    create_player_sprite(player_path)
    create_good_food_sprite(good_path)
    create_bad_food_sprite(bad_path)

    print("Sprites gerados com sucesso:", flush=True)
    print(f" - {player_path}", flush=True)
    print(f" - {good_path}", flush=True)
    print(f" - {bad_path}", flush=True)


if __name__ == "__main__":
    main()
