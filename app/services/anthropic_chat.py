import os
import anthropic
import json
from .embeddings_search import search_articles
from .external_tools import check_deposit_status, get_wallet_details
from .data_service import DataService
from .context_service import ContextService
from typing import List, Dict, Any
from datetime import datetime
from app.models.system_model import System
from extensions import db
from config import Config
from flask import current_app

client = anthropic.Client()

class AnthropicChat:

    def __init__(self):
        self.client = anthropic.Anthropic()
    
    @staticmethod
    def get_system_prompt(conversation_category):
        system_prompt = System.query.filter_by(key=conversation_category).first()
        if system_prompt:
            today = datetime.now().strftime("%Y-%m-%d")
            return system_prompt.value.format(today=today)
        else:
            # Default prompt if not found in the database
            return "You are a helpful assistant."


    @staticmethod
    def process_tool_call(tool_name, tool_input, tool_use_id, chat_id, auth_token):
        if tool_name == "search_articles":
            current_app.logger.debug(f"Searching articles for: {tool_input['query_to_search']}")
            results = search_articles(tool_input["query_to_search"])
            return results
        elif tool_name == "check_deposit_status":
            current_app.logger.debug(f"Checking deposit status for: {tool_input['transfer_number']}")
            results = check_deposit_status(tool_input["transfer_number"], auth_token)
            return results
        elif tool_name == "get_wallet_details":
            results = get_wallet_details(auth_token)
            return results
        else:
            raise ValueError(f"Unsupported tool: {tool_name}")
    
    @staticmethod
    def load_tools():
        tools_path = os.path.join(os.path.dirname(__file__), 'tools', 'tools.json')
        with open(tools_path, 'r') as f:
            return json.load(f)
        
    @staticmethod
    def process_conversation(chat_id: str, conversation_category: str, auth_token: str) -> List[Dict[str, Any]]:
        tools = AnthropicChat.load_tools()
        conversation = ContextService.build_context(chat_id)
        
        # Fetch the system prompt from the database
        system_prompt = AnthropicChat.get_system_prompt(conversation_category)

        response = client.messages.create(
            model=Config.ANTHROPIC_MODEL,
            max_tokens=1000,
            temperature=0,
            system=system_prompt,
            tools=tools,
            messages=conversation,
        )
        current_app.logger.debug(f"Response Received from ANTHROPIC API: {response}")

        if response.stop_reason != "tool_use":
            # No tool use, return the final response
            DataService.save_message(chat_id, "assistant", content=response.content[0].text)
            return response

        # Handle tool use
        tool_use = next(block for block in response.content if block.type == "tool_use")
        
        content = response.content[0].text if response.content and response.content[0].type == "text" else None

        DataService.save_message(chat_id, "assistant", content=content, tool_use_id=tool_use.id, tool_use_input=tool_use.input, tool_name=tool_use.name)
        tool_result = AnthropicChat.process_tool_call(tool_use.name, tool_use.input, tool_use.id, chat_id, auth_token)

        if tool_result:
            # If a tool result is received, build the latest context and call process_conversation again
            DataService.save_message(chat_id, "user", content=json.dumps(tool_result), tool_use_id=tool_use.id, tool_use_input=tool_use.input, tool_name=tool_use.name, tool_result=json.dumps(tool_result))
            conversation = ContextService.build_context(chat_id)
            return AnthropicChat.process_conversation(chat_id, conversation_category, auth_token)

        return response

    @staticmethod
    def handle_chat(chat_id, message, conversation_category='general', external_id=None, auth_token=None):
        if external_id:
            chat = DataService.get_or_create_chat(external_id)
            chat_id = chat.id
        else:
            chat = DataService.get_chat_by_id(chat_id)
            if not chat:
                chat_id = DataService.create_chat()
        
        DataService.save_message(chat_id, "user", content=message)
        # Process the conversation
        response = AnthropicChat.process_conversation(chat_id, conversation_category, auth_token)
        # Extract the text content from the response
        return response