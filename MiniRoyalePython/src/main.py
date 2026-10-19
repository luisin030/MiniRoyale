import os
import math
import random
import pygame

pygame.init()

# =========================================================
# CONFIGURAÇÕES
# =========================================================

WIDTH = 1100
HEIGHT = 800
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Royale - Python")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 22)
SMALL = pygame.font.SysFont("arial", 16)
BIG = pygame.font.SysFont("arial", 34, bold=True)

ARENA = pygame.Rect(120, 40, 860, 620)

AGGRO_RANGE = 260

# =========================================================
# CORES
# =========================================================

BLUE = (70, 130, 240)
RED = (225, 70, 70)

GREEN = (70, 180, 90)
DARK_GREEN = (35, 110, 55)

PURPLE = (150, 80, 200)

WHITE = (245, 245, 245)
BLACK = (25, 25, 25)
GRAY = (95, 95, 95)

RIVER = (65, 145, 190)
BRIDGE = (160, 120, 75)

GOLD = (230, 190, 65)
PINK = (235, 120, 170)

# =========================================================
# ASSETS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ASSETS_DIR = os.path.join(
    BASE_DIR,
    "assets"
)


def load_image(relative_path, size):

    path = os.path.join(
        ASSETS_DIR,
        relative_path
    )

    image = pygame.image.load(
        path
    ).convert_alpha()

    return pygame.transform.smoothscale(
        image,
        size
    )


KNIGHT_IMG = load_image(
    os.path.join("units", "knight.png"),
    (68, 68)
)

ARCHER_IMG = load_image(
    os.path.join("units", "archer.png"),
    (68, 68)
)

GIANT_IMG = load_image(
    os.path.join("units", "giant.png"),
    (92, 92)
)

PRINCESS_BLUE_IMG = load_image(
    os.path.join(
        "towers",
        "princess_blue.png"
    ),
    (105, 105)
)

PRINCESS_RED_IMG = load_image(
    os.path.join(
        "towers",
        "princess_red.png"
    ),
    (105, 105)
)

KING_BLUE_IMG = load_image(
    os.path.join(
        "towers",
        "king_blue.png"
    ),
    (125, 125)
)

KING_RED_IMG = load_image(
    os.path.join(
        "towers",
        "king_red.png"
    ),
    (125, 125)
)

# =========================================================
# PROJÉTIL
# =========================================================

class Projectile:

    def __init__(
        self,
        start,
        target,
        damage,
        color,
        speed=350
    ):

        self.pos = pygame.Vector2(start)

        self.target = target

        self.damage = damage
        self.color = color
        self.speed = speed

        self.alive = True


    def update(self, dt):

        if not self.alive:
            return

        if self.target.hp <= 0:
            self.alive = False
            return

        if hasattr(
            self.target,
            "pos"
        ):
            target_pos = pygame.Vector2(
                self.target.pos
            )
        else:
            target_pos = pygame.Vector2(
                self.target.rect.center
            )

        direction = target_pos - self.pos

        distance = direction.length()

        if distance <= 10:

            if hasattr(
                self.target,
                "hit"
            ):
                self.target.hit(
                    self.damage
                )
            else:
                self.target.hp = max(
                    0,
                    self.target.hp - self.damage
                )

            self.alive = False
            return

        if distance > 0:

            self.pos += (
                direction.normalize()
                * self.speed
                * dt
            )


    def draw(self):

        pygame.draw.circle(
            screen,
            self.color,
            (
                int(self.pos.x),
                int(self.pos.y)
            ),
            6
        )

# =========================================================
# TORRE
# =========================================================

