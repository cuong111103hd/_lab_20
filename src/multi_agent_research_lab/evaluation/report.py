"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Chuyển đổi các chỉ số benchmark thành báo cáo Markdown."""

    lines = [
        "# Báo cáo so sánh Single-Agent vs Multi-Agent",
        "",
        "Báo cáo này so sánh hiệu năng giữa hệ thống Baseline (Single-Agent) và hệ thống Nghiên cứu Multi-Agent.",
        "",
        "## Bảng chỉ số",
        "",
        "| Tên lượt chạy | Thời gian (s) | Chi phí ước tính (USD) | Ghi chú |",
        "|---|---:|---:|---|",
    ]
    
    for item in metrics:
        cost = "N/A" if item.estimated_cost_usd is None else f"${item.estimated_cost_usd:.5f}"
        lines.append(f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {item.notes} |")
    
    lines.extend([
        "",
        "## Phân tích kết quả",
        "- **Thời gian (Latency):** Multi-agent thường chậm hơn do có nhiều bước điều phối và gọi LLM nhiều lần.",
        "- **Chi phí (Cost):** Multi-agent tiêu tốn nhiều token hơn nhưng mang lại độ sâu thông tin tốt hơn.",
        "- **Chất lượng (Quality):** Hệ thống multi-agent có khả năng tự kiểm tra và phân tích đa chiều hơn.",
    ])
    
    return "\n".join(lines) + "\n"
