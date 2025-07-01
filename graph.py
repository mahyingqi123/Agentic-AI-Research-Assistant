
from langgraph.graph import StateGraph, START, END

from graph_state import ResearchState
from functions.discussion import run_topic_discussion
from functions.routing import decide_next_step




# --- You'll also need to implement the helper node functions ---
def check_summarization_queue_node(state: ResearchState) -> dict:
    # This node doesn't DO anything except exist for routing
    # The conditional edge logic does the work
    print("DEBUG: Checking summarization queue")
    return {} # No state change

def check_indexing_queue_node(state: ResearchState) -> dict:
    # This node doesn't DO anything except exist for routing
    print("DEBUG: Checking indexing queue")
    return {} # No state change


def create_graph():
    workflow = StateGraph(ResearchState)

    # Add Nodes
    workflow.add_node("route_request", decide_next_step) # Special case: node is the routing function
    workflow.add_node("topic_discussion", run_topic_discussion)
    workflow.set_entry_point("route_request") # Set the entry point to the topic discussion node
    workflow.add_edge("topic_discussion", END) # After discussion, go to router
    # workflow.add_node("search_download", run_search_download)
    # workflow.add_node("check_summarization_queue", check_summarization_queue_node) # Simple function checking list
    # workflow.add_node("summarize_one_paper", run_summarize_one_paper)
    # workflow.add_node("check_indexing_queue", check_indexing_queue_node) # Simple function checking list/flag
    # workflow.add_node("build_index", run_build_index)
    # workflow.add_node("qa_retrieval_generation", run_qa_rag)
    # workflow.add_node("schedule_reading", run_schedule_reading)
    # workflow.add_node("handle_error", handle_error_node) # Optional

    # Entry Point
    # workflow.set_entry_point("route_request")
        # Edges from Agent/Task Nodes
    # Where should execution go *after* a specific task is done?

    # Topic discussion provides output/asks question, then turn ends.
    # workflow.add_edge("topic_discussion", END)

    # Conditional Edges from the Router
    # The keys in the map match the strings returned by decide_next_step
    workflow.add_conditional_edges(
        "route_request",
        # Pass the state to the routing function
        lambda state: decide_next_step(state),
        {
            "topic_discussion": "topic_discussion",
            # "search_download": "search_download",
            # "check_summarization_queue": "check_summarization_queue",
            # "check_indexing_queue": "check_indexing_queue",
            # "qa_retrieval_generation": "qa_retrieval_generation",
            # "schedule_reading": "schedule_reading",
            # Add mapping for error handling if implementing handle_error node
        }
    )



    # After searching, route to decide next step (summarize? index? wait?)
    # workflow.add_edge("search_download", "route_request")

    # # After checking summary queue, either summarize or go back to router
    # workflow.add_conditional_edges(
    #     "check_summarization_queue",
    #     # Simple lambda checking the list length in state
    #     lambda state: "summarize" if state.get("papers_to_summarize") else "route",
    #     {
    #         "summarize": "summarize_one_paper",
    #         "route": "route_request" # Summaries done, figure out next major step
    #     }
    # )

    # # After summarizing one paper, loop back to check the queue again
    # workflow.add_edge("summarize_one_paper", "check_summarization_queue")

    # After checking index queue, either build index or go back to router
    # workflow.add_conditional_edges(
    #     "check_indexing_queue",
    #     # Simple lambda checking list or flag
    #     lambda state: "index" if state.get("papers_to_index") or state.get("index_needs_rebuild") else "route",
    #     {
    #         "index": "build_index",
    #         "route": "route_request" # Indexing done/not needed, figure out next major step
    #     }
    # )

    # After building index, route to decide next step
    # workflow.add_edge("build_index", "route_request")

    # # QA provides the answer, then turn ends.
    # workflow.add_edge("qa_retrieval_generation", END)

    # # Scheduling provides confirmation, then turn ends.
    # workflow.add_edge("schedule_reading", END)

    # Error Handling (Optional)
    # Add edges from your main nodes to 'handle_error' if errors occur
    # workflow.add_edge("handle_error", END) # Or loop back?
    

    # Compile the graph
    app = workflow.compile()
    return app