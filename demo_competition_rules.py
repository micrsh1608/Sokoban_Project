"""Deterministic engine demonstration, NOT an AI-controlled competitive match."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "source/task1"))
from sokoban.core.model import Action as A
from sokoban.core.parser import load_map
from sokoban.competitive.engine import CompetitionEngine


def main():
    actions = [(A.EAST, A.WAIT), (A.NORTH, A.EAST), (A.WEST, A.NORTH),
               (A.WAIT, A.WEST), (A.WAIT, A.NORTH), (A.WAIT, A.NORTH),
               (A.WAIT, A.EAST), (A.WAIT, A.SOUTH)]
    layout = load_map(ROOT / "maps/competitive/steal_demo.txt", competitive=True)
    engine = CompetitionEngine(layout, len(actions))
    state = engine.initial
    history = [state]
    print("RULE DEMO: scripted actions, not AI agents. Owner 0=Agent 1; 1=Agent 2.")
    for joint in actions:
        result = engine.resolve(state, joint)
        state = result.state
        history.append(state)
        print(f"Round {state.round_index}: {joint[0].value:5} / {joint[1].value:5}"
              f" | score={engine.scores(state)} | reasons={result.reasons}")
        print(f"  players={state.players} boxes={state.boxes}")
    winner = engine.winner(state)
    print("Winner:", "Draw" if winner is None else f"Agent {winner + 1}")
    print("Replay snapshots:", len(history))
    assert engine.scores(state) == (0, 1)
    assert winner == 1
    assert engine.scores(history[1]) == (1, 0)
    assert history[0] == engine.initial


if __name__ == "__main__":
    main()
