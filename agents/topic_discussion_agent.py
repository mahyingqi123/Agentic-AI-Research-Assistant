from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict, Tuple
import os
from dotenv import load_dotenv
from pathlib import Path

import json



class TopicDiscussionAgent:
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
        
        self.system_prompt = """You are an expert research topic discussion agent. Your role is to help users refine their research ideas 
        through interactive discussion. Follow these guidelines:

        1. Ask clarifying questions to understand:
           - The user's research goals and objectives
           - Their field of study and expertise levelI
           - Any specific aspects they want to focus on
           - Potential constraints or requirements

        2. Suggest improvements to their research questions by:
           - Making them more specific and focused
           - Ensuring they are researchable and measurable
           - Identifying potential gaps or areas for exploration
           - Considering interdisciplinary connections

        3. Help identify subtopics by:
           - Breaking down the main topic into manageable components
           - Suggesting related areas that might be relevant
           - Identifying emerging trends or gaps in the field
           - Considering different perspectives or approaches

        Format your response as a JSON object with the following structure:
        {
            "refined_question": "The improved research question",
            "subtopics": ["List of relevant subtopics"],
            "suggestions": ["List of specific suggestions for improvement"],
            "follow_up_questions": ["Questions to ask the user for clarification"]
        }
        """
        
    def _parse_response(self, response: str):
        """Parse the LLM response JSON."""
        response = response.strip().replace("```json", "").replace("```", "").strip() # Clean potential markdown

        parsed = json.loads(response)
        refined = parsed.get("refined_question")
        subtopics = parsed.get("subtopics")
        suggestions = parsed.get("suggestions")
        follow_up = parsed.get("follow_up_questions")
        # Ensure list types where expected
        if subtopics is not None and not isinstance(subtopics, list): subtopics = [str(subtopics)]
        if suggestions is not None and not isinstance(suggestions, list): suggestions = [str(suggestions)]
        if follow_up is not None and not isinstance(follow_up, list): follow_up = [str(follow_up)]

        return refined, subtopics, suggestions, follow_up


    def run(self, messages: List[dict]) -> Tuple[str, List[str]]:
        """
        Process the conversation and extract refined research question and subtopics.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Tuple containing:
            - refined_question: The improved research question
            - subtopics: List of relevant subtopics to explore
        """
        conversation = [
            SystemMessage(content=self.system_prompt)] + messages
        # Get response from LLM
        response = self.llm.invoke(conversation)
        
        # Parse and return the structured response
        print(f"DEBUG: LLM Response: {response.content}")
        refined_q, subtopics, suggestions, follow_up = self._parse_response(response.content)

        ai_response_text = "Okay, let's continue refining your topic." # Default
        if follow_up:
             ai_response_text = "\n".join(follow_up)
        elif suggestions:
             ai_response_text = "Here are some suggestions:\n" + "\n".join(f"- {s}" for s in suggestions)
        elif refined_q:
             ai_response_text = f"Based on our discussion, how about this refined question: {refined_q}"


        return {
            "refined_question": refined_q,
            "subtopics": subtopics,
            "suggestions": suggestions, # Pass suggestions through
            "follow_up_questions": follow_up, # Pass follow-up Qs through
            "ai_message_content": ai_response_text # Content for the AIMessage to be added to history
        }

    def get_follow_up_questions(self, messages: List[dict]) -> List[str]:
        """
        Generate follow-up questions based on the conversation history.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            List of follow-up questions to ask the user
        """
        follow_up_prompt = """Based on the conversation so far, generate 3-5 relevant follow-up questions 
        to help clarify and refine the research topic. Focus on:
        1. Understanding the user's specific goals
        2. Identifying potential research gaps
        3. Clarifying the scope of the research
        4. Understanding the user's expertise level
        5. Identifying any constraints or requirements
        
        Format the response as a JSON array of questions."""
        
        conversation = [SystemMessage(content=follow_up_prompt)] + messages

        response = self.llm.invoke(conversation)
        response_content = response.content.strip().replace("```json", "").replace("```", "").strip()

        parsed_questions = json.loads(response_content)
        if isinstance(parsed_questions, list):
                # Ensure all items are strings
                return [str(q) for q in parsed_questions]
        else:
                return ["Could not parse follow-up questions correctly (not a list)."]

