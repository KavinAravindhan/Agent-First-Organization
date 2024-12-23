import logging

from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI

from agentorg.workers.worker import BaseWorker, register_worker
from agentorg.utils.graph_state import MessageState
from agentorg.utils.model_config import MODEL

# We'll import our local NLP/Query building modules
from agentorg.nlp.intent_detection import IntentDetector
from agentorg.nlp.spell_check import SpellChecker
from agentorg.nlp.query_builder import QueryBuilder
from agentorg.nlp.db_connector import DBConnector

logger = logging.getLogger(__name__)

@register_worker
class NoSQLQueryWorker(BaseWorker):
    """
    Translates a natural-language user request into a NoSQL query, executes it,
    and returns the results.
    """

    description = "Accepts a user query, converts it to NoSQL, queries a DB, and returns results."

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)
        self.action_graph = self._create_action_graph()

        # Instantiate helper objects (intent detector, spell checker, etc.)
        self.intent_detector = IntentDetector()
        self.spell_checker = SpellChecker()
        self.query_builder = QueryBuilder()
        self.db_connector = DBConnector()

    def _create_action_graph(self):
        """
        Create a simple graph with a single node that performs the entire 
        'NLP -> Query -> DB Execution -> Return results' flow.
        """
        workflow = StateGraph(MessageState)
        workflow.add_node("query_flow", self.query_flow)
        workflow.add_edge(START, "query_flow")
        return workflow

    def query_flow(self, state: MessageState) -> MessageState:
        """
        The main logic for converting the user's text to a NoSQL query and fetching results.
        """
        user_text = state["user_message"].message.strip()
        logger.info(f"NoSQLQueryWorker received text: {user_text}")

        # 1) Spell check
        corrected_text = self.spell_checker.correct_spelling(user_text)

        # 2) Detect intent (find, update, delete, etc.) - simplified example
        intent = self.intent_detector.get_intent(corrected_text)

        # 3) Build the query/filter from the user text
        query = self.query_builder.build_query(corrected_text, intent)
        logger.info(f"Generated query filter: {query}")

        # 4) Execute the query in Mongo
        try:
            results = self.db_connector.execute_query(query, intent)
            # results might be a list of docs or an acknowledgement if update
        except Exception as e:
            logger.error(f"DB execution error: {e}")
            results = {"error": str(e)}

        # 5) Put results into state["response"]
        state["response"] = f"Query Intent: {intent}\nResults: {results}"
        return state

    def execute(self, msg_state: MessageState):
        graph = self.action_graph.compile()
        final_state = graph.invoke(msg_state)
        return {
            "response": final_state.get("response", ""),
        }
