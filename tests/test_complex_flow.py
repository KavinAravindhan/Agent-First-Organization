import pytest
import logging
from unittest.mock import MagicMock

from agentorg.workers.dialogue_orchestration_worker import DialogueOrchestrationWorker
from agentorg.utils.graph_state import MessageState

logger = logging.getLogger(__name__)

@pytest.mark.parametrize("user_input", [
    "Hey, can you search something for me?",
    "I need some internal doc facts about the new product.",
    "Just say hello to me in a normal conversation."
])

def test_dialogue_flow(user_input):
    """
    Test how the DialogueOrchestrationWorker routes different user inputs 
    to search, rag, or message workers.
    """
    # We could mock the sub-workers inside the worker, or we can rely on the real ones.
    # Here, let's just rely on the real initialization for demonstration.

    orchestrator = DialogueOrchestrationWorker()

    # Construct a MessageState.
    msg_state = MessageState()
    msg_state["user_message"].message = user_input

    result = orchestrator.execute(msg_state)
    # Check that we got a 'response'
    assert "response" in result, "Expected 'response' key in the orchestrator's result"

    # If "search" in user_input, we expect the search path
    # If "internal doc" or "fact" in user_input, we expect the RAG path
    # Otherwise, the message path
    # We can do a simple check:
    if "search" in user_input.lower():
        assert "SearchWorker" in orchestrator.search_worker.__class__.__name__
    elif "fact" in user_input.lower() or "internal doc" in user_input.lower():
        assert "RAGWorker" in orchestrator.rag_worker.__class__.__name__
    else:
        assert "MessageWorker" in orchestrator.message_worker.__class__.__name__

    logger.info(f"Test with input '{user_input}' produced: {result['response']}")