class Tower:

    def __init__(
        self,
        x,
        y,
        team,
        tower_type,
        lane=None
    ):

        self.rect = pygame.Rect(
            x,
            y,
            75,
            75
        )

        self.team = team
        self.tower_type = tower_type
        self.lane = lane

        if tower_type == "king":

            self.hp = 1200
            self.damage = 32
            self.attack_range = 190
            self.attack_interval = 0.9

        else:

            self.hp = 800
            self.damage = 26
            self.attack_range = 180
            self.attack_interval = 0.8

        self.max_hp = self.hp
        self.attack_timer = 0

        self.crown_counted = False


    def hit(self, damage):

        self.hp = max(
            0,
            self.hp - damage
        )


    def is_alive(self):

        return self.hp > 0


    def find_target(self, units):

        closest = None
        closest_distance = float("inf")

        tower_position = pygame.Vector2(
            self.rect.center
        )

        for unit in units:

            if unit.team == self.team:
                continue

            if unit.hp <= 0:
                continue

            distance = tower_position.distance_to(
                unit.pos
            )

            if (
                distance <= self.attack_range
                and
                distance < closest_distance
            ):
                closest = unit
                closest_distance = distance

        return closest


    def update(
        self,
        dt,
        units,
        projectiles
    ):

        if not self.is_alive():
            return

        self.attack_timer -= dt

        target = self.find_target(
            units
        )

        if target is None:
            return

        if self.attack_timer <= 0:

            projectiles.append(
                Projectile(
                    self.rect.center,
                    target,
                    self.damage,
                    GOLD,
                    400
                )
            )

            self.attack_timer = (
                self.attack_interval
            )


    def draw(self):

        if not self.is_alive():
            return

        if self.tower_type == "king":

            if self.team == "blue":
                image = KING_BLUE_IMG
            else:
                image = KING_RED_IMG

        else:

            if self.team == "blue":
                image = PRINCESS_BLUE_IMG
            else:
                image = PRINCESS_RED_IMG

        rect = image.get_rect(
            center=self.rect.center
        )

        screen.blit(
            image,
            rect
        )

        bar_width = 80

        bar = pygame.Rect(
            self.rect.centerx
            - bar_width // 2,
            self.rect.top - 17,
            bar_width,
            8
        )

        pygame.draw.rect(
            screen,
            GRAY,
            bar
        )

        ratio = (
            self.hp
            / self.max_hp
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                bar.x,
                bar.y,
                int(
                    bar.w
                    * ratio
                ),
                bar.h
            )
        )

# =========================================================
# UNIDADE
# =========================================================

