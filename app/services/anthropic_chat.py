import os
import anthropic
import json
from .embeddings_search import search_articles
from .data_service import DataService
from .context_service import ContextService
from typing import List, Dict, Any
from datetime import datetime
client = anthropic.Client()

MODEL_NAME = "claude-3-opus-20240229"

class AnthropicChat:

    @staticmethod
    def process_tool_call(tool_name, tool_input, tool_use_id, chat_id):
        if tool_name == "search_articles":
            print(f"Searching articles for: {tool_input['query_to_search']}")
            return search_articles(tool_input["query_to_search"], tool_use_id, chat_id)
        else:
            raise ValueError(f"Unsupported tool: {tool_name}")
    
    @staticmethod
    def load_tools():
        tools_path = os.path.join(os.path.dirname(__file__), 'tools', 'tools.json')
        with open(tools_path, 'r') as f:
            return json.load(f)
        
    @staticmethod
    def process_conversation(chat_id: str) -> List[Dict[str, Any]]:
        tools = AnthropicChat.load_tools()
        conversation = ContextService.build_context(chat_id)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0,
            system=
            """
            Today is {today}.\n
            You are the support assistant for Delta Exchange, help the user with their queries.
            """,
            tools=tools,
            messages=conversation,
        )
        print(f"Response Received from ANTHROPIC API: {response}")

        if response.stop_reason != "tool_use":
            # No tool use, return the final response
            DataService.save_message(chat_id, "assistant", content=response.content[0].text)
            return response

        # Handle tool use
        tool_use = next(block for block in response.content if block.type == "tool_use")

        
        content = response.content[0].text if response.content and response.content[0].type == "text" else None
        DataService.save_message(chat_id, "assistant", content=content, tool_use_id=tool_use.id, tool_use_input=tool_use.input, tool_name=tool_use.name)

        tool_result = AnthropicChat.process_tool_call(tool_use.name, tool_use.input, tool_use.id, chat_id)


        if tool_result:
            # If a tool result is received, build the latest context and call process_conversation again
            conversation = ContextService.build_context(chat_id)
            return AnthropicChat.process_conversation(chat_id)

        return response

    @staticmethod
    def handle_chat(chat_id: str, user_message: str) -> str:
        DataService.save_message(chat_id, "user", content=user_message)
        # Process the conversation
        response = AnthropicChat.process_conversation(chat_id)
        # Extract the text content from the response
        return response