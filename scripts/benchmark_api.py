"""Measure search/read latency against a running BioInsight API (roadmap 5.3).

Usage:
    py -3 scripts/benchmark_api.py --base-url http://localhost:8000 --iterations 200

Reports p50/p95/p99 latency per endpoint. Requires the stack to be up and seeded
(see docs/PLATFORM.md). Numbers are environment-dependent; record them in
docs/BENCHMARKS.md alongside the host spec.
"""
from __future__ import annotations

import argparse
import statistics
import time
import urllib.request

ENDPOINTS = [
    ("search_genes", "/api/v1/genes?q=BRCA"),
    ("gene_detail", "/api/v1/genes/ENSG00000012048"),
    ("gene_diseases", "/api/v1/genes/ENSG00000012048/diseases"),
    ("gene_evidence", "/api/v1/genes/ENSG00000012048/evidence"),
    ("stats", "/api/v1/stats"),
]


def _time_request(url: str) -> float:
    start = time.perf_counter()
    with urllib.request.urlopen(url, timeout=10) as resp:
        resp.read()
    return (time.perf_counter() - start) * 1000.0


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, int(round(pct / 100.0 * (len(ordered) - 1))))
    return ordered[idx]


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark BioInsight API latency")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--iterations", type=int, default=200)
    parser.add_argument("--warmup", type=int, default=10)
    args = parser.parse_args()

    print(f"{'endpoint':<16}{'p50 ms':>10}{'p95 ms':>10}{'p99 ms':>10}{'mean ms':>10}")
    for name, path in ENDPOINTS:
        url = args.base_url.rstrip("/") + path
        for _ in range(args.warmup):
            _time_request(url)
        samples = [_time_request(url) for _ in range(args.iterations)]
        print(
            f"{name:<16}"
            f"{_percentile(samples, 50):>10.1f}"
            f"{_percentile(samples, 95):>10.1f}"
            f"{_percentile(samples, 99):>10.1f}"
            f"{statistics.mean(samples):>10.1f}"
        )


if __name__ == "__main__":
    main()
