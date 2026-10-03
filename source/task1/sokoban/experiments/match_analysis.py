"""Summarize the JSON turn logs written by the competition runner."""
from collections import Counter
import json
from pathlib import Path
from statistics import mean, median


def analyze_match_data(data, source=""):
    turns = data.get("turns")
    controllers = data.get("controllers")
    if not isinstance(turns, list) or not isinstance(controllers, list) or len(controllers) != 2:
        raise ValueError("Match log must contain a turns list and exactly two controllers")

    agents = []
    for agent_id in range(2):
        decisions = []
        for turn in turns:
            choices = turn.get("decisions")
            if not isinstance(choices, list) or len(choices) != 2:
                raise ValueError("Each turn must contain exactly two decisions")
            decisions.append(choices[agent_id])
        elapsed = [float(item["elapsed_ms"]) for item in decisions]
        agents.append({
            "agent": agent_id + 1,
            "controller": controllers[agent_id],
            "status_counts": dict(sorted(Counter(item["status"] for item in decisions).items())),
            "action_counts": dict(sorted(Counter(item["action"] for item in decisions).items())),
            "mean_response_ms": mean(elapsed) if elapsed else 0.0,
            "median_response_ms": median(elapsed) if elapsed else 0.0,
            "max_response_ms": max(elapsed, default=0.0),
            "timeouts": sum(item["status"] == "timeout" for item in decisions),
            "errors": sum(item["status"] in ("error", "invalid_action") for item in decisions),
            "over_budget_responses": sum(
                value > float(data.get("decision_ms", 1000)) for value in elapsed
            ),
        })

    conflict_reasons = {"conflict_same_box", "conflict_destination"}
    blocked_reasons = {"blocked_wall_or_void", "blocked_player", "blocked_box_wall_or_void",
                       "blocked_box_player", "blocked_box_box"}
    conflict_turns = 0
    blocked_actions = [0, 0]
    ownership_gains = [0, 0]
    ownership_losses = [0, 0]
    round_scores = []
    for turn in turns:
        reasons = turn.get("reasons", [])
        conflict_turns += bool(conflict_reasons.intersection(reasons))
        for agent_id, reason in enumerate(reasons):
            blocked_actions[agent_id] += reason in blocked_reasons
        round_scores.append({"round": turn.get("round_index"), "scores": turn.get("scores")})
        before_boxes = {
            item["id"]: item.get("owner")
            for item in turn.get("before", {}).get("boxes", [])
        }
        after_boxes = {
            item["id"]: item.get("owner")
            for item in turn.get("after", {}).get("boxes", [])
        }
        for box_id, old_owner in before_boxes.items():
            new_owner = after_boxes.get(box_id)
            if old_owner != new_owner:
                if old_owner in (0, 1):
                    ownership_losses[old_owner] += 1
                if new_owner in (0, 1):
                    ownership_gains[new_owner] += 1

    return {
        "source": source,
        "controllers": controllers,
        "rounds_requested": data.get("initial", {}).get("max_rounds"),
        "rounds_played": len(turns),
        "decision_limit_ms": data.get("decision_ms", 1000),
        "scores": data.get("scores", [0, 0]),
        "winner": data.get("winner"),
        "draw": data.get("winner") is None and len(turns) > 0,
        "agents": agents,
        "conflict_rounds": conflict_turns,
        "blocked_actions": blocked_actions,
        "ownership_gains": ownership_gains,
        "ownership_losses": ownership_losses,
        "round_scores": round_scores,
    }


def analyze_match_file(input_path, output_path=None):
    input_path = Path(input_path)
    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read match log {input_path}: {exc}") from exc
    analysis = analyze_match_data(data, source=str(input_path))
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    return analysis
