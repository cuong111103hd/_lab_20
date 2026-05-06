"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Tạo câu trả lời cuối cùng từ các ghi chú nghiên cứu và phân tích."""

    name = "writer"

    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Cập nhật `state.final_answer`."""
        
        if not state.analysis_notes:
            state.errors.append("WriterAgent: Không tìm thấy analysis_notes để viết câu trả lời.")
            return state

        system_prompt = (
            "Bạn là một biên tập viên chuyên nghiệp.\n"
            "Nhiệm vụ của bạn là tổng hợp một câu trả lời cuối cùng hoàn chỉnh, dễ đọc và chuyên sâu dựa trên các thông tin được cung cấp.\n"
            "Yêu cầu:\n"
            "1. Cấu trúc bài viết rõ ràng với các tiêu đề.\n"
            "2. Bao gồm các trích dẫn nguồn (URL) từ danh sách nguồn cung cấp.\n"
            "3. Trình bày dưới dạng Markdown.\n"
            "4. Đảm bảo câu trả lời trực diện vào câu hỏi nghiên cứu ban đầu."
        )
        
        sources_text = "\n".join([f"- {s.title}: {s.url}" for s in state.sources])
        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Analysis Notes:\n{state.analysis_notes}\n\n"
            f"Sources:\n{sources_text}"
        )
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.add_tokens(response.input_tokens, response.output_tokens)
        state.final_answer = response.content
        
        state.add_trace_event("writer_complete", {})
        
        return state
