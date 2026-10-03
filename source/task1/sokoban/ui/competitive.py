from threading import Event, Thread
from queue import Queue, Empty
import pygame

from ..competitive.engine import CompetitionEngine
from ..competitive.runner import run_match, AGENT_ONE, AGENT_TWO, WAIT_AGENT, MatchCancelled


class CompetitiveApp:
    OPPONENTS = ("wait", "agent-one", "agent-two")

    def __init__(self, layout, rounds=50, agent_two="wait", match_output=None):
        self.layout = layout
        self.rounds = rounds
        self.round_text = str(rounds)
        self.round_editing = False
        self.agent_two = agent_two
        if self.agent_two not in self.OPPONENTS:
            self.agent_two = "wait"
        self.match_output = match_output
        self.decision_ms = 1000

        self.board = layout.board
        self.engine = CompetitionEngine(layout, rounds)

        self.snapshots = [self.engine.initial]
        self.scores = [(0, 0)]
        self.reasons = [("", "")]
        self.current_index = 0

        self.queue = Queue()
        self.cancel_event = Event()
        self.worker = None
        self.running_match = False
        self.finished = False
        self.paused = True
        self.message = "Press Enter to start match."

    @property
    def current_state(self):
        return self.snapshots[self.current_index]

    def start_match(self):
        if self.running_match:
            return

        try:
            rounds = int(self.round_text)
            if rounds <= 0:
                raise ValueError
            self.engine = CompetitionEngine(self.layout, rounds)
        except ValueError:
            self.message = "Rounds n must be a positive whole number."
            return
        self.rounds = rounds
        self.snapshots = [self.engine.initial]
        self.scores = [(0, 0)]
        self.reasons = [("", "")]
        self.current_index = 0
        self.finished = False
        self.paused = False
        self.running_match = True
        self.round_editing = False
        self.message = "Match running..."
        self.queue = Queue()
        self.cancel_event = Event()
        second = {"wait": WAIT_AGENT, "agent-one": AGENT_ONE,
                  "agent-two": AGENT_TWO}[self.agent_two]

        self.worker = Thread(
            target=self._run_match,
            args=(second, self.cancel_event),
            daemon=True
        )
        self.worker.start()

    def _run_match(self, second, cancel_event):
        try:
            def on_turn(record):
                self.queue.put(("turn", record))

            result = run_match(
                self.engine,
                (AGENT_ONE, second),
                self.decision_ms,
                on_turn=on_turn,
                cancel_event=cancel_event,
            )
            if self.match_output is not None:
                result.save(self.match_output)
            self.queue.put(("done", result))

        except MatchCancelled:
            self.queue.put(("cancelled", None))
        except Exception as exc:
            self.queue.put(("error", str(exc)))

    def process_queue(self):
        while True:
            try:
                event, data = self.queue.get_nowait()
            except Empty:
                break

            if event == "turn":
                record = data

                self.snapshots.append(record.after)
                self.scores.append(record.scores)
                self.reasons.append(record.reasons)

                if not self.paused:
                    self.current_index = len(self.snapshots) - 1

            elif event == "done":
                result = data
                self.running_match = False
                self.finished = True

                if result.winner is None:
                    self.message = "Match finished: DRAW"
                else:
                    self.message = f"Match finished: Agent {result.winner + 1} wins"

                self.current_index = len(self.snapshots) - 1

            elif event == "error":
                self.running_match = False
                self.finished = True
                self.message = f"Match error: {data}"

            elif event == "cancelled":
                self.running_match = False
                self.finished = True
                self.message = "Match cancelled."

    def forward(self):
        if self.current_index < len(self.snapshots) - 1:
            self.current_index += 1

    def backward(self):
        if self.current_index > 0:
            self.current_index -= 1

    def reset_view(self):
        if self.running_match:
            return

        self.current_index = 0
        self.paused = True
        self.message = "Press Enter to start match."

    def run(self, smoke=False):
        pygame.init()

        cell = min(
            72,
            max(
                32,
                720 // max(self.board.width, self.board.height)
            )
        )

        width = max(1050, self.board.width * cell + 40)
        height = self.board.height * cell + 280

        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sokoban | Competitive")

        title_font = pygame.font.Font(None, 38)
        font = pygame.font.Font(None, 26)
        small_font = pygame.font.Font(None, 23)

        clock = pygame.time.Clock()
        running = True

        last_step = pygame.time.get_ticks()

        while running:
            self.process_queue()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_RETURN:
                        self.start_match()

                    elif event.key == pygame.K_t and not self.running_match:
                        self.agent_two = self.OPPONENTS[
                            (self.OPPONENTS.index(self.agent_two) + 1) % len(self.OPPONENTS)
                        ]

                    elif event.key == pygame.K_BACKSPACE and not self.running_match:
                        self.round_text = self.round_text[:-1]
                        self.round_editing = True

                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused

                    elif event.key == pygame.K_RIGHT:
                        self.paused = True
                        self.forward()

                    elif event.key == pygame.K_LEFT:
                        self.paused = True
                        self.backward()

                    elif event.key == pygame.K_r:
                        self.reset_view()

                    elif not self.running_match and event.unicode in "0123456789":
                        if not self.round_editing:
                            self.round_text = ""
                            self.round_editing = True
                        self.round_text = (self.round_text + event.unicode)[:8]

            now = pygame.time.get_ticks()

            if not self.paused and now - last_step >= 400:
                if self.current_index < len(self.snapshots) - 1:
                    self.current_index += 1
                last_step = now

            self.draw(
                screen,
                title_font,
                font,
                small_font,
                cell
            )

            pygame.display.flip()
            clock.tick(60)

            if smoke:
                running = False

        self.cancel_event.set()
        pygame.quit()

    def draw(self, screen, title_font, font, small_font, cell):
        screen.fill((237, 242, 247))

        screen.blit(
            title_font.render(
                "SOKOBAN COMPETITIVE",
                True,
                (30, 45, 65)
            ),
            (20, 15)
        )

        state = self.current_state

        offset_x = 20
        offset_y = 65

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

                for box in state.boxes:
                    if box.position == position:
                        if box.owner == 0:
                            color = (52, 113, 205)
                        elif box.owner == 1:
                            color = (220, 120, 60)
                        else:
                            color = (145, 145, 145)

                        pygame.draw.rect(
                            screen,
                            color,
                            rect.inflate(-12, -12),
                            border_radius=5
                        )

                for agent_id, player in enumerate(state.players):
                    if player == position:
                        player_color = (
                            (40, 90, 210)
                            if agent_id == 0
                            else (220, 110, 50)
                        )

                        pygame.draw.circle(
                            screen,
                            player_color,
                            rect.center,
                            max(8, cell // 3)
                        )

        info_x = 20
        info_y = offset_y + self.board.height * cell + 20

        score = self.scores[self.current_index]
        reasons = self.reasons[self.current_index]

        round_number = min(
            self.current_index,
            self.rounds
        )

        lines = [
            f"Rounds n: {self.round_text} | Round: {round_number} / {self.rounds}",
            f"Score: Agent 1 = {score[0]} | Agent 2 = {score[1]}",
            f"Agent 1: BLUE     Agent 2: ORANGE",
            f"Controller 2: {self.agent_two}",
            f"Status: {'RUNNING' if self.running_match else 'FINISHED' if self.finished else 'READY'}",
            self.message,
            f"Last result: {reasons[0]} | {reasons[1]}",
            "Type n + Enter: Start    T: Opponent    Space: Pause/Play    Right: Next    Left: Back    R: Reset    Esc: Quit"
        ]

        for index, line in enumerate(lines):
            rendered = small_font.render(
                line,
                True,
                (30, 45, 65)
            )

            screen.blit(
                rendered,
                (info_x, info_y + index * 27)
            )
