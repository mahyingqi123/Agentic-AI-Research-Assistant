import os
from typing import Dict, List, Optional
from langchain_core.messages import AIMessage, BaseMessage # Import AIMessage
from dotenv import load_dotenv

# Import your specific state definition and agent
from graph_state import ResearchState
# Make sure this path is correct for your project structure
from agents.topic_discussion_agent import TopicDiscussionAgent

# Optional: Load .env only if agent doesn't handle it reliably, adjust path
# load_dotenv('../.env')

def run_topic_discussion(state: ResearchState) -> Dict:
    """
    Executes the Topic Discussion Agent based on the current conversation state.
    Updates state with refined topic, subtopics, and AI response.

    Args:
        state (ResearchState): The current state of the graph.

    Returns:
        Dict: A dictionary containing updates to be applied to the ResearchState.
    """
    print("---NODE: Running Topic Discussion---")
    updates = {}
    error_message = None
    status_msg = "Processing discussion..."

    messages: List[BaseMessage] = state['messages']
    # Get existing values for potential fallback
    current_refined_question: Optional[str] = state.get('refined_research_question')
    current_subtopics: Optional[List[str]] = state.get('subtopics')

    # Initialize agent (consider initializing once outside if agent init is heavy)
    discussion_agent = TopicDiscussionAgent()

    # Call the agent - expecting a dictionary return value
    agent_output: Dict = discussion_agent.run(messages) # Agent returns a Dict now

    # --- CORRECTED: Extract results using dictionary keys ---
    # Get the content intended for the AI's chat response
    assistant_response_content = agent_output.get("ai_message_content")
    # Get other potential state updates
    agent_refined_question = agent_output.get("refined_question")
    agent_subtopics = agent_output.get("subtopics")
    # agent_suggestions = agent_output.get("suggestions") # Available if needed
    # agent_follow_up = agent_output.get("follow_up_questions") # Available if needed
    # --- End Correction ---

    # Handle case where AI content might be missing (e.g., parsing error in agent)
    if assistant_response_content is None:
            assistant_response_content = "Sorry, I encountered an issue processing that."
            error_message = "Agent failed to generate valid response content."
            print("ERROR: Agent output missing 'ai_message_content'")

    status_msg = "Discussion turn processed."
    print(f"DEBUG: Discussion Agent Output - AI Content: '{assistant_response_content[:100]}...', RefinedQ: {agent_refined_question}, Subtopics: {agent_subtopics}")

    # Prepare State Updates
    # Add the assistant's response to the messages list for the reducer
    updates["messages"] = [AIMessage(content=assistant_response_content)]

    # Update refined question only if the agent provided a new one (and it's not None)
    if agent_refined_question is not None:
        updates["refined_research_question"] = agent_refined_question
    # else: # No need for else if we want to keep the existing value implicitly

    # Update subtopics only if the agent provided new ones (and it's not None)
    if agent_subtopics is not None:
        updates["subtopics"] = agent_subtopics # Agent returns [] if none found
    # else: # No need for else

    # Clear request type after handling discussion
    updates["last_user_request_type"] = None


    # Update status and error fields consistently outside the main try block
    updates["last_error"] = error_message
    updates["status_message"] = status_msg

    print(f"---NODE: Topic Discussion Complete. Updating state: {list(updates.keys())} ---")
    return updates