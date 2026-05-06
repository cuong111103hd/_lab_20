# Báo cáo so sánh Single-Agent vs Multi-Agent

Báo cáo này so sánh hiệu năng giữa hệ thống Baseline (Single-Agent) và hệ thống Nghiên cứu Multi-Agent.

## Bảng chỉ số

| Tên lượt chạy | Thời gian (s) | Chi phí ước tính (USD) | Ghi chú |
|---|---:|---:|---|
| Baseline | 20.10 | $0.00061 | Sources found: 3, Iterations: 0 |
| Multi-Agent | 79.14 | $0.00332 | Sources found: 5, Iterations: 7 |

## Phân tích kết quả
- **Thời gian (Latency):** Multi-agent thường chậm hơn do có nhiều bước điều phối và gọi LLM nhiều lần.
- **Chi phí (Cost):** Multi-agent tiêu tốn nhiều token hơn nhưng mang lại độ sâu thông tin tốt hơn.
- **Chất lượng (Quality):** Hệ thống multi-agent có khả năng tự kiểm tra và phân tích đa chiều hơn.
