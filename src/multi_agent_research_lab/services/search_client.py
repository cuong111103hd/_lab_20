"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import SourceDocument


from multi_agent_research_lab.core.config import get_settings
from tavily import TavilyClient


class SearchClient:
    """Client thực hiện tìm kiếm thông tin qua Tavily API."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = TavilyClient(api_key=settings.tavily_api_key)

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Tìm kiếm các tài liệu liên quan đến truy vấn.
        
        Sử dụng Tavily để lấy các kết quả tìm kiếm chất lượng cao.
        """
        response = self.client.search(query=query, max_results=max_results, search_depth="advanced")
        
        results = []
        for result in response.get("results", []):
            results.append(
                SourceDocument(
                    title=result.get("title", "Untitled"),
                    url=result.get("url", ""),
                    content=result.get("content", ""),
                    relevance_score=result.get("score", 0.0),
                )
            )
        return results
