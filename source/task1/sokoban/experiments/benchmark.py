"""Dang: separate timing and Python-memory runs to avoid tracing bias in timing."""
import csv
from dataclasses import asdict
import platform
from pathlib import Path
from time import perf_counter
import tracemalloc
from ..search.registry import SOLVERS
from ..search.contracts import Status, validate_result


def benchmark(layout, limits, repeats: int, output: Path, map_name: str):
    rows = []
    for repetition in range(repeats):
        algorithms = list(SOLVERS.items())
        if repetition % 2:
            algorithms.reverse()
        for algorithm, solve in algorithms:
            initial = layout.single_state()
            start = perf_counter()
            result = solve(layout.board, initial, limits)
            elapsed_ms = (perf_counter() - start) * 1000
            validate_result(layout.board, initial, result)
            if result.status == Status.NOT_IMPLEMENTED:
                raise NotImplementedError(f"{algorithm}: no benchmark CSV written for a missing algorithm.")
            tracemalloc.start()
            try:
                memory_result = solve(layout.board, initial, limits)
                peak_bytes = tracemalloc.get_traced_memory()[1]
            finally:
                tracemalloc.stop()
            validate_result(layout.board, initial, memory_result)
            rows.append({"map": map_name, "algorithm": algorithm, "repeat": repetition + 1,
                         "status": result.status.value, "actions": len(result.actions) if result.status == Status.SOLVED else "",
                         "total_cost": result.total_cost, "elapsed_ms": elapsed_ms,
                         "python_peak_bytes": peak_bytes, "memory_run_status": memory_result.status.value,
                         "memory_run_cost": memory_result.total_cost,
                         "limit_seconds": limits.seconds, "max_expanded_limit": limits.max_expanded,
                         "python": platform.python_version(), "platform": platform.platform(),
                         **asdict(result.metrics)})
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Written {len(rows)} real runs to {output}")
