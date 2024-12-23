import logging

from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI

from agentorg.workers.worker import BaseWorker, register_worker
from agentorg.utils.graph_state import MessageState
from agentorg.workers.tools.RAG.utils import SearchEngine, ToolGenerator
from agentorg.utils.model_config import MODEL

# Adding for trace logger
from agentorg.utils.trace_logger import TraceLogger


logger = logging.getLogger(__name__)


# Adding for trace logger
trace_logger = TraceLogger()  # Create a global or instance-level trace logger

@register_worker
class SearchWorker(BaseWorker):
    ...
    



@register_worker
class SearchWorker(BaseWorker):

    description = "Answer the user's questions based on real-time online search results"

    def __init__(self):
        super().__init__()
        self.action_graph = self._create_action_graph()
        self.llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)
     
    def _create_action_graph(self):
        workflow = StateGraph(MessageState)
        # Add nodes for each worker
        search_engine = SearchEngine()
        workflow.add_node("search_engine", search_engine.search)
        workflow.add_node("tool_generator", ToolGenerator.context_generate)
        # Add edges
        workflow.add_edge(START, "search_engine")
        workflow.add_edge("search_engine", "tool_generator")
        return workflow

    def execute(self, msg_state: MessageState):
        # Start trace
        trace_logger.start_trace("SearchWorker Execution")

        graph = self.action_graph.compile()
        result = graph.invoke(msg_state)

        # Log the final result
        trace_logger.log_event("SearchWorker result", {"response": result.get("response", "")})
        trace_logger.end_trace("SearchWorker Execution Finished")

        return result
