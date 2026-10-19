import pygame
import random

pygame.init()

WIDTH, HEIGHT = 1100, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Royale - Python")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 22)
SMALL = pygame.font.SysFont("arial", 16)
BIG = pygame.font.SysFont("arial", 34, bold=True)

FPS = 60

ARENA = pygame.Rect(120, 40, 860, 620)

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
BROWN = (205, 140, 75)


# ------------------------------------------------
# TORRE
# ------------------------------------------------

class Tower:
    def __init__(self, x, y, team, tower_type, lane=None):

        self.rect = pygame.Rect(x, y, 75, 75)

        self.team = team
        self.tower_type = tower_type
        self.lane = lane

        if tower_type == "king":
            self.hp = 1200
        else:
            self.hp = 800

        self.max_hp = self.hp

    def hit(self, damage):

        self.hp = max(
            0,
            self.hp - damage
        )

    def is_alive(self):

        return self.hp > 0

    def draw(self):

        if not self.is_alive():
            return

        color = (
            BLUE
            if self.team == "blue"
            else RED
        )

        pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=10
        )

        if self.tower_type == "king":

            pygame.draw.circle(
                screen,
                GOLD,
                self.rect.center,
                12
            )

        bar = pygame.Rect(
            self.rect.x,
            self.rect.y - 12,
            self.rect.width,
            7
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


# ------------------------------------------------
# UNIDADES
# ------------------------------------------------

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
            "color": GOLD,
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
            "color": PINK,
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
            "color": BROWN,
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

        self.hp = data["hp"]
        self.max_hp = data["hp"]

        self.damage = data["damage"]
        self.speed = data["speed"]
        self.range = data["range"]

        self.attack_interval = data[
            "attack_interval"
        ]

        self.color = data["color"]

        self.targets_units = data[
            "targets_units"
        ]

        self.timer = 0

        # regra que já adicionamos antes
        self.locked_on_tower = False

        if unit_type == "giant":
            self.radius = 24
        else:
            self.radius = 18

        # Define a lane pela posição
        if x < ARENA.centerx:
            self.lane = "left"
        else:
            self.lane = "right"

        # Pontes
        self.left_bridge = pygame.Vector2(
            ARENA.x + 220,
            ARENA.centery
        )

        self.right_bridge = pygame.Vector2(
            ARENA.right - 220,
            ARENA.centery
        )

        if self.lane == "left":

            self.bridge_target = (
                self.left_bridge
            )

        else:

            self.bridge_target = (
                self.right_bridge
            )

        self.crossed_bridge = False


    # ------------------------------------------------
    # MOVIMENTO
    # ------------------------------------------------

    def move_towards(
        self,
        target,
        dt
    ):

        delta = (
            target
            - self.pos
        )

        if delta.length() > 0:

            self.pos += (
                delta.normalize()
                * self.speed
                * dt
            )


    # ------------------------------------------------
    # ENCONTRAR INIMIGO
    # ------------------------------------------------

    def find_enemy_unit(
        self,
        units
    ):

        if not self.targets_units:
            return None

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

            if distance < closest_distance:

                closest_distance = distance
                closest = other

        return closest


    # ------------------------------------------------
    # ATAQUE EM UNIDADE
    # ------------------------------------------------

    def attack_unit(
        self,
        enemy,
        dt
    ):

        distance = (
            self.pos.distance_to(
                enemy.pos
            )
        )

        if distance <= self.range:

            self.timer -= dt

            if self.timer <= 0:

                enemy.hp -= self.damage

                self.timer = (
                    self.attack_interval
                )

            return True

        if distance < 180:

            self.move_towards(
                enemy.pos,
                dt
            )

            return True

        return False


    # ------------------------------------------------
    # ESCOLHER TORRE
    # ------------------------------------------------

    def choose_target_tower(
        self,
        towers
    ):

        # primeiro tenta torre da lane
        for tower in towers:

            if (
                tower.team != self.team
                and tower.lane == self.lane
                and tower.tower_type == "princess"
                and tower.is_alive()
            ):

                return tower

        # se lateral morreu,
        # vai para torre do rei
        for tower in towers:

            if (
                tower.team != self.team
                and tower.tower_type == "king"
                and tower.is_alive()
            ):

                return tower

        return None


    # ------------------------------------------------
    # UPDATE
    # ------------------------------------------------

    def update(
        self,
        dt,
        units,
        towers
    ):

        if self.hp <= 0:
            return

        target_tower = (
            self.choose_target_tower(
                towers
            )
        )

        if target_tower is None:
            return

        tower_target = pygame.Vector2(
            target_tower.rect.center
        )

        distance_to_tower = (
            self.pos.distance_to(
                tower_target
            )
        )

        # --------------------------------------------
        # SE JÁ ESTÁ BATENDO NA TORRE
        # NÃO MUDA DE ALVO
        # --------------------------------------------

        if self.locked_on_tower:

            if (
                not target_tower.is_alive()
            ):

                self.locked_on_tower = False
                return

            if (
                distance_to_tower
                > self.range
            ):

                self.move_towards(
                    tower_target,
                    dt
                )

            else:

                self.timer -= dt

                if self.timer <= 0:

                    target_tower.hit(
                        self.damage
                    )

                    self.timer = (
                        self.attack_interval
                    )

            return


        # --------------------------------------------
        # PROCURAR TROPA INIMIGA
        # --------------------------------------------

        enemy = self.find_enemy_unit(
            units
        )

        if enemy is not None:

            attacked = (
                self.attack_unit(
                    enemy,
                    dt
                )
            )

            if attacked:
                return


        # --------------------------------------------
        # IR PARA PONTE
        # --------------------------------------------

        if not self.crossed_bridge:

            distance = (
                self.pos.distance_to(
                    self.bridge_target
                )
            )

            if distance > 8:

                self.move_towards(
                    self.bridge_target,
                    dt
                )

                return

            self.crossed_bridge = True


        # --------------------------------------------
        # IR PARA TORRE
        # --------------------------------------------

        distance_to_tower = (
            self.pos.distance_to(
                tower_target
            )
        )

        if (
            distance_to_tower
            > self.range
        ):

            self.move_towards(
                tower_target,
                dt
            )

        else:

            self.locked_on_tower = True

            self.timer -= dt

            if self.timer <= 0:

                target_tower.hit(
                    self.damage
                )

                self.timer = (
                    self.attack_interval
                )


    # ------------------------------------------------
    # DESENHO
    # ------------------------------------------------

    def draw(self):

        if self.team == "blue":

            color = self.color

        else:

            color = RED

        pygame.draw.circle(
            screen,
            color,
            (
                int(self.pos.x),
                int(self.pos.y)
            ),
            self.radius
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (
                int(self.pos.x),
                int(self.pos.y)
            ),
            self.radius,
            2
        )

        bar_width = (
            50
            if self.unit_type == "giant"
            else 40
        )

        x = int(
            self.pos.x
            - bar_width / 2
        )

        y = int(
            self.pos.y
            - self.radius
            - 12
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


# ------------------------------------------------
# GAME
# ------------------------------------------------

class Game:

    def __init__(self):

        self.units = []

        # --------------------------------------------
        # TORRES AZUIS
        # --------------------------------------------

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


        # --------------------------------------------
        # TORRES VERMELHAS
        # --------------------------------------------

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


        # --------------------------------------------
        # ELIXIR
        # --------------------------------------------

        self.elixir = 5.0
        self.max_elixir = 10.0

        self.elixir_rate = 0.6


        # --------------------------------------------
        # CARTAS
        # --------------------------------------------

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


        # --------------------------------------------
        # IA
        # --------------------------------------------

        self.enemy_spawn_timer = 2.5


        # --------------------------------------------
        # ESTADO
        # --------------------------------------------

        self.game_over = False
        self.winner = None


    # ------------------------------------------------
    # RESET
    # ------------------------------------------------

    def reset(self):

        self.__init__()


    # ------------------------------------------------
    # SELECIONAR CARTA
    # ------------------------------------------------

    def try_select_card(
        self,
        pos
    ):

        for rect, card_type in zip(
            self.card_rects,
            self.card_types
        ):

            if rect.collidepoint(pos):

                if (
                    self.selected_card
                    == card_type
                ):

                    self.selected_card = None

                else:

                    self.selected_card = (
                        card_type
                    )

                return True

        return False


    # ------------------------------------------------
    # CRIAR TROPA DO JOGADOR
    # ------------------------------------------------

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

        if (
            pos[1]
            <= ARENA.centery
        ):
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


    # ------------------------------------------------
    # CRIAR TROPA DA IA
    # ------------------------------------------------

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


    # ------------------------------------------------
    # EVENTOS
    # ------------------------------------------------

    def handle_event(
        self,
        event
    ):

        if (
            event.type
            == pygame.KEYDOWN
            and event.key
            == pygame.K_r
        ):

            self.reset()
            return

        if self.game_over:
            return

        if (
            event.type
            == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            if self.try_select_card(
                event.pos
            ):
                return

            self.spawn_player_unit(
                event.pos
            )


    # ------------------------------------------------
    # UPDATE
    # ------------------------------------------------

    def update(
        self,
        dt
    ):

        if self.game_over:
            return


        # ELIXIR
        self.elixir = min(

            self.max_elixir,

            self.elixir
            + self.elixir_rate
            * dt

        )


        # IA
        self.enemy_spawn_timer -= dt

        if (
            self.enemy_spawn_timer
            <= 0
        ):

            self.spawn_enemy_unit()

            self.enemy_spawn_timer = (
                random.uniform(
                    3.0,
                    5.0
                )
            )


        # UNIDADES
        for unit in self.units:

            unit.update(

                dt,
                self.units,
                self.towers

            )


        # REMOVE MORTOS
        self.units = [

            unit

            for unit in self.units

            if unit.hp > 0

        ]


        # --------------------------------------------
        # VITÓRIA
        # --------------------------------------------

        if (
            not self.red_king.is_alive()
        ):

            self.game_over = True
            self.winner = "Você"


        elif (
            not self.blue_king.is_alive()
        ):

            self.game_over = True
            self.winner = "Inimigo"


    # ------------------------------------------------
    # ARENA
    # ------------------------------------------------

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


    # ------------------------------------------------
    # CARTAS
    # ------------------------------------------------

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


            color = (

                PURPLE

                if selected

                else (
                    85,
                    60,
                    110
                )

            )


            pygame.draw.rect(

                screen,

                color,

                rect,

                border_radius=10

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

                name.get_rect(

                    center=(

                        rect.centerx,

                        rect.centery - 10

                    )

                )

            )


            screen.blit(

                cost,

                cost.get_rect(

                    center=(

                        rect.centerx,

                        rect.centery + 13

                    )

                )

            )


    # ------------------------------------------------
    # INTERFACE
    # ------------------------------------------------

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
                    150
                )

            )


            screen.blit(

                overlay,

                (0, 0)

            )


            victory = BIG.render(

                f"{self.winner} venceu!",

                True,

                WHITE

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

                        HEIGHT // 2 - 20

                    )

                )

            )


            screen.blit(

                restart,

                restart.get_rect(

                    center=(

                        WIDTH // 2,

                        HEIGHT // 2 + 25

                    )

                )

            )


    # ------------------------------------------------
    # DRAW
    # ------------------------------------------------

    def draw(self):

        self.draw_arena()


        for tower in self.towers:

            tower.draw()


        for unit in self.units:

            unit.draw()


        self.draw_cards()

        self.draw_ui()


        pygame.display.flip()


# ------------------------------------------------
# MAIN
# ------------------------------------------------

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