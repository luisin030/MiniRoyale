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
pygame.display.set_caption("Mini Royale")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 22)
SMALL = pygame.font.SysFont("arial", 15)
TINY = pygame.font.SysFont("arial", 12)
BIG = pygame.font.SysFont("arial", 34, bold=True)

ARENA = pygame.Rect(120, 40, 860, 620)

AGGRO_RANGE = 250
LANE_AGGRO_WIDTH = 145

RIVER_HALF_HEIGHT = 32
BRIDGE_SAFE_MARGIN = 45

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
CYAN = (80, 210, 255)
ORANGE = (255, 145, 50)

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


# =========================================================
# UNIDADES
# =========================================================

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

GUARD_IMG = load_image(
    os.path.join("units", "guard.png"),
    (72, 72)
)

MUSKETEER_IMG = load_image(
    os.path.join("units", "musketeer.png"),
    (74, 74)
)

BERSERKER_IMG = load_image(
    os.path.join("units", "berserker.png"),
    (78, 78)
)

COLOSSUS_IMG = load_image(
    os.path.join("units", "colossus.png"),
    (100, 100)
)

SCOUT_IMG = load_image(
    os.path.join("units", "scout.png"),
    (68, 68)
)

# =========================================================
# TORRES
# =========================================================

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
# EFEITO
# =========================================================


