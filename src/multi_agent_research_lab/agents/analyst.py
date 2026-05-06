"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Chuyển đổi các ghi chú nghiên cứu thành các thông tin chi tiết có cấu trúc."""

    name = "analyst"

    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Cập nhật `state.analysis_notes`."""
        
        if not state.research_notes:
            state.errors.append("AnalystAgent: Không tìm thấy research_notes để phân tích.")
            return state

        system_prompt = (
            "Bạn là một chuyên gia phân tích dữ liệu và chiến lược.\n"
            "Nhiệm vụ của bạn là đọc các ghi chú nghiên cứu và:\n"
            "1. Xác định các luận điểm chính.\n"
            "2. So sánh các quan điểm khác nhau (nếu có).\n"
            "3. Đánh giá độ tin cậy của các bằng chứng.\n"
            "4. Đề xuất các kết luận sơ bộ.\n"
            "Hãy viết phân tích một cách khách quan và có cấu trúc."
        )
        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Research Notes:\n{state.research_notes}"
        )
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.add_tokens(response.input_tokens, response.output_tokens)
        state.analysis_notes = response.content
        
        state.add_trace_event("analyst_complete", {})
        
        return state
