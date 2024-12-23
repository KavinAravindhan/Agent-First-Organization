import logging

from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.vectorstores import Chroma

from agentorg.workers.worker import BaseWorker, register_worker
from agentorg.utils.graph_state import MessageState
from agentorg.utils.model_config import MODEL

logger = logging.getLogger(__name__)

@register_worker
class VectorDBWorker(BaseWorker):
    """
    A worker for advanced retrieval from a vector DB (like Chroma, Pinecone, etc.).
    """

    description = "Performs advanced retrieval using a vector store to find relevant documents."

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)
        self.action_graph = self._create_action_graph()
        # Initialize or load the vector DB as needed
        # e.g., self._init_vector_db()

    def _create_action_graph(self):
        workflow = StateGraph(MessageState)

        # For simplicity, just one node: do the vector retrieval
        workflow.add_node("vector_retrieval", self.vector_retrieval)
        workflow.add_edge(START, "vector_retrieval")

        return workflow

    def vector_retrieval(self, state: MessageState) -> MessageState:
        user_text = state["user_message"].message
        logger.info(f"VectorDBWorker: retrieving docs for text: {user_text}")

        # Real logic:
        # 1) Embed the user_text
        # 2) Query the vector DB for top_k docs
        # 3) Possibly pass docs to LLM for a summarized answer
        # For demo, we mock a response
        retrieved_docs = [
            {"title": "Doc1", "content": "Relevant info about your query..."},
            {"title": "Doc2", "content": "Even more relevant info..."},
        ]
        # Summarize or store in state
        state["response"] = f"Found {len(retrieved_docs)} docs from the vector DB."
        state["retrieved_docs"] = retrieved_docs
        return state

    def execute(self, msg_state: MessageState):
        graph = self.action_graph.compile()
        result = graph.invoke(msg_state)
        # Return a dict consistent with your other workers
        return {
            "response": result.get("response", ""),
            "retrieved_docs": result.get("retrieved_docs", []),
        }
