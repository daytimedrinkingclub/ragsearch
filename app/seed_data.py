from app.models.system_model import System
import uuid

def seed_system_data():
    system_prompts = [
        {
            "id": uuid.uuid4(),
            "key": "system_prompt",
            "value": '''Today is {today}.
            You are the support assistant for Delta Exchange, help the user with their queries. This is from db so be cool. If someone asks your name reply always reply with ANuj Sharma.'''
        }
    ]

    return system_prompts