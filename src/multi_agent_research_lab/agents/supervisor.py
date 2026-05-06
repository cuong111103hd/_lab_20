"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.config import get_settings


class SupervisorAgent(BaseAgent):
    """Quyết định agent nào sẽ chạy tiếp theo và khi nào dừng lại."""

    name = "supervisor"

    def __init__(self) -> None:
        self.llm = LLMClient()
        self.settings = get_settings()

    def run(self, state: ResearchState) -> ResearchState:
        """Cập nhật `state.route_history` với route tiếp theo."""
        
        # 1. Kiểm tra giới hạn số lần lặp
        if state.iteration >= self.settings.max_iterations:
            state.record_route("FINISH")
            return state

        # 2. Xây dựng prompt cho Supervisor
        system_prompt = (
            "Bạn là một Supervisor điều phối quy trình nghiên cứu.\n"
            "Các agent khả dụng:\n"
            "- researcher: Tìm kiếm thông tin mới trên web.\n"
            "- analyst: Phân tích các ghi chú nghiên cứu đã có.\n"
            "- writer: Viết câu trả lời cuối cùng dựa trên phân tích.\n"
            "- critic: Kiểm tra tính chính xác và trích dẫn của câu trả lời.\n"
            "\n"
            "Quy tắc:\n"
            "1. Nếu chưa có thông tin (research_notes trống), hãy gọi researcher.\n"
            "2. Nếu đã có thông tin nhưng chưa có phân tích, hãy gọi analyst.\n"
            "3. Nếu đã có phân tích nhưng chưa có câu trả lời, hãy gọi writer.\n"
            "4. Nếu đã có câu trả lời nhưng chưa được critic kiểm tra, hãy gọi critic.\n"
            "5. Nếu critic yêu cầu sửa (REVISE), hãy quay lại analyst hoặc writer tùy mức độ.\n"
            "6. Nếu critic phê duyệt (APPROVED), hãy chọn FINISH.\n"
            "\n"
            "Chỉ trả về tên agent (researcher, analyst, writer, critic, FINISH) và không có gì khác."
        )
        
        user_prompt = (
            f"Query: {state.request.query}\n"
            f"Iteration: {state.iteration}\n"
            f"Research Notes: {state.research_notes[:200] if state.research_notes else 'Trống'}\n"
            f"Analysis Notes: {state.analysis_notes[:200] if state.analysis_notes else 'Trống'}\n"
            f"Final Answer: {'Đã có' if state.final_answer else 'Chưa có'}\n"
            f"Last Route: {state.route_history[-1] if state.route_history else 'None'}\n"
        )
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.add_tokens(response.input_tokens, response.output_tokens)
        next_step = response.content.strip().lower()
        
        # 3. Ghi nhận route
        if next_step not in ["researcher", "analyst", "writer", "critic", "finish"]:
            # Fallback logic
            if not state.research_notes:
                next_step = "researcher"
            elif not state.analysis_notes:
                next_step = "analyst"
            elif not state.final_answer:
                next_step = "writer"
            elif state.route_history[-1] != "APPROVED" and state.route_history[-1] != "CRITIC":
                next_step = "critic"
            else:
                next_step = "finish"
        
        state.record_route(next_step.upper())
        state.add_trace_event("supervisor_decision", {"next_step": next_step})
        
        return state