class ImpactEffect:

    def __init__(
        self,
        pos,
        color,
        size=25,
        duration=0.25
    ):

        self.pos = pygame.Vector2(pos)

        self.color = color

        self.size = size

        self.duration = duration
        self.timer = duration

        self.alive = True

    def update(self, dt):

        self.timer -= dt

        if self.timer <= 0:

            self.alive = False

    def draw(self):

        if not self.alive:
            return

        progress = (
            1
            - self.timer
            / self.duration
        )

        radius = int(
            5
            + self.size
            * progress
        )

        alpha = int(
            255
            * self.timer
            / self.duration
        )

        surface = pygame.Surface(
            (
                radius * 2 + 10,
                radius * 2 + 10
            ),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            surface,
            (
                self.color[0],
                self.color[1],
                self.color[2],
                alpha
            ),
            (
                surface.get_width() // 2,
                surface.get_height() // 2
            ),
            radius,
            3
        )

        rect = surface.get_rect(
            center=(
                int(self.pos.x),
                int(self.pos.y)
            )
        )

        screen.blit(
            surface,
            rect
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
        speed=350,
        projectile_type="default"
    ):

        self.pos = pygame.Vector2(
            start
        )

        self.target = target

        self.damage = damage

        self.color = color
        self.speed = speed

        self.projectile_type = (
            projectile_type
        )

        self.alive = True

        self.trail = []

    def update(
        self,
        dt,
        effects
    ):

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

        self.trail.append(
            pygame.Vector2(
                self.pos
            )
        )

        if len(self.trail) > 6:

            self.trail.pop(0)

        direction = (
            target_pos
            - self.pos
        )

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
                    self.target.hp
                    - self.damage
                )

            if self.projectile_type == "musket":

                effects.append(
                    ImpactEffect(
                        target_pos,
                        GOLD,
                        24,
                        0.22
                    )
                )

            elif self.projectile_type == "bolt":

                effects.append(
                    ImpactEffect(
                        target_pos,
                        CYAN,
                        18,
                        0.18
                    )
                )

            elif self.projectile_type == "arrow":

                effects.append(
                    ImpactEffect(
                        target_pos,
                        PINK,
                        14,
                        0.16
                    )
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

        if len(self.trail) > 1:

            for i, point in enumerate(
                self.trail
            ):

                radius = max(
                    1,
                    int(
                        4
                        * (i + 1)
                        / len(self.trail)
                    )
                )

                pygame.draw.circle(
                    screen,
                    self.color,
                    (
                        int(point.x),
                        int(point.y)
                    ),
                    radius
                )

        if self.projectile_type == "musket":

            pygame.draw.circle(
                screen,
                GOLD,
                (
                    int(self.pos.x),
                    int(self.pos.y)
                ),
                7
            )

            pygame.draw.circle(
                screen,
                WHITE,
                (
                    int(self.pos.x),
                    int(self.pos.y)
                ),
                3
            )

        elif self.projectile_type == "bolt":

            pygame.draw.circle(
                screen,
                CYAN,
                (
                    int(self.pos.x),
                    int(self.pos.y)
                ),
                5
            )

        elif self.projectile_type == "arrow":

            pygame.draw.circle(
                screen,
                PINK,
                (
                    int(self.pos.x),
                    int(self.pos.y)
                ),
                5
            )

        else:

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

    def find_target(
        self,
        units
    ):

        closest = None
        closest_distance = float("inf")

        tower_pos = pygame.Vector2(
            self.rect.center
        )

        for unit in units:

            if unit.team == self.team:
                continue

            if unit.hp <= 0:
                continue

            distance = tower_pos.distance_to(
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
                    400,
                    "default"
                )
            )

            self.attack_timer = (
                self.attack_interval
            )

    def draw(self):

        if not self.is_alive():
            return

        if self.tower_type == "king":

            image = (
                KING_BLUE_IMG
                if self.team == "blue"
                else KING_RED_IMG
            )

        else:

            image = (
                PRINCESS_BLUE_IMG
                if self.team == "blue"
                else PRINCESS_RED_IMG
            )

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
            "targets_units": True,
            "ranged": False
        },

        "archer": {
            "name": "Arqueira",
            "cost": 3,
            "hp": 100,
            "damage": 20,
            "speed": 90,
            "range": 125,
            "attack_interval": 0.95,
            "targets_units": True,
            "ranged": True
        },

        "giant": {
            "name": "Gigante",
            "cost": 5,
            "hp": 420,
            "damage": 45,
            "speed": 58,
            "range": 48,
            "attack_interval": 1.2,
            "targets_units": False,
            "ranged": False
        },

        "guard": {
            "name": "Guarda",
            "cost": 2,
            "hp": 150,
            "damage": 18,
            "speed": 100,
            "range": 45,
            "attack_interval": 0.72,
            "targets_units": True,
            "ranged": False
        },

        "musketeer": {
            "name": "Mosqueteira",
            "cost": 4,
            "hp": 140,
            "damage": 32,
            "speed": 82,
            "range": 165,
            "attack_interval": 1.1,
            "targets_units": True,
            "ranged": True
        },

        "berserker": {
            "name": "Berserker",
            "cost": 4,
            "hp": 210,
            "damage": 36,
            "speed": 120,
            "range": 42,
            "attack_interval": 0.62,
            "targets_units": True,
            "ranged": False
        },

        "colossus": {
            "name": "Colosso",
            "cost": 6,
            "hp": 600,
            "damage": 62,
            "speed": 48,
            "range": 52,
            "attack_interval": 1.45,
            "targets_units": False,
            "ranged": False
        },

        "scout": {
            "name": "Batedora",
            "cost": 2,
            "hp": 80,
            "damage": 15,
            "speed": 125,
            "range": 110,
            "attack_interval": 0.65,
            "targets_units": True,
            "ranged": True
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

        self.ranged = data[
            "ranged"
        ]

        self.timer = 0

        if unit_type in [
            "giant",
            "colossus"
        ]:

            self.collision_radius = 27

        else:

            self.collision_radius = 20

        self.unit_target = None
        self.tower_target = None

        self.locked_on_tower = False

        self.animation_time = (
            random.uniform(
                0,
                10
            )
        )

        self.is_moving = False

        self.attack_animation = 0
        self.attack_animation_duration = 0.18

        self.direction_x = 1

        self.hit_flash = 0
        self.last_hp = self.hp

        if x < ARENA.centerx:
            self.lane = "left"
        else:
            self.lane = "right"

        self.left_bridge = pygame.Vector2(
            ARENA.x + 220,
            ARENA.centery
        )

        self.right_bridge = pygame.Vector2(
            ARENA.right - 220,
            ARENA.centery
        )

        self.bridge_target = (
            self.left_bridge
            if self.lane == "left"
            else self.right_bridge
        )

        self.reached_bridge = False
        self.crossed_bridge = False

    # =====================================================
    # MOVIMENTO
    # =====================================================

    def forward_value(
        self,
        position
    ):

        if self.team == "blue":

            return (
                self.pos.y
                - position.y
            )

        return (
            position.y
            - self.pos.y
        )

    def in_bridge_safe_zone(self):

        top = (
            ARENA.centery
            - RIVER_HALF_HEIGHT
            - BRIDGE_SAFE_MARGIN
        )

        bottom = (
            ARENA.centery
            + RIVER_HALF_HEIGHT
            + BRIDGE_SAFE_MARGIN
        )

        return (
            top
            <= self.pos.y
            <= bottom
        )

    def is_on_enemy_side(
        self,
        position
    ):

        if self.team == "blue":

            return (
                position.y
                <
                ARENA.centery
                - RIVER_HALF_HEIGHT
            )

        return (
            position.y
            >
            ARENA.centery
            + RIVER_HALF_HEIGHT
        )

    def update_bridge_status(self):

        if self.crossed_bridge:
            return

        if self.team == "blue":

            if (
                self.pos.y
                <=
                ARENA.centery
                - RIVER_HALF_HEIGHT
                - 25
            ):

                self.crossed_bridge = True
                self.reached_bridge = True

        else:

            if (
                self.pos.y
                >=
                ARENA.centery
                + RIVER_HALF_HEIGHT
                + 25
            ):

                self.crossed_bridge = True
                self.reached_bridge = True

    def move_towards(
        self,
        target,
        dt
    ):

        target = pygame.Vector2(
            target
        )

        delta = (
            target
            - self.pos
        )

        self.is_moving = False

        if delta.length() <= 0:
            return

        direction = (
            delta.normalize()
        )

        if abs(direction.x) > 0.05:

            self.direction_x = (
                1
                if direction.x > 0
                else -1
            )

        movement = (
            direction
            * self.speed
            * dt
        )

        if (
            movement.length()
            >=
            delta.length()
        ):

            self.pos = pygame.Vector2(
                target
            )

        else:

            self.pos += movement

        self.is_moving = True

        self.update_bridge_status()

    def navigate_bridge(
        self,
        dt
    ):

        if self.crossed_bridge:
            return False

        if not self.reached_bridge:

            distance = (
                self.pos.distance_to(
                    self.bridge_target
                )
            )

            if distance > 5:

                self.move_towards(
                    self.bridge_target,
                    dt
                )

                return True

            self.pos = pygame.Vector2(
                self.bridge_target
            )

            self.reached_bridge = True

        self.pos.x = (
            self.bridge_target.x
        )

        if self.team == "blue":

            exit_y = (
                ARENA.centery
                - RIVER_HALF_HEIGHT
                - 30
            )

        else:

            exit_y = (
                ARENA.centery
                + RIVER_HALF_HEIGHT
                + 30
            )

        bridge_exit = pygame.Vector2(
            self.bridge_target.x,
            exit_y
        )

        distance = (
            self.pos.distance_to(
                bridge_exit
            )
        )

        if distance > 4:

            self.move_towards(
                bridge_exit,
                dt
            )

            self.pos.x = (
                self.bridge_target.x
            )

            return True

        self.pos = pygame.Vector2(
            bridge_exit
        )

        self.crossed_bridge = True
        self.reached_bridge = True

        return False

    def move_towards_enemy(
        self,
        enemy,
        dt
    ):

        if (
            not self.crossed_bridge
            and
            self.is_on_enemy_side(
                enemy.pos
            )
        ):

            self.navigate_bridge(
                dt
            )

            return

        self.move_towards(
            enemy.pos,
            dt
        )

    # =====================================================
    # TARGET
    # =====================================================

    def enemy_in_lane(
        self,
        enemy
    ):

        horizontal_distance = abs(
            enemy.pos.x
            - self.pos.x
        )

        return (
            horizontal_distance
            <= LANE_AGGRO_WIDTH
        )

    def enemy_is_ahead(
        self,
        enemy
    ):

        forward = (
            self.forward_value(
                enemy.pos
            )
        )

        if forward >= -10:
            return True

        distance = (
            self.pos.distance_to(
                enemy.pos
            )
        )

        if (
            distance
            <=
            self.range + 25
        ):

            return True

        return False

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

        distance = (
            self.pos.distance_to(
                target.pos
            )
        )

        if distance > AGGRO_RANGE + 50:
            return False

        if not self.enemy_in_lane(
            target
        ):

            if (
                distance
                >
                self.range + 30
            ):

                return False

        if not self.enemy_is_ahead(
            target
        ):

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

            distance = (
                self.pos.distance_to(
                    other.pos
                )
            )

            if distance > AGGRO_RANGE:
                continue

            if not self.enemy_in_lane(
                other
            ):
                continue

            if not self.enemy_is_ahead(
                other
            ):
                continue

            if distance < closest_distance:

                closest = other
                closest_distance = distance

        self.unit_target = closest

        return closest

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

    def tower_blocks_enemy(
        self,
        tower,
        enemy
    ):

        if tower is None:
            return False

        if enemy is None:
            return False

        tower_pos = pygame.Vector2(
            tower.rect.center
        )

        if (
            abs(
                enemy.pos.x
                - tower_pos.x
            )
            > 115
        ):

            return False

        tower_forward = (
            self.forward_value(
                tower_pos
            )
        )

        enemy_forward = (
            self.forward_value(
                enemy.pos
            )
        )

        if tower_forward < 0:
            return False

        if enemy_forward < 0:
            return False

        return (
            tower_forward
            <
            enemy_forward
        )

    # =====================================================
    # ATAQUE
    # =====================================================

    def start_attack_animation(self):

        self.attack_animation = (
            self.attack_animation_duration
        )

    def target_position(
        self,
        target
    ):

        if hasattr(
            target,
            "pos"
        ):

            return target.pos

        return target.rect.center

    def do_melee_attack(
        self,
        target,
        effects
    ):

        if hasattr(
            target,
            "hit"
        ):

            target.hit(
                self.damage
            )

        else:

            target.hp = max(
                0,
                target.hp
                - self.damage
            )

        target_pos = (
            self.target_position(
                target
            )
        )

        if self.unit_type == "guard":

            effects.append(
                ImpactEffect(
                    target_pos,
                    BLUE,
                    15,
                    0.16
                )
            )

        elif self.unit_type == "berserker":

            effects.append(
                ImpactEffect(
                    target_pos,
                    RED,
                    22,
                    0.18
                )
            )

        elif self.unit_type == "giant":

            effects.append(
                ImpactEffect(
                    target_pos,
                    ORANGE,
                    28,
                    0.23
                )
            )

        elif self.unit_type == "colossus":

            effects.append(
                ImpactEffect(
                    target_pos,
                    GOLD,
                    42,
                    0.32
                )
            )

        else:

            effects.append(
                ImpactEffect(
                    target_pos,
                    WHITE,
                    12,
                    0.14
                )
            )

    def shoot_projectile(
        self,
        target,
        projectiles
    ):

        if self.unit_type == "archer":

            projectiles.append(
                Projectile(
                    self.pos,
                    target,
                    self.damage,
                    PINK,
                    390,
                    "arrow"
                )
            )

        elif self.unit_type == "musketeer":

            projectiles.append(
                Projectile(
                    self.pos,
                    target,
                    self.damage,
                    GOLD,
                    520,
                    "musket"
                )
            )

        elif self.unit_type == "scout":

            projectiles.append(
                Projectile(
                    self.pos,
                    target,
                    self.damage,
                    CYAN,
                    470,
                    "bolt"
                )
            )

    def attack_unit(
        self,
        enemy,
        dt,
        projectiles,
        effects
    ):

        if enemy is None:
            return False

        if enemy.hp <= 0:

            self.unit_target = None
            return False

        distance = (
            self.pos.distance_to(
                enemy.pos
            )
        )

        if distance <= self.range:

            self.is_moving = False

            self.timer -= dt

            if self.timer <= 0:

                self.start_attack_animation()

                if self.ranged:

                    self.shoot_projectile(
                        enemy,
                        projectiles
                    )

                else:

                    self.do_melee_attack(
                        enemy,
                        effects
                    )

                self.timer = (
                    self.attack_interval
                )

            return True

        if (
            distance
            <=
            AGGRO_RANGE + 50
        ):

            self.move_towards_enemy(
                enemy,
                dt
            )

            return True

        self.unit_target = None

        return False

    def attack_locked_tower(
        self,
        dt,
        projectiles,
        effects
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

        distance = (
            self.pos.distance_to(
                tower_pos
            )
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

            if self.ranged:

                self.shoot_projectile(
                    tower,
                    projectiles
                )

            else:

                self.do_melee_attack(
                    tower,
                    effects
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
        projectiles,
        effects
    ):

        if self.hp <= 0:
            return

        self.update_bridge_status()

        self.animation_time += dt
        self.is_moving = False

        if self.attack_animation > 0:

            self.attack_animation -= dt

            if self.attack_animation < 0:
                self.attack_animation = 0

        if self.hp < self.last_hp:

            self.hit_flash = 0.12

        self.last_hp = self.hp

        if self.hit_flash > 0:

            self.hit_flash -= dt

        if self.locked_on_tower:

            if self.attack_locked_tower(
                dt,
                projectiles,
                effects
            ):

                return

        target_tower = (
            self.choose_target_tower(
                towers
            )
        )

        enemy = (
            self.find_enemy_unit(
                units
            )
        )

        if (
            target_tower is not None
            and
            enemy is not None
            and
            self.tower_blocks_enemy(
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

            if (
                distance_to_tower
                <=
                self.range
            ):

                self.locked_on_tower = True
                self.tower_target = target_tower
                self.unit_target = None

                self.attack_locked_tower(
                    dt,
                    projectiles,
                    effects
                )

                return

            enemy = None
            self.unit_target = None

        if enemy is not None:

            if self.attack_unit(
                enemy,
                dt,
                projectiles,
                effects
            ):

                return

        self.unit_target = None

        if not self.crossed_bridge:

            self.navigate_bridge(
                dt
            )

            return

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

        if (
            distance_to_tower
            >
            self.range
        ):

            self.move_towards(
                tower_pos,
                dt
            )

            return

        self.locked_on_tower = True
        self.tower_target = target_tower
        self.unit_target = None

        self.attack_locked_tower(
            dt,
            projectiles,
            effects
        )

    # =====================================================
    # SPRITE
    # =====================================================

    def get_sprite(self):

        sprites = {
            "knight": KNIGHT_IMG,
            "archer": ARCHER_IMG,
            "giant": GIANT_IMG,
            "guard": GUARD_IMG,
            "musketeer": MUSKETEER_IMG,
            "berserker": BERSERKER_IMG,
            "colossus": COLOSSUS_IMG,
            "scout": SCOUT_IMG
        }

        return sprites[
            self.unit_type
        ]

    # =====================================================
    # DRAW
    # =====================================================

    def draw(self):

        image = (
            self.get_sprite()
        )

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

            if (
                self.unit_type
                == "berserker"
            ):

                attack_offset *= 1.5
                rotation += 7

            elif (
                self.unit_type
                == "colossus"
            ):

                scale_factor = 1.12

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
            (
                20,
                20,
                20
            ),
            (
                int(
                    self.pos.x
                    - 22
                ),
                int(
                    self.pos.y
                    + 18
                ),
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

        team_color = (
            BLUE
            if self.team == "blue"
            else RED
        )

        pygame.draw.circle(
            screen,
            team_color,
            (
                int(self.pos.x),
                int(self.pos.y - 39)
            ),
            5
        )

        if self.unit_type in [
            "giant",
            "colossus"
        ]:

            bar_width = 58

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
            self.hp
            / self.max_hp
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
        self.effects = []

        # =================================================
        # TORRES
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
        # ELIXIR DO JOGADOR
        # =================================================

        self.elixir = 5.0
        self.max_elixir = 10.0

        self.normal_elixir_rate = 0.6

        self.elixir_rate = (
            self.normal_elixir_rate
        )

        # =================================================
        # ELIXIR DA IA
        # =================================================

        self.enemy_elixir = 5.0
        self.enemy_max_elixir = 10.0

        self.enemy_elixir_rate = (
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
        # DECK DO JOGADOR
        # =================================================

        self.deck = [
            "knight",
            "archer",
            "giant",
            "guard",
            "musketeer",
            "berserker",
            "colossus",
            "scout"
        ]

        random.shuffle(
            self.deck
        )

        self.hand = (
            self.deck[:4]
        )

        self.card_queue = (
            self.deck[4:]
        )

        self.selected_card = None

        # =================================================
        # DECK DA IA
        # =================================================

        self.enemy_deck = [
            "knight",
            "archer",
            "giant",
            "guard",
            "musketeer",
            "berserker",
            "colossus",
            "scout"
        ]

        random.shuffle(
            self.enemy_deck
        )

        self.enemy_hand = (
            self.enemy_deck[:4]
        )

        self.enemy_card_queue = (
            self.enemy_deck[4:]
        )

        # =================================================
        # TEMPO DE DECISÃO DA IA
        # =================================================

        self.ai_decision_timer = 1.5

        # =================================================
        # CARTAS
        # =================================================

        self.card_rects = []

        card_width = 150
        card_height = 78
        gap = 10

        total_width = (
            card_width * 4
            + gap * 3
        )

        start_x = (
            WIDTH
            - total_width
        ) // 2

        for i in range(4):

            self.card_rects.append(
                pygame.Rect(
                    start_x
                    + i
                    * (
                        card_width
                        + gap
                    ),
                    705,
                    card_width,
                    card_height
                )
            )

        # =================================================
        # ESTADO
        # =================================================

        self.game_over = False
        self.winner = None

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.__init__()

    # =====================================================
    # ROTAÇÃO DO JOGADOR
    # =====================================================

    def rotate_card(
        self,
        played_card
    ):

        if (
            played_card
            not in self.hand
        ):

            return

        index = self.hand.index(
            played_card
        )

        next_card = (
            self.card_queue.pop(0)
        )

        self.hand[index] = (
            next_card
        )

        self.card_queue.append(
            played_card
        )

    # =====================================================
    # ROTAÇÃO DA IA
    # =====================================================

    def rotate_enemy_card(
        self,
        played_card
    ):

        if (
            played_card
            not in self.enemy_hand
        ):

            return

        index = (
            self.enemy_hand.index(
                played_card
            )
        )

        next_card = (
            self.enemy_card_queue.pop(0)
        )

        self.enemy_hand[index] = (
            next_card
        )

        self.enemy_card_queue.append(
            played_card
        )

    # =====================================================
    # CARTAS QUE A IA PODE PAGAR
    # =====================================================

    def get_affordable_enemy_cards(self):

        affordable = []

        for card in self.enemy_hand:

            cost = (
                Unit.UNIT_DATA[
                    card
                ]["cost"]
            )

            if (
                cost
                <=
                self.enemy_elixir
            ):

                affordable.append(
                    card
                )

        return affordable

    # =====================================================
    # AMEAÇAS CONTRA A IA
    # =====================================================

    def get_enemy_threats(self):

        left_threats = []
        right_threats = []

        for unit in self.units:

            if unit.team != "blue":
                continue

            if unit.hp <= 0:
                continue

            # Só consideramos realmente perigosa
            # uma tropa que já está no lado vermelho
            # ou muito perto da ponte.
            if (
                unit.pos.y
                >
                ARENA.centery + 30
            ):

                continue

            if (
                unit.pos.x
                <
                ARENA.centerx
            ):

                left_threats.append(
                    unit
                )

            else:

                right_threats.append(
                    unit
                )

        return (
            left_threats,
            right_threats
        )

    # =====================================================
    # ESCOLHER DEFENSOR
    # =====================================================

    def choose_ai_defender(
        self,
        affordable
    ):

        priority = [
            "guard",
            "knight",
            "berserker",
            "musketeer",
            "archer",
            "scout"
        ]

        for card in priority:

            if card in affordable:
                return card

        if affordable:
            return random.choice(
                affordable
            )

        return None

    # =====================================================
    # ESCOLHER CARTA DE ATAQUE
    # =====================================================

    def choose_ai_attacker(
        self,
        affordable
    ):

        # Se tiver tanque disponível,
        # frequentemente inicia ataque com ele.
        tanks = [
            card
            for card
            in [
                "giant",
                "colossus"
            ]
            if card in affordable
        ]

        if (
            tanks
            and
            random.random() < 0.65
        ):

            return random.choice(
                tanks
            )

        # Suporte/pressão
        pressure_cards = [
            card
            for card
            in [
                "knight",
                "berserker",
                "musketeer",
                "archer",
                "scout",
                "guard"
            ]
            if card in affordable
        ]

        if pressure_cards:

            return random.choice(
                pressure_cards
            )

        if affordable:

            return random.choice(
                affordable
            )

        return None

    # =====================================================
    # JOGAR CARTA DA IA
    # =====================================================

    def enemy_play_card(
        self,
        card,
        lane,
        defensive=False
    ):

        if card is None:
            return False

        if card not in self.enemy_hand:
            return False

        cost = (
            Unit.UNIT_DATA[
                card
            ]["cost"]
        )

        if (
            self.enemy_elixir
            <
            cost
        ):

            return False

        # =================================================
        # POSIÇÃO
        # =================================================

        if lane == "left":

            x = random.randint(
                285,
                355
            )

        else:

            x = random.randint(
                695,
                765
            )

        if defensive:

            # Defende perto das princesas.
            y = random.randint(
                185,
                245
            )

        else:

            # Ataque começa mais atrás.
            y = random.randint(
                110,
                200
            )

        self.units.append(
            Unit(
                x,
                y,
                "red",
                card
            )
        )

        self.enemy_elixir -= (
            cost
        )

        self.rotate_enemy_card(
            card
        )

        return True

    # =====================================================
    # IA
    # =====================================================

    def update_ai(
        self,
        dt
    ):

        self.ai_decision_timer -= dt

        if self.ai_decision_timer > 0:
            return

        # A IA pensa novamente em aproximadamente
        # 0,8 a 1,6 segundos.
        self.ai_decision_timer = (
            random.uniform(
                0.8,
                1.6
            )
        )

        affordable = (
            self.get_affordable_enemy_cards()
        )

        if not affordable:
            return

        left_threats, right_threats = (
            self.get_enemy_threats()
        )

        # =================================================
        # DEFESA TEM PRIORIDADE
        # =================================================

        if (
            left_threats
            or
            right_threats
        ):

            # Decide qual lado parece mais perigoso.
            left_power = sum(
                unit.hp
                for unit
                in left_threats
            )

            right_power = sum(
                unit.hp
                for unit
                in right_threats
            )

            if left_power > right_power:

                lane = "left"

            elif right_power > left_power:

                lane = "right"

            else:

                lane = random.choice(
                    [
                        "left",
                        "right"
                    ]
                )

            card = (
                self.choose_ai_defender(
                    affordable
                )
            )

            if self.enemy_play_card(
                card,
                lane,
                defensive=True
            ):

                return

        # =================================================
        # ATAQUE
        # =================================================

        # A IA não precisa gastar imediatamente.
        # Às vezes acumula elixir.
        if (
            self.enemy_elixir < 4
            and
            random.random() < 0.75
        ):

            return

        card = (
            self.choose_ai_attacker(
                affordable
            )
        )

        if card is None:
            return

        # =================================================
        # ESCOLHA DE LANE
        # =================================================

        # Prefere atacar torre que esteja mais machucada.
        if (
            self.blue_left.is_alive()
            and
            self.blue_right.is_alive()
        ):

            left_ratio = (
                self.blue_left.hp
                /
                self.blue_left.max_hp
            )

            right_ratio = (
                self.blue_right.hp
                /
                self.blue_right.max_hp
            )

            # 65% de chance de pressionar
            # a torre mais fraca.
            if random.random() < 0.65:

                if (
                    left_ratio
                    <
                    right_ratio
                ):

                    lane = "left"

                elif (
                    right_ratio
                    <
                    left_ratio
                ):

                    lane = "right"

                else:

                    lane = random.choice(
                        [
                            "left",
                            "right"
                        ]
                    )

            else:

                lane = random.choice(
                    [
                        "left",
                        "right"
                    ]
                )

        elif self.blue_left.is_alive():

            lane = "left"

        elif self.blue_right.is_alive():

            lane = "right"

        else:

            lane = random.choice(
                [
                    "left",
                    "right"
                ]
            )

        self.enemy_play_card(
            card,
            lane,
            defensive=False
        )

    # =====================================================
    # SEPARAÇÃO
    # =====================================================

    def resolve_unit_separation(self):

        count = len(
            self.units
        )

        for i in range(count):

            a = self.units[i]

            if a.hp <= 0:
                continue

            for j in range(
                i + 1,
                count
            ):

                b = self.units[j]

                if b.hp <= 0:
                    continue

                if (
                    a.in_bridge_safe_zone()
                    or
                    b.in_bridge_safe_zone()
                ):

                    continue

                delta = (
                    b.pos
                    - a.pos
                )

                distance = (
                    delta.length()
                )

                minimum_distance = (
                    a.collision_radius
                    +
                    b.collision_radius
                ) * 0.80

                if (
                    distance
                    >=
                    minimum_distance
                ):

                    continue

                if distance < 0.001:

                    direction = pygame.Vector2(
                        1
                        if (i + j) % 2 == 0
                        else -1,
                        0
                    )

                else:

                    direction = (
                        delta.normalize()
                    )

                overlap = (
                    minimum_distance
                    - distance
                )

                push = (
                    direction
                    * overlap
                    * 0.30
                )

                a.pos -= push
                b.pos += push

    # =====================================================
    # SELEÇÃO
    # =====================================================

    def select_card_by_index(
        self,
        index
    ):

        if (
            index < 0
            or
            index >= len(
                self.hand
            )
        ):

            return

        card = self.hand[
            index
        ]

        if (
            self.selected_card
            == card
        ):

            self.selected_card = None

        else:

            self.selected_card = card

    def try_select_card(
        self,
        pos
    ):

        for i, rect in enumerate(
            self.card_rects
        ):

            if rect.collidepoint(
                pos
            ):

                self.select_card_by_index(
                    i
                )

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

        if (
            self.selected_card
            not in self.hand
        ):

            self.selected_card = None
            return

        if not ARENA.collidepoint(
            pos
        ):

            return

        if (
            pos[1]
            <=
            ARENA.centery
        ):

            return

        card = (
            self.selected_card
        )

        cost = (
            Unit.UNIT_DATA[
                card
            ]["cost"]
        )

        if self.elixir < cost:
            return

        self.units.append(
            Unit(
                pos[0],
                pos[1],
                "blue",
                card
            )
        )

        self.elixir -= cost

        self.rotate_card(
            card
        )

        self.selected_card = None

    # =====================================================
    # EVENTOS
    # =====================================================

    def handle_event(
        self,
        event
    ):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:

                self.reset()
                return

            if not self.game_over:

                if event.key == pygame.K_1:

                    self.select_card_by_index(
                        0
                    )

                elif event.key == pygame.K_2:

                    self.select_card_by_index(
                        1
                    )

                elif event.key == pygame.K_3:

                    self.select_card_by_index(
                        2
                    )

                elif event.key == pygame.K_4:

                    self.select_card_by_index(
                        3
                    )

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

            if (
                tower.tower_type
                == "princess"
            ):

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
    # FIM
    # =====================================================

    def finish_by_time(self):

        if (
            self.blue_crowns
            >
            self.red_crowns
        ):

            self.winner = "Você"

        elif (
            self.red_crowns
            >
            self.blue_crowns
        ):

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
        # ELIXIR DUPLO
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

            self.enemy_elixir_rate = (
                self.normal_elixir_rate
                * 2
            )

        # =================================================
        # ELIXIR DO JOGADOR
        # =================================================

        self.elixir = min(
            self.max_elixir,
            self.elixir
            + self.elixir_rate
            * dt
        )

        # =================================================
        # ELIXIR DA IA
        # =================================================

        self.enemy_elixir = min(
            self.enemy_max_elixir,
            self.enemy_elixir
            + self.enemy_elixir_rate
            * dt
        )

        # =================================================
        # IA
        # =================================================

        self.update_ai(
            dt
        )

        # =================================================
        # UNIDADES
        # =================================================

        for unit in self.units:

            unit.update(
                dt,
                self.units,
                self.towers,
                self.projectiles,
                self.effects
            )

        self.resolve_unit_separation()

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
                dt,
                self.effects
            )

        self.projectiles = [
            projectile
            for projectile
            in self.projectiles
            if projectile.alive
        ]

        # =================================================
        # EFEITOS
        # =================================================

        for effect in self.effects:

            effect.update(
                dt
            )

        self.effects = [
            effect
            for effect
            in self.effects
            if effect.alive
        ]

        # =================================================
        # MORTOS
        # =================================================

        self.units = [
            unit
            for unit
            in self.units
            if unit.hp > 0
        ]

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

            ARENA.centery
            - RIVER_HALF_HEIGHT,

            ARENA.width,

            RIVER_HALF_HEIGHT
            * 2
        )

        pygame.draw.rect(
            screen,
            RIVER,
            river
        )

        bridge_left = pygame.Rect(
            ARENA.x + 170,

            ARENA.centery
            - RIVER_HALF_HEIGHT,

            110,

            RIVER_HALF_HEIGHT
            * 2
        )

        bridge_right = pygame.Rect(
            ARENA.right - 280,

            ARENA.centery
            - RIVER_HALF_HEIGHT,

            110,

            RIVER_HALF_HEIGHT
            * 2
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
    # ÍCONES
    # =====================================================

    def get_card_icon(
        self,
        card
    ):

        sprites = {
            "knight": KNIGHT_IMG,
            "archer": ARCHER_IMG,
            "giant": GIANT_IMG,
            "guard": GUARD_IMG,
            "musketeer": MUSKETEER_IMG,
            "berserker": BERSERKER_IMG,
            "colossus": COLOSSUS_IMG,
            "scout": SCOUT_IMG
        }

        return sprites[
            card
        ]

    # =====================================================
    # CARTAS
    # =====================================================

    def draw_cards(self):

        for i, (
            rect,
            card
        ) in enumerate(
            zip(
                self.card_rects,
                self.hand
            )
        ):

            data = (
                Unit.UNIT_DATA[
                    card
                ]
            )

            selected = (
                self.selected_card
                == card
            )

            affordable = (
                self.elixir
                >=
                data["cost"]
            )

            if selected:

                color = PURPLE

            elif not affordable:

                color = (
                    65,
                    55,
                    70
                )

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

            pygame.draw.rect(
                screen,
                WHITE,
                rect,
                width=2,
                border_radius=10
            )

            number = SMALL.render(
                str(i + 1),
                True,
                WHITE
            )

            screen.blit(
                number,
                (
                    rect.x + 7,
                    rect.y + 4
                )
            )

            icon = (
                self.get_card_icon(
                    card
                )
            )

            icon_small = (
                pygame.transform.smoothscale(
                    icon,
                    (
                        48,
                        48
                    )
                )
            )

            screen.blit(
                icon_small,
                (
                    rect.x + 22,
                    rect.y + 22
                )
            )

            name = SMALL.render(
                data["name"],
                True,
                WHITE
            )

            screen.blit(
                name,
                (
                    rect.x + 73,
                    rect.y + 18
                )
            )

            pygame.draw.circle(
                screen,
                PURPLE,
                (
                    rect.right - 20,
                    rect.bottom - 18
                ),
                15
            )

            cost = SMALL.render(
                str(
                    data["cost"]
                ),
                True,
                WHITE
            )

            screen.blit(
                cost,
                cost.get_rect(
                    center=(
                        rect.right - 20,
                        rect.bottom - 18
                    )
                )
            )

    # =====================================================
    # PRÓXIMA CARTA
    # =====================================================

    def draw_next_card(self):

        if not self.card_queue:
            return

        next_card = (
            self.card_queue[0]
        )

        data = (
            Unit.UNIT_DATA[
                next_card
            ]
        )

        panel = pygame.Rect(
            900,
            700,
            170,
            83
        )

        pygame.draw.rect(
            screen,
            (
                55,
                55,
                65
            ),
            panel,
            border_radius=10
        )

        label = TINY.render(
            "PRÓXIMA",
            True,
            WHITE
        )

        screen.blit(
            label,
            (
                panel.x + 8,
                panel.y + 5
            )
        )

        icon = (
            self.get_card_icon(
                next_card
            )
        )

        icon = (
            pygame.transform.smoothscale(
                icon,
                (
                    42,
                    42
                )
            )
        )

        screen.blit(
            icon,
            (
                panel.x + 8,
                panel.y + 28
            )
        )

        name = TINY.render(
            data["name"],
            True,
            WHITE
        )

        screen.blit(
            name,
            (
                panel.x + 55,
                panel.y + 37
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

        player_elixir_text = (
            FONT.render(
                f"Elixir: {self.elixir:.1f}/10",
                True,
                WHITE
            )
        )

        screen.blit(
            player_elixir_text,
            (
                20,
                730
            )
        )

        # =================================================
        # ELIXIR DA IA
        # =================================================

        enemy_elixir_text = (
            SMALL.render(
                (
                    f"Elixir IA: "
                    f"{self.enemy_elixir:.1f}/10"
                ),
                True,
                RED
            )
        )

        screen.blit(
            enemy_elixir_text,
            (
                20,
                15
            )
        )

        blue_text = FONT.render(
            (
                f"Você "
                f"{self.blue_crowns} Coroas"
            ),
            True,
            BLUE
        )

        red_text = FONT.render(
            (
                f"{self.red_crowns} Coroas "
                f"Inimigo"
            ),
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
                (
                    0,
                    0
                )
            )

            result = (
                "Empate!"
                if self.winner == "Empate"
                else f"{self.winner} venceu!"
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

        for effect in self.effects:
            effect.draw()

        self.draw_cards()
        self.draw_next_card()
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

            if (
                event.type
                == pygame.QUIT
            ):

                running = False

            else:

                game.handle_event(
                    event
                )

        game.update(
            dt
        )

        game.draw()

    pygame.quit()


if __name__ == "__main__":

    main()