class Unit:

    UNIT_DATA = {

        "knight": {
            "name": "Cavaleiro",
            "cost": 3,
            "hp": 180,
            "damage": 28,
            "speed": 95,
            "range": 42,
            "attack_interval": 0.8,
            "targets_units": True
        },

        "archer": {
            "name": "Arqueira",
            "cost": 3,
            "hp": 100,
            "damage": 20,
            "speed": 90,
            "range": 125,
            "attack_interval": 0.95,
            "targets_units": True
        },

        "giant": {
            "name": "Gigante",
            "cost": 5,
            "hp": 420,
            "damage": 45,
            "speed": 58,
            "range": 48,
            "attack_interval": 1.2,
            "targets_units": False
        }
    }


    def __init__(
        self,
        x,
        y,
        team,
        unit_type
    ):

        data = self.UNIT_DATA[
            unit_type
        ]

        self.pos = pygame.Vector2(
            x,
            y
        )

        self.team = team
        self.unit_type = unit_type

        self.name = data["name"]

        self.hp = data["hp"]
        self.max_hp = data["hp"]

        self.damage = data["damage"]
        self.speed = data["speed"]
        self.range = data["range"]

        self.attack_interval = data[
            "attack_interval"
        ]

        self.targets_units = data[
            "targets_units"
        ]

        self.timer = 0

        self.unit_target = None

        self.tower_target = None

        self.locked_on_tower = False

        # =================================================
        # ANIMAÇÃO
        # =================================================

        self.animation_time = random.uniform(
            0,
            10
        )

        self.is_moving = False

        self.attack_animation = 0

        self.attack_animation_duration = 0.18

        self.direction_x = 1

        self.hit_flash = 0

        self.last_hp = self.hp

        # =================================================
        # LANE
        # =================================================

        if x < ARENA.centerx:
            self.lane = "left"
        else:
            self.lane = "right"

        # =================================================
        # PONTES
        # =================================================

        self.left_bridge = pygame.Vector2(
            ARENA.x + 220,
            ARENA.centery
        )

        self.right_bridge = pygame.Vector2(
            ARENA.right - 220,
            ARENA.centery
        )

        if self.lane == "left":
            self.bridge_target = self.left_bridge
        else:
            self.bridge_target = self.right_bridge

        self.crossed_bridge = False


    # =====================================================
    # PONTE
    # =====================================================

    def update_bridge_status(self):

        if self.crossed_bridge:
            return

        if self.team == "blue":

            if self.pos.y < ARENA.centery - 8:
                self.crossed_bridge = True

        else:

            if self.pos.y > ARENA.centery + 8:
                self.crossed_bridge = True


    # =====================================================
    # MOVIMENTO
    # =====================================================

    def move_towards(
        self,
        target,
        dt
    ):

        delta = target - self.pos

        self.is_moving = False

        if delta.length() <= 0:
            return

        direction = delta.normalize()

        if abs(direction.x) > 0.05:

            if direction.x > 0:
                self.direction_x = 1
            else:
                self.direction_x = -1

        movement = (
            direction
            * self.speed
            * dt
        )

        if movement.length() > delta.length():

            self.pos = pygame.Vector2(
                target
            )

        else:

            self.pos += movement

        self.is_moving = True

        self.update_bridge_status()


    # =====================================================
    # TROPA INIMIGA
    # =====================================================

    def valid_unit_target(
        self,
        target
    ):

        if target is None:
            return False

        if target.hp <= 0:
            return False

        if target.team == self.team:
            return False

        distance = self.pos.distance_to(
            target.pos
        )

        if distance > AGGRO_RANGE + 40:
            return False

        return True


    def find_enemy_unit(
        self,
        units
    ):

        if not self.targets_units:

            self.unit_target = None
            return None

        if self.valid_unit_target(
            self.unit_target
        ):
            return self.unit_target

        self.unit_target = None

        closest = None
        closest_distance = float("inf")

        for other in units:

            if other is self:
                continue

            if other.team == self.team:
                continue

            if other.hp <= 0:
                continue

            distance = self.pos.distance_to(
                other.pos
            )

            if distance > AGGRO_RANGE:
                continue

            if distance < closest_distance:

                closest = other
                closest_distance = distance

        self.unit_target = closest

        return closest


    # =====================================================
    # TORRE ALVO
    # =====================================================

    def choose_target_tower(
        self,
        towers
    ):

        for tower in towers:

            if (
                tower.team != self.team
                and
                tower.tower_type == "princess"
                and
                tower.lane == self.lane
                and
                tower.is_alive()
            ):
                return tower

        for tower in towers:

            if (
                tower.team != self.team
                and
                tower.tower_type == "king"
                and
                tower.is_alive()
            ):
                return tower

        return None


    # =====================================================
    # NOVA REGRA:
    # TORRE NA FRENTE > TROPA ATRÁS
    # =====================================================

    def should_attack_tower_first(
        self,
        tower,
        enemy
    ):

        if tower is None:
            return False

        if enemy is None:
            return True

        tower_pos = pygame.Vector2(
            tower.rect.center
        )

        distance_to_tower = (
            self.pos.distance_to(
                tower_pos
            )
        )

        distance_to_enemy = (
            self.pos.distance_to(
                enemy.pos
            )
        )

        # Se a torre está mais próxima,
        # ela está "na frente".
        return (
            distance_to_tower
            <= distance_to_enemy
        )


    # =====================================================
    # ATAQUE VISUAL
    # =====================================================

    def start_attack_animation(
        self
    ):

        self.attack_animation = (
            self.attack_animation_duration
        )


    # =====================================================
    # ATAQUE TROPA
    # =====================================================

    def attack_unit(
        self,
        enemy,
        dt,
        projectiles
    ):

        if enemy is None:
            return False

        if enemy.hp <= 0:

            self.unit_target = None
            return False

        distance = self.pos.distance_to(
            enemy.pos
        )

        if distance <= self.range:

            self.is_moving = False

            self.timer -= dt

            if self.timer <= 0:

                self.start_attack_animation()

                if self.unit_type == "archer":

                    projectiles.append(
                        Projectile(
                            self.pos,
                            enemy,
                            self.damage,
                            PINK,
                            380
                        )
                    )

                else:

                    enemy.hp = max(
                        0,
                        enemy.hp - self.damage
                    )

                self.timer = (
                    self.attack_interval
                )

            return True

        if distance <= AGGRO_RANGE + 40:

            self.move_towards(
                enemy.pos,
                dt
            )

            return True

        self.unit_target = None

        return False


    # =====================================================
    # ATAQUE TORRE
    # =====================================================

    def attack_locked_tower(
        self,
        dt,
        projectiles
    ):

        tower = self.tower_target

        if tower is None:

            self.locked_on_tower = False
            return False

        if not tower.is_alive():

            self.locked_on_tower = False
            self.tower_target = None

            return False

        tower_pos = pygame.Vector2(
            tower.rect.center
        )

        distance = self.pos.distance_to(
            tower_pos
        )

        if distance > self.range:

            self.move_towards(
                tower_pos,
                dt
            )

            return True

        self.is_moving = False

        self.timer -= dt

        if self.timer <= 0:

            self.start_attack_animation()

            if self.unit_type == "archer":

                projectiles.append(
                    Projectile(
                        self.pos,
                        tower,
                        self.damage,
                        PINK,
                        380
                    )
                )

            else:

                tower.hit(
                    self.damage
                )

            self.timer = (
                self.attack_interval
            )

        return True


    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        dt,
        units,
        towers,
        projectiles
    ):

        if self.hp <= 0:
            return

        self.update_bridge_status()

        self.animation_time += dt

        self.is_moving = False

        # =================================================
        # ANIMAÇÃO
        # =================================================

        if self.attack_animation > 0:

            self.attack_animation -= dt

            if self.attack_animation < 0:
                self.attack_animation = 0

        # =================================================
        # DANO
        # =================================================

        if self.hp < self.last_hp:

            self.hit_flash = 0.12

        self.last_hp = self.hp

        if self.hit_flash > 0:

            self.hit_flash -= dt

        # =================================================
        # SE JÁ COMEÇOU A BATER NA TORRE
        # =================================================

        if self.locked_on_tower:

            if self.attack_locked_tower(
                dt,
                projectiles
            ):
                return

        # =================================================
        # ESCOLHER TORRE E TROPA
        # =================================================

        target_tower = (
            self.choose_target_tower(
                towers
            )
        )

        enemy = self.find_enemy_unit(
            units
        )

        # =================================================
        # REGRA PRINCIPAL
        #
        # Se a torre estiver mais perto do que
        # a tropa, então a torre está na frente.
        # =================================================

        if (
            target_tower is not None
            and
            self.should_attack_tower_first(
                target_tower,
                enemy
            )
        ):

            tower_pos = pygame.Vector2(
                target_tower.rect.center
            )

            distance_to_tower = (
                self.pos.distance_to(
                    tower_pos
                )
            )

            # Já chegou na torre.
            if distance_to_tower <= self.range:

                self.locked_on_tower = True

                self.tower_target = (
                    target_tower
                )

                self.unit_target = None

                self.attack_locked_tower(
                    dt,
                    projectiles
                )

                return

        # =================================================
        # TROPA NA FRENTE
        # =================================================

        if enemy is not None:

            if self.attack_unit(
                enemy,
                dt,
                projectiles
            ):
                return

        self.unit_target = None

        # =================================================
        # AINDA NÃO CRUZOU PONTE
        # =================================================

        if not self.crossed_bridge:

            distance = self.pos.distance_to(
                self.bridge_target
            )

            if distance > 8:

                self.move_towards(
                    self.bridge_target,
                    dt
                )

                return

            self.crossed_bridge = True

        # =================================================
        # IR PARA TORRE
        # =================================================

        target_tower = (
            self.choose_target_tower(
                towers
            )
        )

        if target_tower is None:
            return

        tower_pos = pygame.Vector2(
            target_tower.rect.center
        )

        distance_to_tower = (
            self.pos.distance_to(
                tower_pos
            )
        )

        if distance_to_tower > self.range:

            self.move_towards(
                tower_pos,
                dt
            )

            return

        # =================================================
        # COMEÇOU ATAQUE NA TORRE
        # =================================================

        self.locked_on_tower = True

        self.tower_target = (
            target_tower
        )

        self.unit_target = None

        self.attack_locked_tower(
            dt,
            projectiles
        )


    # =====================================================
    # SPRITE
    # =====================================================

    def get_sprite(self):

        if self.unit_type == "knight":
            return KNIGHT_IMG

        if self.unit_type == "archer":
            return ARCHER_IMG

        return GIANT_IMG


    # =====================================================
    # DRAW
    # =====================================================

    def draw(self):

        image = self.get_sprite()

        if self.direction_x < 0:

            image = pygame.transform.flip(
                image,
                True,
                False
            )

        offset_y = 0
        rotation = 0

        if self.is_moving:

            offset_y = (
                abs(
                    math.sin(
                        self.animation_time
                        * 10
                    )
                )
                * 4
            )

            rotation = (
                math.sin(
                    self.animation_time
                    * 8
                )
                * 3
            )

        attack_offset = 0
        scale_factor = 1.0

        if self.attack_animation > 0:

            progress = (
                self.attack_animation
                /
                self.attack_animation_duration
            )

            attack_offset = (
                math.sin(
                    progress
                    * math.pi
                )
                * 9
            )

            scale_factor = 1.08

        original_size = (
            image.get_size()
        )

        image = pygame.transform.smoothscale(
            image,
            (
                int(
                    original_size[0]
                    * scale_factor
                ),
                int(
                    original_size[1]
                    * scale_factor
                )
            )
        )

        image = pygame.transform.rotate(
            image,
            rotation
        )

        if self.hit_flash > 0:

            flash = image.copy()

            flash.fill(
                (
                    120,
                    25,
                    25,
                    0
                ),
                special_flags=pygame.BLEND_RGB_ADD
            )

            image = flash

        draw_x = self.pos.x

        draw_y = (
            self.pos.y
            - offset_y
        )

        if self.direction_x > 0:
            draw_x += attack_offset
        else:
            draw_x -= attack_offset

        pygame.draw.ellipse(
            screen,
            (20, 20, 20),
            (
                int(self.pos.x - 22),
                int(self.pos.y + 18),
                44,
                13
            )
        )

        rect = image.get_rect(
            center=(
                int(draw_x),
                int(draw_y)
            )
        )

        screen.blit(
            image,
            rect
        )

        if self.team == "blue":
            team_color = BLUE
        else:
            team_color = RED

        pygame.draw.circle(
            screen,
            team_color,
            (
                int(self.pos.x),
                int(self.pos.y - 39)
            ),
            5
        )

        if self.unit_type == "giant":
            bar_width = 55
        else:
            bar_width = 45

        x = int(
            self.pos.x
            - bar_width / 2
        )

        y = int(
            self.pos.y - 48
        )

        pygame.draw.rect(
            screen,
            GRAY,
            (
                x,
                y,
                bar_width,
                5
            )
        )

        ratio = max(
            0,
            self.hp / self.max_hp
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                x,
                y,
                int(
                    bar_width
                    * ratio
                ),
                5
            )
        )

