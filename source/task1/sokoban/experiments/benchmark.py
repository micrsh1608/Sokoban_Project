"""Repeatable UCS/A* measurements with raw runs and an aggregate CSV."""
import csv
from dataclasses import asdict
import platform
from pathlib import Path
from statistics import median
from time import perf_counter
import tracemalloc

from ..search.contracts import Status, validate_result
from ..search.registry import SOLVERS


def _write_csv(path: Path, rows):
    if not rows:
        raise ValueError("There are no benchmark rows to write.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _summary_rows(rows):
    groups = {}
    for row in rows:
        groups.setdefault((row["map"], row["algorithm"]), []).append(row)

    summaries = []
    for (map_name, algorithm), runs in sorted(groups.items()):
        solved = [row for row in runs if row["status"] == Status.SOLVED.value]
        summaries.append({
            "map": map_name,
            "algorithm": algorithm,
            "runs": len(runs),
            "solved_runs": len(solved),
            "timeout_runs": sum(row["status"] == Status.TIMEOUT.value for row in runs),
            "limit_runs": sum(row["status"] == Status.LIMIT_REACHED.value for row in runs),
            "unsolvable_runs": sum(row["status"] == Status.UNSOLVABLE.value for row in runs),
            "median_elapsed_ms": median(row["elapsed_ms"] for row in runs),
            "median_python_peak_bytes": median(row["python_peak_bytes"] for row in runs),
            "median_expanded": median(row["expanded"] for row in runs),
            "median_total_cost_solved": median(row["total_cost"] for row in solved) if solved else "",
        })
    return summaries


def benchmark_suite(layouts, limits, repeats: int, output: Path):
    """Benchmark ``[(map_name, layout), ...]`` and write raw plus summary CSVs.

    Wall time and Python allocation peak are measured in separate runs so
    tracemalloc does not distort elapsed-time measurements. Missing solvers
    fail the sweep before either output file is replaced.
    """
    if type(repeats) is not int or repeats <= 0:
        raise ValueError("repeats must be a positive integer")
    layouts = list(layouts)
    if not layouts:
        raise ValueError("At least one map is required for a benchmark")
    if not SOLVERS:
        raise ValueError("No search algorithms are registered")

    rows = []
    for map_index, (map_name, layout) in enumerate(layouts):
        for repetition in range(repeats):
            algorithms = list(SOLVERS.items())
            if (repetition + map_index) % 2:
                algorithms.reverse()
            for algorithm, solve in algorithms:
                initial = layout.single_state()
                start = perf_counter()
                result = solve(layout.board, initial, limits)
                elapsed_ms = (perf_counter() - start) * 1000
                validate_result(layout.board, initial, result)
                if result.status == Status.NOT_IMPLEMENTED:
                    raise NotImplementedError(
                        f"{algorithm}: no benchmark files written because this solver is not implemented."
                    )

                tracing_was_active = tracemalloc.is_tracing()
                if not tracing_was_active:
                    tracemalloc.start()
                tracemalloc.reset_peak()
                try:
                    memory_result = solve(layout.board, initial, limits)
                    peak_bytes = tracemalloc.get_traced_memory()[1]
                finally:
                    if not tracing_was_active:
                        tracemalloc.stop()
                validate_result(layout.board, initial, memory_result)
                if memory_result.status == Status.NOT_IMPLEMENTED:
                    raise NotImplementedError(
                        f"{algorithm}: memory run reports that the solver is not implemented."
                    )

                rows.append({
                    "map": str(map_name),
                    "algorithm": algorithm,
                    "repeat": repetition + 1,
                    "status": result.status.value,
                    "actions": len(result.actions) if result.status == Status.SOLVED else "",
                    "total_cost": result.total_cost,
                    "elapsed_ms": elapsed_ms,
                    "python_peak_bytes": peak_bytes,
                    "memory_run_status": memory_result.status.value,
                    "memory_run_cost": memory_result.total_cost,
                    "limit_seconds": limits.seconds,
                    "max_expanded_limit": limits.max_expanded,
                    "python": platform.python_version(),
                    "platform": platform.platform(),
                    **asdict(result.metrics),
                })

    output = Path(output)
    summary_output = output.with_name(f"{output.stem}_summary{output.suffix or '.csv'}")
    _write_csv(output, rows)
    _write_csv(summary_output, _summary_rows(rows))
    print(f"Written {len(rows)} measured runs to {output}")
    print(f"Written aggregate results to {summary_output}")
    return output, summary_output


def benchmark(layout, limits, repeats: int, output: Path, map_name: str):
    """Backward-compatible one-map entry point used by earlier callers."""
    return benchmark_suite(((map_name, layout),), limits, repeats, output)
