"""Command-line entrypoint for the lab starter."""

import os
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery, BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.observability.tracing import init_tracing
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    init_tracing()


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Chạy baseline single-agent thực tế."""

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    
    # 1. Search
    search_client = SearchClient()
    docs = search_client.search(query, max_results=3)
    state.sources.extend(docs)
    context = "\n\n".join([f"Source: {d.url}\nContent: {d.content}" for d in docs])
    
    # 2. LLM completion
    llm_client = LLMClient()
    system_prompt = "Bạn là một research assistant chuyên nghiệp. Hãy trả lời câu hỏi dựa trên các tài liệu cung cấp."
    user_prompt = f"Câu hỏi: {query}\n\nTài liệu:\n{context}"
    
    response = llm_client.complete(system_prompt, user_prompt)
    state.add_tokens(response.input_tokens, response.output_tokens)
    state.final_answer = response.content
    
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    
    console.print(Panel.fit(result.final_answer or "Không có câu trả lời.", title="Multi-Agent Result"))
    console.print(f"Total Iterations: {result.iteration}")
    console.print(f"Total Tokens: {result.prompt_tokens + result.completion_tokens}")


@app.command()
def benchmark(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Chạy benchmark so sánh Single-Agent vs Multi-Agent."""
    
    _init()
    metrics_list: list[BenchmarkMetrics] = []
    
    # 1. Run Baseline
    console.print("[bold blue]Running Baseline...[/bold blue]")
    def baseline_runner(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        
        # Search
        search_client = SearchClient()
        docs = search_client.search(q, max_results=3)
        state.sources.extend(docs)
        context = "\n\n".join([f"Source: {d.url}\nContent: {d.content}" for d in docs])
        
        # LLM
        llm_client = LLMClient()
        response = llm_client.complete(
            "Bạn là một research assistant.",
            f"Câu hỏi: {q}\n\nTài liệu:\n{context}"
        )
        state.add_tokens(response.input_tokens, response.output_tokens)
        state.final_answer = response.content
        return state

    _, b_metrics = run_benchmark("Baseline", query, baseline_runner)
    metrics_list.append(b_metrics)
    
    # 2. Run Multi-Agent
    console.print("[bold green]Running Multi-Agent...[/bold green]")
    def multi_agent_runner(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        return workflow.run(state)
        
    _, m_metrics = run_benchmark("Multi-Agent", query, multi_agent_runner)
    metrics_list.append(m_metrics)
    
    # 3. Render and save report
    report_md = render_markdown_report(metrics_list)
    os.makedirs("reports", exist_ok=True)
    with open("reports/benchmark_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)
        
    console.print(Panel.fit("Benchmark hoàn tất! Báo cáo đã được lưu tại reports/benchmark_report.md", style="green"))


if __name__ == "__main__":
    app()
