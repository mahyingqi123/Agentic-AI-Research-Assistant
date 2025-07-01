# graph_state.py

from typing import List, Dict, Optional, TypedDict, Annotated
from langchain_core.messages import BaseMessage # Import base class for messages

# --- Helper Reducer Function for Messages ---
# LangGraph needs this to know HOW to update the messages list (append vs overwrite)
def add_messages(left: List[BaseMessage], right: List[BaseMessage]) -> List[BaseMessage]:
    """Append new messages to the existing list."""
    return left + right

# --- Define Sub-Structures for Clarity ---

class PaperInfo(TypedDict):
    """Structure to hold information about a single research paper."""
    # Identifiers
    paper_id: str                 # A unique ID (e.g., arXiv ID, DOI, or generated hash of title)
    arxiv_id: Optional[str]       # Specifically if from arXiv
    doi: Optional[str]            # Digital Object Identifier
    # Core Metadata
    title: str
    authors: List[str]
    abstract: Optional[str]
    published_date: Optional[str] # e.g., "YYYY-MM-DD"
    # Source and Local Storage
    source_url: Optional[str]     # URL of the paper page (e.g., arXiv abstract page)
    pdf_url: Optional[str]        # Direct URL to the PDF file
    local_path: Optional[str]     # Filesystem path where the PDF is saved
    # Processing Status Flags
    needs_summary: bool           # Flag: Does this paper still need summarization?
    has_summary: bool             # Flag: Has a summary been generated?
    summary_text: Optional[str]   # Store the generated summary text here (can be None)
    indexed_in_rag: bool          # Flag: Is the content of this paper included in the FAISS index?

class UserPreferences(TypedDict):
    """Structure for user-specific settings, primarily for the scheduler."""
    experience_level: Optional[str] # e.g., 'beginner', 'intermediate', 'expert'
    hours_per_week: Optional[int]   # Estimated time available for reading/research per week
    calendar_id: Optional[str]      # User's Google Calendar ID (defaults to 'primary')
    # Add other preferences like preferred reading times if needed

# --- Define the Main Research State TypedDict ---

class ResearchState(TypedDict):
    """
    The central state object passed between nodes in the LangGraph workflow
    for the Agentic Research Assistant.
    """

    # === Core Conversation & Task Management ===
    messages: Annotated[List[BaseMessage], add_messages] # Full conversation history
    initial_user_query: Optional[str]   # The user's very first research request
    current_user_request: Optional[str]# The text content of the latest user message being processed
    last_user_request_type: Optional[str] # User's intent for the current turn (e.g., 'qa', 'search', 'summarize', 'schedule', 'discuss')

    # === Topic Refinement ===
    refined_research_question: Optional[str] # The specific question finalized by TopicDiscussionAgent
    subtopics: Optional[List[str]]           # Key subtopics identified during discussion

    # === Paper Discovery & Management ===
    papers: Optional[List[PaperInfo]] # List of papers found by SearchDownloadAgent
    # Queues for background processing (using paper_id for reference)
    papers_to_summarize: Optional[List[str]] # List of paper_ids needing summary
    papers_to_index: Optional[List[str]]     # List of paper_ids needing indexing for RAG

    # === RAG (Retrieval-Augmented Generation) ===
    vector_store_path: Optional[str]    # Path to the saved FAISS index file
    index_needs_rebuild: bool           # Flag if new papers were added/summarized since last build (Defaults to False)

    # === Scheduling ===
    user_preferences: Optional[UserPreferences] # User's scheduling preferences
    schedule_confirmation: Optional[str]      # Confirmation message from ReadingSchedulerAgent

    # === Error Handling / Status ===
    last_error: Optional[str]           # Store information about the last error encountered
    status_message: Optional[str]       # A message indicating current status (e.g., "Summarizing paper X...")


