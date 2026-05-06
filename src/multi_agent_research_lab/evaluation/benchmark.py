"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Đo lường thời gian chạy, chi phí và các chỉ số hiệu năng."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    
    # Ước tính chi phí (gpt-4o-mini: input ~$0.15/1M, output ~$0.60/1M)
    input_cost = (state.prompt_tokens / 1_000_000) * 0.15
    output_cost = (state.completion_tokens / 1_000_000) * 0.60
    total_cost = input_cost + output_cost
    
    # Citation coverage: số lượng sources thu thập được
    num_sources = len(state.sources)
    
    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=total_cost,
        notes=f"Sources found: {num_sources}, Iterations: {state.iteration}"
    )
    return state, metrics