# =========================================================
# GAME
# =========================================================

class Game:

    def __init__(self):

        self.units = []

        self.projectiles = []

        # =================================================
        # TORRES AZUIS
        # =================================================

        self.blue_left = Tower(
            250,
            500,
            "blue",
            "princess",
            "left"
        )

        self.blue_right = Tower(
            775,
            500,
            "blue",
            "princess",
            "right"
        )

        self.blue_king = Tower(
            WIDTH // 2 - 38,
            570,
            "blue",
            "king"
        )

        # =================================================
        # TORRES VERMELHAS
        # =================================================

        self.red_left = Tower(
            250,
            120,
            "red",
            "princess",
            "left"
        )

        self.red_right = Tower(
            775,
            120,
            "red",
            "princess",
            "right"
        )

        self.red_king = Tower(
            WIDTH // 2 - 38,
            55,
            "red",
            "king"
        )

        self.towers = [
            self.blue_left,
            self.blue_right,
            self.blue_king,

            self.red_left,
            self.red_right,
            self.red_king
        ]

        # =================================================
        # ELIXIR
        # =================================================

        self.elixir = 5.0

        self.max_elixir = 10.0

        self.normal_elixir_rate = 0.6

        self.elixir_rate = (
            self.normal_elixir_rate
        )

        # =================================================
        # PARTIDA
        # =================================================

        self.match_time = 180.0

        self.double_elixir = False

        self.blue_crowns = 0
        self.red_crowns = 0

        # =================================================
        # CARTAS
        # =================================================

        self.selected_card = None

        self.card_types = [
            "knight",
            "archer",
            "giant"
        ]

        self.card_rects = []

        card_width = 170
        card_height = 65
        gap = 15

        total_width = (
            card_width * 3
            + gap * 2
        )

        start_x = (
            WIDTH
            - total_width
        ) // 2

        for i in range(3):

            self.card_rects.append(
                pygame.Rect(
                    start_x
                    + i
                    * (
                        card_width
                        + gap
                    ),
                    710,
                    card_width,
                    card_height
                )
            )

        # =================================================
        # IA
        # =================================================

        self.enemy_spawn_timer = 2.5

        # =================================================
        # ESTADO
        # =================================================

        self.game_over = False

        self.winner = None


    def reset(self):

        self.__init__()


    # =====================================================
    # CARTAS
    # =====================================================

    def try_select_card(
        self,
        pos
    ):

        for rect, card_type in zip(
            self.card_rects,
            self.card_types
        ):

            if rect.collidepoint(
                pos
            ):

                if (
                    self.selected_card
                    == card_type
                ):
                    self.selected_card = None
                else:
                    self.selected_card = card_type

                return True

        return False


    # =====================================================
    # PLAYER
    # =====================================================

    def spawn_player_unit(
        self,
        pos
    ):

        if self.selected_card is None:
            return

        if not ARENA.collidepoint(
            pos
        ):
            return

        if pos[1] <= ARENA.centery:
            return

        data = Unit.UNIT_DATA[
            self.selected_card
        ]

        cost = data["cost"]

        if self.elixir < cost:
            return

        self.units.append(
            Unit(
                pos[0],
                pos[1],
                "blue",
                self.selected_card
            )
        )

        self.elixir -= cost

        self.selected_card = None


    # =====================================================
    # IA
    # =====================================================

    def spawn_enemy_unit(self):

        unit_type = random.choice(
            self.card_types
        )

        lane = random.choice(
            [
                "left",
                "right"
            ]
        )

        if lane == "left":
            x = 320
        else:
            x = 730

        y = 200

        self.units.append(
            Unit(
                x,
                y,
                "red",
                unit_type
            )
        )


    # =====================================================
    # EVENTOS
    # =====================================================

    def handle_event(
        self,
        event
    ):

        if (
            event.type == pygame.KEYDOWN
            and
            event.key == pygame.K_r
        ):

            self.reset()
            return

        if self.game_over:
            return

        if (
            event.type
            == pygame.MOUSEBUTTONDOWN
            and
            event.button == 1
        ):

            if self.try_select_card(
                event.pos
            ):
                return

            self.spawn_player_unit(
                event.pos
            )


    # =====================================================
    # COROAS
    # =====================================================

    def update_crowns(self):

        for tower in self.towers:

            if tower.is_alive():
                continue

            if tower.crown_counted:
                continue

            tower.crown_counted = True

            if tower.tower_type == "princess":

                if tower.team == "red":
                    self.blue_crowns += 1
                else:
                    self.red_crowns += 1

            else:

                if tower.team == "red":
                    self.blue_crowns = 3
                else:
                    self.red_crowns = 3


    # =====================================================
    # FIM POR TEMPO
    # =====================================================

    def finish_by_time(self):

        if self.blue_crowns > self.red_crowns:

            self.winner = "Você"

        elif self.red_crowns > self.blue_crowns:

            self.winner = "Inimigo"

        else:

            self.winner = "Empate"

        self.game_over = True


    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        dt
    ):

        if self.game_over:
            return

        # =================================================
        # TEMPO
        # =================================================

        self.match_time -= dt

        if self.match_time < 0:
            self.match_time = 0

        # =================================================
        # ELIXIR x2
        # =================================================

        if (
            self.match_time <= 60
            and
            not self.double_elixir
        ):

            self.double_elixir = True

            self.elixir_rate = (
                self.normal_elixir_rate
                * 2
            )

        # =================================================
        # ELIXIR
        # =================================================

        self.elixir = min(
            self.max_elixir,
            self.elixir
            + self.elixir_rate
            * dt
        )

        # =================================================
        # IA
        # =================================================

        self.enemy_spawn_timer -= dt

        if self.enemy_spawn_timer <= 0:

            self.spawn_enemy_unit()

            if self.double_elixir:

                self.enemy_spawn_timer = random.uniform(
                    2.0,
                    3.5
                )

            else:

                self.enemy_spawn_timer = random.uniform(
                    3.0,
                    5.0
                )

        # =================================================
        # UNIDADES
        # =================================================

        for unit in self.units:

            unit.update(
                dt,
                self.units,
                self.towers,
                self.projectiles
            )

        # =================================================
        # TORRES
        # =================================================

        for tower in self.towers:

            tower.update(
                dt,
                self.units,
                self.projectiles
            )

        # =================================================
        # PROJÉTEIS
        # =================================================

        for projectile in self.projectiles:

            projectile.update(
                dt
            )

        self.projectiles = [
            projectile
            for projectile
            in self.projectiles
            if projectile.alive
        ]

        # =================================================
        # REMOVER MORTOS
        # =================================================

        self.units = [
            unit
            for unit
            in self.units
            if unit.hp > 0
        ]

        # =================================================
        # COROAS
        # =================================================

        self.update_crowns()

        # =================================================
        # VITÓRIA
        # =================================================

        if not self.red_king.is_alive():

            self.game_over = True
            self.winner = "Você"
            return

        if not self.blue_king.is_alive():

            self.game_over = True
            self.winner = "Inimigo"
            return

        if self.match_time <= 0:

            self.finish_by_time()


    # =====================================================
    # ARENA
    # =====================================================

    def draw_arena(self):

        screen.fill(
            (30, 30, 35)
        )

        pygame.draw.rect(
            screen,
            DARK_GREEN,
            ARENA,
            border_radius=14
        )

        river = pygame.Rect(
            ARENA.x,
            ARENA.centery - 32,
            ARENA.width,
            64
        )

        pygame.draw.rect(
            screen,
            RIVER,
            river
        )

        bridge_left = pygame.Rect(
            ARENA.x + 170,
            ARENA.centery - 32,
            110,
            64
        )

        bridge_right = pygame.Rect(
            ARENA.right - 280,
            ARENA.centery - 32,
            110,
            64
        )

        pygame.draw.rect(
            screen,
            BRIDGE,
            bridge_left
        )

        pygame.draw.rect(
            screen,
            BRIDGE,
            bridge_right
        )


    # =====================================================
    # CARTAS
    # =====================================================

    def draw_cards(self):

        for rect, card_type in zip(
            self.card_rects,
            self.card_types
        ):

            data = Unit.UNIT_DATA[
                card_type
            ]

            selected = (
                self.selected_card
                == card_type
            )

            if selected:
                color = PURPLE
            else:
                color = (
                    85,
                    60,
                    110
                )

            pygame.draw.rect(
                screen,
                color,
                rect,
                border_radius=10
            )

            if card_type == "knight":
                icon = KNIGHT_IMG

            elif card_type == "archer":
                icon = ARCHER_IMG

            else:
                icon = GIANT_IMG

            icon_small = (
                pygame.transform.smoothscale(
                    icon,
                    (48, 48)
                )
            )

            screen.blit(
                icon_small,
                (
                    rect.x + 7,
                    rect.y + 8
                )
            )

            name = SMALL.render(
                data["name"],
                True,
                WHITE
            )

            cost = SMALL.render(
                f"{data['cost']} Elixir",
                True,
                WHITE
            )

            screen.blit(
                name,
                (
                    rect.x + 61,
                    rect.y + 13
                )
            )

            screen.blit(
                cost,
                (
                    rect.x + 61,
                    rect.y + 36
                )
            )


    # =====================================================
    # TEMPO
    # =====================================================

    def get_time_text(self):

        total_seconds = int(
            math.ceil(
                self.match_time
            )
        )

        minutes = (
            total_seconds
            // 60
        )

        seconds = (
            total_seconds
            % 60
        )

        return (
            f"{minutes:02d}:{seconds:02d}"
        )


    # =====================================================
    # UI
    # =====================================================

    def draw_ui(self):

        text = FONT.render(
            f"Elixir: {self.elixir:.1f}/10",
            True,
            WHITE
        )

        screen.blit(
            text,
            (
                25,
                730
            )
        )

        blue_text = FONT.render(
            f"Você {self.blue_crowns} Coroas",
            True,
            BLUE
        )

        red_text = FONT.render(
            f"{self.red_crowns} Coroas Inimigo",
            True,
            RED
        )

        screen.blit(
            blue_text,
            (
                135,
                8
            )
        )

        screen.blit(
            red_text,
            (
                WIDTH
                - red_text.get_width()
                - 135,
                8
            )
        )

        timer = BIG.render(
            self.get_time_text(),
            True,
            WHITE
        )

        screen.blit(
            timer,
            timer.get_rect(
                center=(
                    WIDTH // 2,
                    20
                )
            )
        )

        if self.double_elixir:

            double_text = SMALL.render(
                "ELIXIR x2",
                True,
                PURPLE
            )

            screen.blit(
                double_text,
                double_text.get_rect(
                    center=(
                        WIDTH // 2,
                        52
                    )
                )
            )

        if self.game_over:

            overlay = pygame.Surface(
                (
                    WIDTH,
                    HEIGHT
                ),
                pygame.SRCALPHA
            )

            overlay.fill(
                (
                    0,
                    0,
                    0,
                    165
                )
            )

            screen.blit(
                overlay,
                (0, 0)
            )

            if self.winner == "Empate":
                result = "Empate!"
            else:
                result = (
                    f"{self.winner} venceu!"
                )

            victory = BIG.render(
                result,
                True,
                WHITE
            )

            crowns = FONT.render(
                (
                    f"Você "
                    f"{self.blue_crowns}"
                    f" x "
                    f"{self.red_crowns} "
                    f"Inimigo"
                ),
                True,
                GOLD
            )

            restart = FONT.render(
                "Pressione R para reiniciar",
                True,
                WHITE
            )

            screen.blit(
                victory,
                victory.get_rect(
                    center=(
                        WIDTH // 2,
                        HEIGHT // 2 - 45
                    )
                )
            )

            screen.blit(
                crowns,
                crowns.get_rect(
                    center=(
                        WIDTH // 2,
                        HEIGHT // 2
                    )
                )
            )

            screen.blit(
                restart,
                restart.get_rect(
                    center=(
                        WIDTH // 2,
                        HEIGHT // 2 + 45
                    )
                )
            )


    # =====================================================
    # DRAW
    # =====================================================

    def draw(self):

        self.draw_arena()

        for tower in self.towers:
            tower.draw()

        for unit in self.units:
            unit.draw()

        for projectile in self.projectiles:
            projectile.draw()

        self.draw_cards()

        self.draw_ui()

        pygame.display.flip()

# =========================================================
# MAIN
# =========================================================

def main():

    game = Game()

    running = True

    while running:

        dt = (
            clock.tick(FPS)
            / 1000
        )

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            else:

                game.handle_event(
                    event
                )

        game.update(dt)

        game.draw()

    pygame.quit()


if __name__ == "__main__":
    main()