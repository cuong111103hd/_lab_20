"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.llm_client import LLMClient


class CriticAgent(BaseAgent):
    """Agent chuyên thực hiện fact-checking và đánh giá chất lượng câu trả lời."""

    name = "critic"

    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Kiểm tra câu trả lời cuối cùng và đưa ra phản hồi/góp ý."""
        
        if not state.final_answer:
            state.errors.append("CriticAgent: Không có câu trả lời cuối cùng để đánh giá.")
            return state

        system_prompt = (
            "Bạn là một chuyên gia thẩm định và fact-checker.\n"
            "Nhiệm vụ của bạn là đánh giá câu trả lời cuối cùng dựa trên các ghi chú nghiên cứu (research notes).\n"
            "Các tiêu chí đánh giá:\n"
            "1. Tính chính xác: Có thông tin nào sai lệch so với nguồn không?\n"
            "2. Độ phủ trích dẫn: Các luận điểm chính đã có nguồn trích dẫn chưa?\n"
            "3. Sự đầy đủ: Có thông tin quan trọng nào trong research notes bị bỏ sót không?\n"
            "4. Tính trung thực (Hallucination): Có thông tin nào LLM tự bịa ra mà không có trong nguồn không?\n\n"
            "Nếu câu trả lời ĐẠT yêu cầu, hãy bắt đầu bằng từ 'APPROVED'.\n"
            "Nếu CẦN CHỈNH SỬA, hãy liệt kê các lỗi cụ thể và bắt đầu bằng từ 'REVISE'."
        )
        
        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Research Notes:\n{state.research_notes}\n\n"
            f"Final Answer:\n{state.final_answer}"
        )
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.add_tokens(response.input_tokens, response.output_tokens)
        
        # Lưu kết quả phê bình vào metadata hoặc một trường riêng nếu cần
        state.add_trace_event("critic_feedback", {"feedback": response.content})
        
        # Nếu cần sửa đổi, ta có thể đánh dấu trong state để Supervisor biết
        if response.content.startswith("REVISE"):
            state.analysis_notes = f"CRITIC FEEDBACK: {response.content}\n\n{state.analysis_notes}"
            state.record_route("REVISE") # Đánh dấu để quay lại bước trước nếu cần
        else:
            state.record_route("APPROVED")

        return state
