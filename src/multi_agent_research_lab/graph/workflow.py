"""LangGraph workflow skeleton."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from langgraph.graph import StateGraph, END
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.writer import WriterAgent


from langgraph.graph import StateGraph, END
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.agents.critic import CriticAgent


class MultiAgentWorkflow:
    """Xây dựng và chạy đồ thị multi-agent."""

    def __init__(self) -> None:
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.critic = CriticAgent()

    def build(self) -> StateGraph:
        """Tạo đồ thị LangGraph."""
        
        builder = StateGraph(ResearchState)
        
        # Thêm các nodes
        builder.add_node("supervisor", self.supervisor.run)
        builder.add_node("researcher", self.researcher.run)
        builder.add_node("analyst", self.analyst.run)
        builder.add_node("writer", self.writer.run)
        builder.add_node("critic", self.critic.run)
        
        # Thiết lập điểm bắt đầu
        builder.set_entry_point("supervisor")
        
        # Thêm các cạnh điều kiện từ supervisor
        builder.add_conditional_edges(
            "supervisor",
            lambda state: state.route_history[-1] if state.route_history else "FINISH",
            {
                "RESEARCHER": "researcher",
                "ANALYST": "analyst",
                "WRITER": "writer",
                "CRITIC": "critic",
                "REVISE": "analyst", # Nếu critic bảo REVISE, supervisor có thể đưa về analyst
                "APPROVED": END,     # Nếu critic bảo APPROVED, kết thúc qua supervisor
                "FINISH": END
            }
        )
        
        # Sau mỗi worker, quay lại supervisor
        builder.add_edge("researcher", "supervisor")
        builder.add_edge("analyst", "supervisor")
        builder.add_edge("writer", "supervisor")
        builder.add_edge("critic", "supervisor")
        
        return builder.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Thực thi đồ thị và trả về trạng thái cuối cùng."""
        
        app = self.build()
        # LangGraph invoke trả về dict các trường đã cập nhật hoặc chính State object tùy cấu hình
        # Ở đây builder dùng ResearchState class nên nó sẽ trả về instance của ResearchState
        result = app.invoke(state)
        
        # Nếu result là dict (tùy version langgraph), ta cần convert lại
        if isinstance(result, dict):
            return ResearchState(**result)
            
        return result
