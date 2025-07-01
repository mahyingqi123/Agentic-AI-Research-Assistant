import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pathlib import Path
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

class RoutingAgent:
    def __init__(self):
        base_dir = Path(__file__).parent.parent
        env_path = base_dir / '.env'
        print(f"Loading environment variables from: {env_path}")
        load_dotenv(dotenv_path=env_path) # Load environment variables from .env file
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")  # Ensure this matches your .env file
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            google_api_key=GEMINI_API_KEY,
            temperature=0.7
        )
        self.VALID_INTENTS = [
            'discuss', 'qa', 'search', 'schedule', 'unknown'
        ]

        self.system_prompt = f"""You are an intent classification agent for a research assistant. Analyze the **last user message** in the provided conversation history. Classify the user's primary intent into one of the following categories ONLY:

            {self.VALID_INTENTS}

            Consider the immediate user request but also the last few turns for context. For example:
            - If the user intends to asks a question, classify as 'qa'.
            - If the user intends to dicuss about a resarch topic, classify as 'discuss'.
            - If the user intends to search and download research paper, classify as 'search'.
            - If the user intends to schedule a reading time table, classify as 'schedule'.
            - If unsure or ambiguous, classify as 'unknown'.

            Output *only* the single intent string corresponding to your classification (e.g., 'general_qa', 'discuss'). Do not add any explanation or other text.

            Conversation History (Last few messages):
            {{history}}

            Last User Message: {{last_user_message}}

            Intent:"""


    def run(self, messages: List[BaseMessage]) -> str:
        last_user_message_content = messages[-1].content
        
        history_context = messages[-5:-1] # Get up to 4 previous messages
        formatted_history = "\n".join([f"{type(m).__name__}: {m.content}" for m in history_context])
        if not formatted_history:
            formatted_history = "[Start of Conversation]"
        prompt = self.system_prompt.format(
            history=formatted_history,
            last_user_message=last_user_message_content
        )

        # Use a simple HumanMessage containing the formatted prompt
        llm_input_messages = [HumanMessage(content=prompt)]
        print(f"DEBUG: Invoking Intent LLM on: '{last_user_message_content}'")
        response = self.llm.invoke(llm_input_messages)
        detected_intent = response.content.strip().lower().replace("'", "").replace('"', '') # Clean output
        print(f"DEBUG: Raw intent from LLM: '{detected_intent}'")

        # Validate the response against our defined intents
        if detected_intent in self.VALID_INTENTS:
            return detected_intent
        else:
            print(f"WARNING: Detected intent '{detected_intent}' is not valid. Defaulting to 'unknown'.")
            return "unknown"

