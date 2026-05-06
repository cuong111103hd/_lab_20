"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.search_client import SearchClient
from multi_agent_research_lab.services.llm_client import LLMClient


class ResearcherAgent(BaseAgent):
    """Thu thập nguồn tài liệu và tạo các ghi chú nghiên cứu súc tích."""

    name = "researcher"

    def __init__(self) -> None:
        self.search_client = SearchClient()
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Cập nhật `state.sources` và `state.research_notes`."""
        
        # 1. Tìm kiếm thông tin
        query = state.request.query
        sources = self.search_client.search(query, max_results=5)
        state.sources.extend(sources)
        
        # 2. Tổng hợp thành ghi chú nghiên cứu
        context = "\n\n".join([f"Source: {s.url}\nContent: {s.content}" for s in sources])
        
        system_prompt = (
            "Bạn là một chuyên gia nghiên cứu. Hãy đọc các tài liệu cung cấp và trích xuất các ý chính quan trọng nhất.\n"
            "Ghi chú phải súc tích, có cấu trúc và sẵn sàng cho việc phân tích chuyên sâu.\n"
            "Hãy giữ lại các trích dẫn (URL) nếu có thể."
        )
        user_prompt = f"Câu hỏi nghiên cứu: {query}\n\nTài liệu:\n{context}"
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.add_tokens(response.input_tokens, response.output_tokens)
        state.research_notes = response.content
        
        state.add_trace_event("researcher_complete", {"num_sources": len(sources)})
        
        return state
