"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

from multi_agent_research_lab.core.errors import StudentTodoError


from multi_agent_research_lab.core.config import get_settings
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


@dataclass(frozen=True)
class LLMResponse:
    """Cấu trúc phản hồi từ LLM."""
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Client giao tiếp với OpenAI LLM."""

    def __init__(self) -> None:
        settings = get_settings()
        self.model = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0,
        )

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Thực hiện gọi model và nhận kết quả completion.
        
        Sử dụng LangChain OpenAI client để gọi API.
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        response = self.model.invoke(messages)
        
        # Trích xuất thông tin token sử dụng nếu có
        usage = getattr(response, "response_metadata", {}).get("token_usage", {})
        
        return LLMResponse(
            content=str(response.content),
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            # Cost sẽ được tính toán sau trong bước benchmark nếu cần
        )
