import streamlit as st
from openai import OpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import Dict, List, TypedDict, Literal
from templates import assistant_character
import os

# Define the state structure for our graph
class AgentState(TypedDict):
    messages: List[dict]
    next: str

api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# Initialize the OpenAI client
client = OpenAI()

# Create a model for responding to queries
def get_model():
    return OpenAI(
        model="gpt-3.5-turbo",
        temperature=1.2,
        max_tokens=500,
        streaming=True
    )

# Node functions for the graph
def greeting(state: AgentState) -> AgentState:
    """Initial greeting from the assistant"""
    greeting_text = """
    Hello there! I am your personal research assistant. Ask me anything related to your research. I can help you with:
    1. Finding research papers 
    2. Summarizing research papers
    3. Planning your research
    4. Creating reading schedules

    Let's get started!
    What would you like to research about? Please provide a topic or a question.
    """
    state["messages"].append({"role": "assistant", "content": greeting_text})
    state["next"] = "wait_for_input"
    return state

def process_input(state: AgentState) -> AgentState:
    """Process the user input and prepare for the response"""
    # Last message should be from the user
    last_message = state["messages"][-1]
    if last_message["role"] != "user":
        state["next"] = "wait_for_input"
        return state
    
    state["next"] = "generate_response"
    return state

def generate_response(state: AgentState) -> AgentState:
    """Generate a response based on the conversation history"""
    formatted_messages = []
    # Add system message first
    formatted_messages.append(SystemMessage(content=assistant_character.context))
    
    # Add all user and assistant messages
    for message in state["messages"]:
        if message["role"] == "user":
            formatted_messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            formatted_messages.append(AIMessage(content=message["content"]))
    
    # Generate a response (this will be used in Streamlit)
    # We're not actually calling the model here, just setting up for it
    state["next"] = "wait_for_input"
    return state

def router(state: AgentState) -> Literal["greeting", "process_input", "generate_response", "wait_for_input", END]:
    """Route to the appropriate node based on the state"""
    return state["next"]

# Create the graph
def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("greeting", greeting)
    workflow.add_node("process_input", process_input)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("wait_for_input", lambda x: x)  # Pass-through node
    
    # Add edges
    workflow.add_edge("greeting", "wait_for_input")
    workflow.add_edge("wait_for_input", "process_input")
    workflow.add_edge("process_input", "generate_response")
    workflow.add_edge("generate_response", "wait_for_input")
    
    # Set the entry point
    workflow.set_entry_point("greeting")
    
    # Compile the graph
    return workflow.compile()

# Streamlit app
def main():
    st.title("Your AI Research Assistant")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.graph_state = {"messages": [], "next": "greeting"}
        st.session_state.graph = create_graph()
        
        # Run greeting
        state = st.session_state.graph.invoke(st.session_state.graph_state)
        st.session_state.graph_state = state
        st.session_state.messages = state["messages"]
    
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] != "system":  # Don't display system messages
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me a research query!"):
        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.graph_state["messages"].append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process user input through the graph
        st.session_state.graph_state = st.session_state.graph.invoke(st.session_state.graph_state)
        
        # We need to actually generate the response here (not in the graph)
        with st.chat_message("assistant"):
            messages_for_model = [{"role": "system", "content": assistant_character.context}]
            for msg in st.session_state.messages:
                if msg["role"] in ["user", "assistant"]:
                    messages_for_model.append({"role": msg["role"], "content": msg["content"]})
            
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages_for_model,
                stream=True,
                max_tokens=500,
                temperature=1.2
            )
            response = st.write_stream(stream)
        
        # Add assistant response to state
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.graph_state["messages"].append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()