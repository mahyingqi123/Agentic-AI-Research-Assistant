from typing import Dict, Any
from langchain_core.messages import BaseMessage
from graph_state import ResearchState

def decide_next_step(state: ResearchState) -> str:
    """Determines the next node to execute based on the current state."""

    last_request_type = state.get("last_user_request_type")
    question_refined = bool(state.get("refined_research_question"))
    papers_exist = bool(state.get("papers"))
    papers_to_summarize = state.get("papers_to_summarize", [])
    papers_to_index = state.get("papers_to_index", [])
    index_exists = bool(state.get("vector_store_path"))
    index_needs_rebuild = state.get("index_needs_rebuild", False)

    print(f"DEBUG: Routing based on state: last_request_type={last_request_type}, question_refined={question_refined}, papers_exist={papers_exist}, len(papers_to_summarize)={len(papers_to_summarize)}, len(papers_to_index)={len(papers_to_index)}, index_exists={index_exists}, index_needs_rebuild={index_needs_rebuild}")

    # --- Priority 1: Handle explicit user requests ---
    if last_request_type == 'qa' and index_exists:
        return "qa_retrieval_generation"
    if last_request_type == 'schedule' and papers_exist:
        # TODO: Add check for Google Auth token if needed before routing
        return "schedule_reading"
    if last_request_type == 'search' and question_refined:
        return "search_download"
    if last_request_type == 'summarize' and papers_exist:
         # Go check the queue first
        return "check_summarization_queue"
    if last_request_type == 'index' and papers_exist:
         # Go check if indexing is needed
        return "check_indexing_queue"
    if last_request_type == 'discuss' or last_request_type == 'refine':
        return "topic_discussion"

    # --- Priority 2: Implicit workflow progression ---
    if not question_refined:
        # If topic isn't clear, always go back to discussion
        return "topic_discussion"

    if not papers_exist:
        # If topic is clear but no papers, search
        return "search_download"

    # Check background tasks only if no specific user request conflicts
    if papers_to_summarize:
        return "check_summarization_queue"

    if papers_to_index or index_needs_rebuild:
         # Check if indexing is needed after summarization might be done
        return "check_indexing_queue"

    # --- Fallback ---
    # If topic is refined, papers exist, summaries/indexing done,
    # and no specific user request is pending, wait for user input/clarification.
    # Returning to topic_discussion might let it give a status update or prompt.
    print("DEBUG: Fallback routing to topic_discussion")
    return "topic_discussion"