import argparse
import json
from dataclasses import asdict
from pathlib import Path
from .core.parser import load_map
from .search.contracts import SearchLimits, Status, validate_result
from .search.registry import SOLVERS


def main(root: Path) -> int:
    parser = argparse.ArgumentParser(description="Sokoban team starter - not the final submission")
    parser.add_argument("--mode", choices=("gui", "validate", "solve", "benchmark", "verify",
                                             "compete", "competitive-gui", "analyze-match"), default="gui")
    parser.add_argument("--map", type=Path, default=root / "maps/single/tiny.txt")
    parser.add_argument("--maps", type=Path, nargs="+", default=None,
                        help="One or more maps for a combined benchmark sweep")
    parser.add_argument("--algorithm", choices=tuple(SOLVERS), default="ucs")
    parser.add_argument("--seconds", type=float, default=10.0)
    parser.add_argument("--max-expanded", type=int, default=100_000)
    parser.add_argument("--rounds", type=int, default=50)
    parser.add_argument("--agent-two", choices=("wait", "agent-one", "agent-two"), default="wait",
                        help="opponent: wait baseline, AgentOne, or Phuong's AgentTwo controller")
    parser.add_argument("--match-output", type=Path, default=root / "results/match.json")
    parser.add_argument("--match-input", type=Path, default=root / "results/match.json")
    parser.add_argument("--analysis-output", type=Path, default=root / "results/match_analysis.json")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, default=root / "results/benchmark.csv")
    parser.add_argument("--verify-states", type=int, default=72,
                        help="Maximum number of reachable states used by heuristic verification")
    parser.add_argument("--competitive-map", action="store_true", help="Use A/P map convention for validation")
    parser.add_argument("--smoke", action="store_true", help="Render one GUI frame and exit (headless checks)")
    args = parser.parse_args()
    try:
        limits = SearchLimits(args.seconds, args.max_expanded)
        if args.rounds <= 0 or args.repeats <= 0:
            raise ValueError("rounds and repeats must be positive")
        if args.mode == "analyze-match":
            from .experiments.match_analysis import analyze_match_file
            analysis = analyze_match_file(args.match_input, args.analysis_output)
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
            print("Analysis:", args.analysis_output)
            return 0

        competitive = args.mode in ("compete", "competitive-gui") or args.competitive_map
        layout = load_map(args.map, competitive)
        if args.mode == "validate":
            print(json.dumps({"valid": True, "players": len(layout.players),
                              "boxes": len(layout.boxes), "goals": len(layout.board.goals)}, indent=2))
            return 0
        if args.mode == "competitive-gui":
            from .ui.competitive import CompetitiveApp
            CompetitiveApp(layout, args.rounds, args.agent_two,
                           match_output=args.match_output).run(smoke=args.smoke)
            return 0
        if args.mode == "compete":
            from .competitive.engine import CompetitionEngine
            from .competitive.runner import run_match, AGENT_ONE, AGENT_TWO, WAIT_AGENT
            second = {"wait": WAIT_AGENT, "agent-one": AGENT_ONE,
                      "agent-two": AGENT_TWO}[args.agent_two]
            labels = {"wait": "WAIT BASELINE (testing only)",
                      "agent-one": "AgentOne", "agent-two": "AgentTwo"}
            print("Agent 1: bounded BFS | Agent 2:",
                  labels[args.agent_two])
            def show_turn(record):
                print(f"Round {record.round_index}: "
                      f"{[d.action.value for d in record.decisions]} "
                      f"scores={record.scores} status={[d.status for d in record.decisions]}")
            result = run_match(CompetitionEngine(layout, args.rounds),
                               (AGENT_ONE, second), on_turn=show_turn)
            result.save(args.match_output)
            print("Winner:", "Draw" if result.winner is None else f"Agent {result.winner + 1}")
            print("Match log:", args.match_output)
            return 0
        state = layout.single_state()
        if args.mode == "solve":
            result = SOLVERS[args.algorithm](layout.board, state, limits)
            validate_result(layout.board, state, result)
            print(json.dumps(asdict(result), indent=2))
            return 0 if result.status == Status.SOLVED else 2
        if args.mode == "benchmark":
            from .experiments.benchmark import benchmark_suite
            paths = args.maps if args.maps else [args.map]
            benchmark_layouts = []
            for path in paths:
                benchmark_layouts.append((path.as_posix(), load_map(path)))
            benchmark_suite(benchmark_layouts, limits, args.repeats, args.output)
            return 0
        if args.mode == "verify":
            from .experiments.verify_heuristic import verify_map
            from .search.heuristics import Heuristic
            if args.verify_states <= 0:
                raise ValueError("verify-states must be positive")
            report = verify_map(
                layout.board, state, Heuristic(layout.board),
                max_states=args.verify_states,
                oracle_limits=SearchLimits(seconds=args.seconds,
                                            max_expanded=args.max_expanded),
            )
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if not report["violations"] else 2
        from .ui.app import App
        App(layout, limits, args.algorithm).run(smoke=args.smoke)
        return 0
    except (ValueError, OSError, NotImplementedError, RuntimeError) as exc:
        print(f"{type(exc).__name__}: {exc}")
        return 2
    except ModuleNotFoundError as exc:
        if exc.name != "pygame":
            raise
        print("pygame is missing. Run: python -m pip install -r requirements.txt")
        return 2
