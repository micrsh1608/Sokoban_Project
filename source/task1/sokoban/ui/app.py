"""Dang: working single-player viewer/manual/replay shell; competition UI remains TODO."""
from concurrent.futures import ThreadPoolExecutor
import pygame
from ..core.history import History
from ..core.model import Action, Layout
from ..core.rules import is_goal, replay, step
from ..search.contracts import SearchLimits, Status, validate_result
from ..search.registry import SOLVERS


class App:
    def __init__(self, layout: Layout, limits: SearchLimits, algorithm: str):
        self.board = layout.board
        self.initial = layout.single_state()
        self.history = History((self.initial,))
        self.limits = limits
        self.algorithm = algorithm
        self.paused = True
        self.message = "Starter ready. WASD to play; Enter to call solver."
        self.future = None

    def run(self, smoke: bool = False):
        pygame.init()
        cell = min(64, max(12, 720 // max(self.board.width, self.board.height)))
        screen = pygame.display.set_mode((max(900, self.board.width * cell + 40),
                                          self.board.height * cell + 230))
        pygame.display.set_caption("Sokoban | Huy - Phuong - Dang | Starter")
        font = pygame.font.Font(None, 25)
        clock = pygame.time.Clock()
        pool = ThreadPoolExecutor(max_workers=1)
        running, last_tick = True, pygame.time.get_ticks()
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        key = event.key
                        if key == pygame.K_ESCAPE:
                            running = False
                        elif self.future is None:
                            if key == pygame.K_1: self.algorithm = "ucs"
                            elif key == pygame.K_2: self.algorithm = "astar"
                            elif key == pygame.K_SPACE: self.paused = not self.paused
                            elif key == pygame.K_RIGHT:
                                self.paused = True
                                self.history.forward()
                            elif key == pygame.K_LEFT:
                                self.paused = True
                                self.history.backward()
                            elif key == pygame.K_r:
                                self.history = History((self.initial,))
                                self.paused = True
                            elif key == pygame.K_RETURN:
                                self.paused = True
                                self.message = "Searching from initial state..."
                                self.future = pool.submit(SOLVERS[self.algorithm], self.board,
                                                          self.initial, self.limits)
                            else:
                                actions = {pygame.K_w: Action.NORTH, pygame.K_d: Action.EAST,
                                           pygame.K_a: Action.WEST, pygame.K_s: Action.SOUTH}
                                if key in actions:
                                    self.paused = True
                                    next_state = step(self.board, self.history.current, actions[key])
                                    if next_state is not None:
                                        self.history.append(next_state)
                if self.future is not None and self.future.done():
                    try:
                        result = self.future.result()
                        validate_result(self.board, self.initial, result)
                        self.message = f"{result.status.value}: {result.message}"
                        if result.status == Status.SOLVED:
                            self.history = History(replay(self.board, self.initial, result.actions))
                            self.message = f"Solved | actions={len(result.actions)} | cost={result.total_cost}"
                    except Exception as exc:
                        self.message = f"Solver error: {exc}"
                    finally:
                        self.future = None
                now = pygame.time.get_ticks()
                if not self.paused and now - last_tick >= 300:
                    self.history.forward()
                    last_tick = now
                self.draw(screen, font, cell)
                pygame.display.flip()
                clock.tick(30)
                if smoke:
                    running = False
        finally:
            # Single-player solver MUST check its own SearchLimits. This thread
            # is not a hard timeout sandbox and must not be used for competition.
            pool.shutdown(wait=False, cancel_futures=True)
            pygame.quit()

    def draw(self, screen, font, cell):
        screen.fill((237, 242, 247))
        state = self.history.current
        for r in range(self.board.height):
            for c in range(self.board.width):
                p = (r, c)
                rect = pygame.Rect(20 + c * cell, 20 + r * cell, cell - 2, cell - 2)
                if p in self.board.walls:
                    pygame.draw.rect(screen, (66, 80, 101), rect, border_radius=3)
                elif p in self.board.floors:
                    pygame.draw.rect(screen, (255, 255, 255), rect)
                    if p in self.board.goals:
                        pygame.draw.circle(screen, (224, 90, 80), rect.center, max(3, cell // 7))
                if p in state.boxes:
                    color = (51, 150, 114) if p in self.board.goals else (204, 143, 55)
                    pygame.draw.rect(screen, color, rect.inflate(-8, -8), border_radius=3)
                if p == state.player:
                    pygame.draw.circle(screen, (52, 113, 205), rect.center, max(4, cell // 3))
        lines = [f"Algorithm: {self.algorithm.upper()} | actions: {self.history.index}/{len(self.history.states)-1} | cost: {self.history.index}",
                 "1: UCS   2: A*   Enter: Solve from start   R: Reset   Esc: Quit",
                 "WASD: Manual   Space: Play/Pause   Right: Forward   Left: Back",
                 f"{'PAUSED' if self.paused else 'PLAYING'} | {'GOAL REACHED' if is_goal(self.board, state) else 'In progress'}",
                 self.message]
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, (30, 45, 65)), (20, 45 + self.board.height * cell + i * 30))
