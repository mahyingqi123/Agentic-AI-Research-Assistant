
from langchain_core.messages import HumanMessage
import streamlit as st
from graph_state import ResearchState
from graph import create_graph

# Example usage
if __name__ == "__main__":
    app = create_graph()

    st.title("Research Assistant")
    if 'state' not in st.session_state:
        initial_state = ResearchState(
        messages=[],
        initial_user_query=None,
        current_user_request=None,
        last_user_request_type=None,
        refined_research_question=None,
        subtopics=None,
        papers=None, # Or [] if you prefer an empty list default
        papers_to_summarize=[],
        papers_to_index=[],
        vector_store_path=None, # Or path to a default/empty index
        index_needs_rebuild=False,
        user_preferences=None, # Or default preferences
        schedule_confirmation=None,
        last_error=None,
        status_message=None
        )
        st.session_state.state = initial_state
    
    # Initialize session state for messages if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add initial greeting
        greeting = "Hello! I'm your research assistant. What would you like to research today?"
        st.session_state.messages.append({"role": "assistant", "content": greeting})
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to research?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Process the message
        user_current_message = HumanMessage(content=prompt)
        current_graph_state = st.session_state.state
        current_graph_state["messages"].append(user_current_message)
        current_graph_state["current_user_request"] = prompt

        agent_response = app.invoke(current_graph_state)
        st.session_state.state = agent_response

        agent_response_messages = agent_response["messages"][-1]
        agent_response_content = agent_response_messages.content 

        with st.chat_message("assistant"):
            st.markdown(agent_response_content)
        
        st.session_state.messages.append({"role": "assistant", "content": agent_response_content})
