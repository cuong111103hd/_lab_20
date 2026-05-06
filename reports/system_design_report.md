# Báo cáo Thiết kế Hệ thống và Benchmark Multi-Agent Research

## 1. Vấn đề (Problem)

Xây dựng một trợ lý nghiên cứu (Research Assistant) có khả năng xử lý các câu hỏi phức tạp, yêu cầu tìm kiếm thông tin chuyên sâu từ nhiều nguồn trên web, phân tích đối chiếu dữ liệu và tổng hợp thành báo cáo có cấu trúc chuyên nghiệp kèm trích dẫn chính xác.

## 2. Tại sao chọn Multi-Agent? (Why multi-agent?)

Một hệ thống Single-agent thường gặp khó khăn khi xử lý các tác vụ dài và phức tạp do:
- **Giới hạn Context Window:** Dễ bị nhiễu thông tin khi nạp quá nhiều kết quả tìm kiếm vào một prompt duy nhất.
- **Thiếu tính chuyên môn hóa:** Một prompt duy nhất khó có thể vừa tìm kiếm giỏi, vừa phân tích sắc bén, vừa viết lách mượt mà.
- **Khó kiểm soát lỗi:** Nếu agent bị lạc đề ở bước tìm kiếm, toàn bộ kết quả cuối cùng sẽ bị ảnh hưởng mà không có bước kiểm tra chéo.

Mô hình Multi-agent cho phép chia nhỏ trách nhiệm, áp dụng quy trình kiểm soát chất lượng (như Critic agent) và lặp lại các bước nếu cần thiết để đạt chất lượng tốt nhất.

## 3. Vai trò các Agents (Agent roles)

| Agent | Trách nhiệm | Đầu vào (Input) | Đầu ra (Output) | Chế độ lỗi (Failure mode) |
|---|---|---|---|---|
| **Supervisor** | Điều phối toàn bộ luồng chạy, quyết định agent tiếp theo. | Research State | Route Name | Routing sai dẫn đến lặp vô hạn. |
| **Researcher** | Tìm kiếm thông tin từ web bằng Tavily API. | Query | Research Notes | Không tìm thấy nguồn uy tín. |
| **Analyst** | Phân tích, đối chiếu và trích xuất insights từ ghi chú. | Research Notes | Analysis Notes | Phân tích hời hợt hoặc sai lệch. |
| **Writer** | Tổng hợp báo cáo cuối cùng theo định dạng Markdown. | Analysis Notes | Final Answer | Quên trích dẫn nguồn (citations). |
| **Critic** | Thẩm định, fact-check và đánh giá tính trung thực. | Final Answer + Notes | APPROVED/REVISE | Bỏ sót lỗi logic hoặc ảo giác (hallucination). |

## 4. Trạng thái chia sẻ (Shared state)

Chúng ta sử dụng `ResearchState` (Pydantic) để lưu trữ:
- `request`: Câu hỏi ban đầu và cấu hình.
- `sources`: Danh sách các tài liệu tìm thấy.
- `research_notes`, `analysis_notes`: Kết quả trung gian của các worker.
- `final_answer`: Kết quả cuối cùng.
- `route_history`: Lịch sử điều phối để theo dõi luồng chạy.
- `prompt_tokens`, `completion_tokens`: Để tính toán chi phí.

## 5. Chính sách điều phối (Routing policy)

Hệ thống sử dụng **LangGraph** với cấu trúc đồ thị có hướng:
1. `Supervisor` kiểm tra state.
2. Nếu thiếu thông tin -> `Researcher`.
3. Nếu đã có thông tin -> `Analyst`.
4. Nếu đã có phân tích -> `Writer`.
5. Nếu đã có câu trả lời -> `Critic`.
6. Nếu `Critic` phê duyệt -> `FINISH`. Nếu yêu cầu sửa -> Quay lại `Analyst/Writer`.

## 6. Guardrails (Rào chắn)

