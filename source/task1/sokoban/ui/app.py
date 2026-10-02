from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import pygame


@dataclass(frozen=True)
class DemoBoard:
    width: int
    height: int
    walls: frozenset[tuple[int, int]]
    floors: frozenset[tuple[int, int]]
    goals: frozenset[tuple[int, int]]


@dataclass(frozen=True)
class DemoState:
    player: tuple[int, int]
    boxes: frozenset[tuple[int, int]]


class DemoEngine:
    def __init__(self):
        self.board = self.create_board()
        self.initial = DemoState((1, 1), frozenset({(2, 2)}))
        self.actions = ["East", "South"]
        self.states = self.build_states()

    def create_board(self):
        rows = [
            "%%%%%%%",
            "%     %",
            "%     %",
            "%     %",
            "%%%%%%%"
        ]

        walls = set()
        floors = set()

        for r, row in enumerate(rows):
            for c, char in enumerate(row):
                if char == "%":
                    walls.add((r, c))
                else:
                    floors.add((r, c))

        return DemoBoard(
            width=len(rows[0]),
            height=len(rows),
            walls=frozenset(walls),
            floors=frozenset(floors),
            goals=frozenset({(3, 2)})
        )

    def step(self, state, action):
        directions = {
            "North": (-1, 0),
            "East": (0, 1),
            "West": (0, -1),
            "South": (1, 0)
        }

        dr, dc = directions[action]
        target = (state.player[0] + dr, state.player[1] + dc)

        if target not in self.board.floors:
            return state

        boxes = set(state.boxes)

        if target in boxes:
            destination = (target[0] + dr, target[1] + dc)

            if destination not in self.board.floors or destination in boxes:
                return state

            boxes.remove(target)
            boxes.add(destination)

        return DemoState(target, frozenset(boxes))

    def build_states(self):
        states = [self.initial]
        current = self.initial

        for action in self.actions:
            current = self.step(current, action)
            states.append(current)

        return states


