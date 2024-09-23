# Folder structure for the RAG chat app

```bash
ragbot/
    - app/
        - __init__.py
        - routes/
            - __init__.py
            - article_routes.py # all the routes for the app
            - chat_routes.py # all the routes for the app
        - models/
            - __init__.py
            - embeddings_model.py # the model which will store the embeddings response and articles in the database
            - chat_model.py # the model which will store the chat history and user chats
        - services/
            - __init__.py
            - embedding_upsert.py # function to insert embeddings into pinecone
            - embeddings_generator.py # function to generate embeddings using openai
            - embeddings_search.py # function to search for embeddings in pinecone
    - run.py # the main file to run the app
    - config.py # the config file to store the config variables
    - extensions.py # the extensions file to store the extensions for the app
    - requirements.txt # the requirements file to store the dependencies for the app
    - .env
    - .gitignore
```