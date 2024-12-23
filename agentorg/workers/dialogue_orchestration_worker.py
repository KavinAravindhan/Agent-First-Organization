import logging

from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI

from agentorg.workers.worker import BaseWorker, register_worker
from agentorg.utils.graph_state import MessageState
from agentorg.utils.model_config import MODEL
from agentorg.workers.search_worker import SearchWorker
from agentorg.workers.rag_worker import RAGWorker
from agentorg.workers.message_worker import MessageWorker

logger = logging.getLogger(__name__)

@register_worker
class DialogueOrchestrationWorker(BaseWorker):
    """
    A worker that orchestrates multi-turn conversation flows, deciding which
    sub-worker to invoke (Search, RAG, or standard Message).
    """

    description = "Orchestrates calls to various sub-workers (Search, RAG, Message) based on user input."

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)
        self.action_graph = self._create_action_graph()
        # Optionally create the actual sub-worker instances
        self.search_worker = SearchWorker()
        self.rag_worker = RAGWorker()
        self.message_worker = MessageWorker()

    def _create_action_graph(self):
        workflow = StateGraph(MessageState)

        # 1) Node that decides which worker to call
        workflow.add_node("decide_worker", self.decide_worker)

        # 2) Node that might call search
        #    We'll define these "call_search", "call_rag", etc. as separate methods
        workflow.add_node("call_search", self.call_search)
        workflow.add_node("call_rag", self.call_rag)
        workflow.add_node("call_message", self.call_message)

        # Edges:
        # Start --> decide_worker
        workflow.add_edge(START, "decide_worker")

        # From decide_worker, we’ll jump to either search, rag, or message
        workflow.add_edge("decide_worker", "call_search", condition=lambda state: state.get("chosen_worker") == "search")
        workflow.add_edge("decide_worker", "call_rag", condition=lambda state: state.get("chosen_worker") == "rag")
        workflow.add_edge("decide_worker", "call_message", condition=lambda state: state.get("chosen_worker") == "message")

        return workflow

    def decide_worker(self, state: MessageState) -> MessageState:
        """
        Analyze the user's message and decide which worker to call next.
        """
        user_text = state["user_message"].message.lower()

        if "search" in user_text:
            logger.info("DialogueOrchestrationWorker: routing to SearchWorker")
            state["chosen_worker"] = "search"
        elif "fact" in user_text or "internal doc" in user_text or "rag" in user_text:
            logger.info("DialogueOrchestrationWorker: routing to RAGWorker")
            state["chosen_worker"] = "rag"
        else:
            logger.info("DialogueOrchestrationWorker: routing to MessageWorker")
            state["chosen_worker"] = "message"

        return state

    def call_search(self, state: MessageState) -> MessageState:
        """
        Invoke the SearchWorker.
        """
        # We assume the search worker returns a dict with 'response' in it
        result = self.search_worker.execute(state)
        # Put that into state["response"]
        if isinstance(result, dict) and "response" in result:
            state["response"] = result["response"]
        return state

    def call_rag(self, state: MessageState) -> MessageState:
        """
        Invoke the RAGWorker.
        """
        result = self.rag_worker.execute(state)
        if isinstance(result, dict) and "response" in result:
            state["response"] = result["response"]
        return state

    def call_message(self, state: MessageState) -> MessageState:
        """
        Invoke the basic MessageWorker.
        """
        result = self.message_worker.execute(state)
        if isinstance(result, dict) and "response" in result:
            state["response"] = result["response"]
        return state

    def execute(self, msg_state: MessageState):
        """
        Orchestrate the pipeline by compiling the graph and invoking it with msg_state.
        """
        graph = self.action_graph.compile()
        result = graph.invoke(msg_state)  # final state
        return {"response": result.get("response", "No response generated.")}