class App:
    def __init__(self, layout=None, limits=None, algorithm="ucs"):
        self.demo = layout is None
        self.algorithm = algorithm
        self.limits = limits
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = None
        self.paused = True
        self.message = "Demo mode"
        self.current_index = 0

        if self.demo:
            engine = DemoEngine()
            self.board = engine.board
            self.initial = engine.initial
            self.states = list(engine.states)
            self.solution_actions = list(engine.actions)
            self.message = "Demo ready"
        else:
            self.board = layout.board
            self.initial = layout.single_state()
            self.states = [self.initial]
            self.solution_actions = []
            self.message = "Ready"

    @property
    def current_state(self):
        return self.states[self.current_index]

    def forward(self):
        if self.current_index < len(self.states) - 1:
            self.current_index += 1

    def backward(self):
        if self.current_index > 0:
            self.current_index -= 1

    def reset(self):
        self.current_index = 0
        self.paused = True
        self.message = "Reset"

    def is_goal(self, state):
        return state.boxes == self.board.goals

    def run(self):
        pygame.init()

        cell = min(
            80,
            max(
                40,
                700 // max(self.board.width, self.board.height)
            )
        )

        width = max(1000, self.board.width * cell + 40)
        height = self.board.height * cell + 250

        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sokoban - Dang GUI")

        font = pygame.font.Font(None, 28)
        title_font = pygame.font.Font(None, 38)
        clock = pygame.time.Clock()

        running = True
        last_update = pygame.time.get_ticks()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                        self.message = "Playing" if not self.paused else "Paused"

                    elif event.key == pygame.K_RIGHT:
                        self.paused = True
                        self.forward()

                    elif event.key == pygame.K_LEFT:
                        self.paused = True
                        self.backward()

                    elif event.key == pygame.K_r:
                        self.reset()

                    elif event.key == pygame.K_1:
                        self.algorithm = "ucs"
                        self.message = "Algorithm: UCS"

                    elif event.key == pygame.K_2:
                        self.algorithm = "astar"
                        self.message = "Algorithm: A*"

                    elif event.key == pygame.K_RETURN:
                        self.solve()

            if not self.paused:
                now = pygame.time.get_ticks()

                if now - last_update >= 500:
                    self.forward()
                    last_update = now

            self.draw(screen, font, title_font, cell)
            pygame.display.flip()
            clock.tick(60)

        self.executor.shutdown(wait=False, cancel_futures=True)
        pygame.quit()

    def solve(self):
        if self.demo:
            self.current_index = 0
            self.paused = False
            self.message = f"Demo solution | {len(self.solution_actions)} actions"
            return

        try:
            from ..search.registry import SOLVERS
            from ..search.contracts import validate_result

            self.paused = True
            self.message = f"Searching with {self.algorithm.upper()}..."

            solver = SOLVERS[self.algorithm]

            self.future = self.executor.submit(
                solver,
                self.board,
                self.initial,
                self.limits
            )

        except Exception as exc:
            self.message = f"Solver error: {exc}"

    def check_future(self):
        if self.future is None:
            return

        if not self.future.done():
            return

        try:
            from ..search.contracts import Status, validate_result
            from ..core.rules import replay

            result = self.future.result()

            validate_result(
                self.board,
                self.initial,
                result
            )

            self.message = (
                f"{result.status.value} | "
                f"actions={len(result.actions)} | "
                f"cost={result.total_cost}"
            )

            if result.status == Status.SOLVED:
                self.solution_actions = list(result.actions)
                self.states = list(
                    replay(
                        self.board,
                        self.initial,
                        result.actions
                    )
                )
                self.current_index = 0

        except Exception as exc:
            self.message = f"Solver error: {exc}"

        finally:
            self.future = None

    def draw(self, screen, font, title_font, cell):
        screen.fill((237, 242, 247))

        title = title_font.render(
            "SOKOBAN",
            True,
            (30, 45, 65)
        )

        screen.blit(title, (20, 15))

        state = self.current_state

        offset_x = 20
        offset_y = 70

        for r in range(self.board.height):
            for c in range(self.board.width):
                position = (r, c)

                rect = pygame.Rect(
                    offset_x + c * cell,
                    offset_y + r * cell,
                    cell - 2,
                    cell - 2
                )

                if position in self.board.walls:
                    pygame.draw.rect(
                        screen,
                        (66, 80, 101),
                        rect,
                        border_radius=4
                    )

                elif position in self.board.floors:
                    pygame.draw.rect(
                        screen,
                        (255, 255, 255),
                        rect
                    )

                    if position in self.board.goals:
                        pygame.draw.circle(
                            screen,
                            (220, 80, 80),
                            rect.center,
                            max(5, cell // 7)
                        )

                if position in state.boxes:
                    box_color = (
                        (51, 150, 114)
                        if position in self.board.goals
                        else (204, 143, 55)
                    )

                    pygame.draw.rect(
                        screen,
                        box_color,
                        rect.inflate(-12, -12),
                        border_radius=5
                    )

                if position == state.player:
                    pygame.draw.circle(
                        screen,
                        (52, 113, 205),
                        rect.center,
                        max(8, cell // 3)
                    )

        info_y = offset_y + self.board.height * cell + 20

        lines = [
            f"Algorithm: {self.algorithm.upper()}",
            f"Actions: {self.current_index}",
            f"Cost: {self.current_index}",
            f"Status: {'GOAL REACHED' if self.is_goal(state) else 'IN PROGRESS'}",
            self.message,
            "1: UCS    2: A*    Enter: Solve    R: Reset    Esc: Quit",
            "Space: Play/Pause    Right: Forward    Left: Back"
        ]

        for index, line in enumerate(lines):
            surface = font.render(
                line,
                True,
                (30, 45, 65)
            )

            screen.blit(
                surface,
                (20, info_y + index * 30)
            )


if __name__ == "__main__":
    App().run()