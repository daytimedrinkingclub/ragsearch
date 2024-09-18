import anthropic
import json
from .embeddings_search import search_articles
from .data_service import DataService
from .context_service import ContextService
from typing import List, Dict, Any

client = anthropic.Client()

MODEL_NAME = "claude-3-opus-20240229"



def process_tool_call(tool_name, tool_input, tool_use_id, chat_id):
    if tool_name == "search_articles":
        return search_articles(tool_input["query_to_search"], tool_use_id, chat_id)
    else:
        raise ValueError(f"Unsupported tool: {tool_name}")

class AnthropicChat:

    @staticmethod
    def process_conversation(chat_id: str) -> List[Dict[str, Any]]:
        tools = [
                    {
                        "name": "search_articles",
                        "description": "Searches the database for the most relevant support articles, this will search and return the top 3 relevant articles which will help in responding to the user query",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "query_to_search": {
                                    "type": "string",
                                    "description": "The query that needs to be searched for the article database needs to be passed here."
                                }
                            },
                            "required": ["query_to_search"]
                        }
                    }
            ]
        conversation = ContextService.build_context(chat_id)
        print(f"process_conversation started with {chat_id} with current context_len: {len(conversation)}")
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            temperature=0,
            system=
            """
            Today is {today}.\n
            You are tasked to help the user with their research tasks for ai tools. Always let the user know the list of tools available
            """,
            tools=tools,
            # tool_choice={"type": "auto"},
            messages=conversation,
        )
        print(f"Response Received from ANTHROPIC API: {response}")

        if response.stop_reason != "tool_use":
            # No tool use, return the final response
            print(f"No tool use, returning assistant response which needs a user message")
            DataService.save_message(chat_id, "assistant", content=response.content[0].text)
            return response

        # Handle tool use
        print(f"Tool use detected, processing tool use")
        tool_use = next(block for block in response.content if block.type == "tool_use")

        print(f"Tool Name: {tool_use.name}")
        
        content = response.content[0].text if response.content and response.content[0].type == "text" else None
        DataService.save_message(chat_id, "assistant", content=content, tool_use_id=tool_use.id, tool_use_input=tool_use.input, tool_name=tool_use.name)

        tool_result = process_tool_call(tool_use.name, tool_use.input, tool_use.id, chat_id)

        print(f"Tool Result received: {tool_result}")

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