- **Max iterations:** Giới hạn 6-10 vòng lặp để tránh chi phí leo thang.
- **Timeout:** 60 giây cho mỗi bước gọi API.
- **Validation:** Sử dụng Pydantic để đảm bảo dữ liệu truyền qua các agent luôn đúng định dạng.
- **Feedback Loop:** Critic agent đóng vai trò là rào chắn chất lượng cuối cùng.

## 7. Kết quả Benchmark (Benchmark Results)

Dựa trên dữ liệu thực tế thu thập được từ lượt chạy gần nhất (bao gồm cả CriticAgent):

| Tên lượt chạy | Thời gian (s) | Chi phí ước tính (USD) | Ghi chú |
|---|---:|---:|---|
| **Baseline** | 20.10 | $0.00061 | Sources found: 3, Iterations: 0 |
| **Multi-Agent** | 79.14 | $0.00332 | Sources found: 5, Iterations: 7 |

### Phân tích kết quả:
- **Thời gian (Latency):** Multi-agent chậm hơn ~4 lần so với Baseline do quy trình tuần tự và kiểm soát chất lượng (bao gồm bước thẩm định của Critic).
- **Chi phí (Cost):** Cao hơn do gọi LLM nhiều lần, nhưng vẫn ở mức cực thấp (~$0.003) nhờ model `gpt-4o-mini`.
- **Chất lượng (Quality):** Multi-agent thu thập được nhiều nguồn tin hơn (5 so với 3) và có quy trình phân tích/thẩm định chặt chẽ hơn, giảm thiểu ảo giác của AI.

---

## 8. Phân tích Failure Modes và Giải pháp khắc phục

Trong quá trình phát triển và chạy benchmark, chúng tôi xác định được một số lỗi tiềm tàng (Failure Modes) và đã triển khai các giải pháp khắc phục:

### 1. Vòng lặp vô hạn (Infinite Routing Loop)
- **Vấn đề:** Supervisor có thể bị quẩn giữa hai agent (ví dụ: Researcher tìm chưa đủ, Analyst yêu cầu tìm lại) dẫn đến cạn kiệt token.
- **Cách fix:** Thiết lập `max_iterations` trong `ResearchState`. Khi đạt đến giới hạn (ví dụ: 7-10 iterations), hệ thống tự động ép buộc Writer tổng hợp câu trả lời từ dữ liệu hiện có hoặc trả về lỗi rõ ràng thay vì chạy tiếp.

### 2. Ảo giác của LLM (Hallucination)
- **Vấn đề:** Agent có thể tự đưa ra các thông tin không có trong kết quả tìm kiếm của Tavily.
- **Cách fix:** Triển khai **Critic Agent**. Agent này không tham gia vào việc tạo nội dung mà chỉ đóng vai trò "thẩm định viên", đối chiếu `Final Answer` với `Research Notes`. Nếu phát hiện sai lệch, Critic sẽ yêu cầu `REVISE`.

### 3. Trôi ngữ cảnh (Context Drift)
- **Vấn đề:** Qua nhiều bước truyền tin giữa các agent, yêu cầu ban đầu của người dùng có thể bị hiểu sai hoặc bị lược bỏ các chi tiết quan trọng.
- **Cách fix:** Luôn đính kèm `ResearchQuery` gốc vào Shared State và yêu cầu các agent (đặc biệt là Writer) phải kiểm tra lại yêu cầu gốc trước khi xuất dữ liệu.

### 4. Lỗi Search API (Tavily Rate Limit)
- **Vấn đề:** Khi query quá nhiều hoặc gặp sự cố mạng, bước Researcher có thể bị fail.
- **Cách fix:** Sử dụng cơ chế **Retry với Exponential Backoff** (thử lại với thời gian chờ tăng dần) trong service layer và cung cấp fallback data nếu cần thiết.

---
*Báo cáo được hoàn thiện bởi Antigravity AI Engineer.*

