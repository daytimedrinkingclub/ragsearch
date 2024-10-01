import os
import anthropic
import json
from .embeddings_search import search_articles
from .external_tools import check_deposit_status
from .data_service import DataService
from .context_service import ContextService
from typing import List, Dict, Any
from datetime import datetime
from app.models.system_model import System
from extensions import db

client = anthropic.Client()

MODEL_NAME = "claude-3-opus-20240229"

class AnthropicChat:

    def __init__(self):
        self.client = anthropic.Anthropic()

    def get_system_prompt(self):
        system_prompt = System.query.filter_by(key='system_prompt').first()
        if system_prompt:
            today = datetime.now().strftime("%Y-%m-%d")
            return system_prompt.value.format(today=today)
        else:
            # Default prompt if not found in the database
            return "You are a helpful assistant."

    def chat(self, messages):
        system_prompt = self.get_system_prompt()
        
        formatted_messages = [
            {"role": "system", "content": system_prompt},
            *[{"role": msg.role, "content": msg.content} for msg in messages]
        ]

        response = self.client.messages.create(
            model="claude-3-opus-20240229",
            messages=formatted_messages,
            max_tokens=1000,
        )

        return response.content[0].text

    @staticmethod
    def process_tool_call(tool_name, tool_input, tool_use_id, chat_id):
        if tool_name == "search_articles":
            print(f"Searching articles for: {tool_input['query_to_search']}")
            results = search_articles(tool_input["query_to_search"])
            return results
        elif tool_name == "check_deposit_status":
            print(f"Checking deposit status for: {tool_input['transfer_number']}")
            results = check_deposit_status(tool_input["transfer_number"])
            return results
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
        
        # Fetch the system prompt from the database
        system_prompt = System.query.filter_by(key='system_prompt').first()
        if system_prompt:
            today = datetime.now().strftime("%Y-%m-%d")
            system_message = system_prompt.value.format(today=today)
        else:
            # Default prompt if not found in the database
            system_message = "You are a helpful assistant."
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0,
            system=system_message,
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
            DataService.save_message(chat_id, "user", content=json.dumps(tool_result), tool_use_id=tool_use.id, tool_use_input=tool_use.input, tool_name=tool_use.name, tool_result=json.dumps(tool_result))
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