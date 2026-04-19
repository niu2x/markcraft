# Performance

This page describes how to benchmark markcraft and how to interpret results.

## Goals

- Track parser performance across releases.
- Compare markcraft with other Python Markdown parsers.
- Detect regressions from parser or renderer changes.

## Run Benchmarks

Install benchmark dependencies first:

```sh
uv sync --group benchmark
```

Use the built-in benchmark script:

```sh
uv run python tests/benchmark.py
```

## Benchmark Method

- Input corpus comes from `tests/samples/`.
- Multiple parser libraries are executed for the same inputs.
- Reported values are elapsed time in seconds.

For meaningful comparisons, keep these constants fixed:

- Python version
- CPU and load conditions
- iteration count
- dependency versions

## Interpreting Results

- Lower total time is better.
- Small differences may be noise; rerun and average.
- Large jumps after a change usually indicate a real regression.

Performance alone is not the only goal. markcraft prioritizes predictable,
CommonMark-oriented behavior and extensibility as well.

## Reproducibility Checklist

When publishing numbers, include:

- markcraft version (`markcraft.__version__`)
- Python version
- operating system
- CPU model
- benchmark command and iteration settings

## Optimization Guidance

Before optimizing:

1. Confirm the bottleneck with profiling.
2. Add regression tests for behavior.
3. Re-run benchmarks before and after changes.

Avoid micro-optimizations that reduce readability without measurable gain.
