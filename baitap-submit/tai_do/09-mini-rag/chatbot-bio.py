# 1. Dùng chunking để làm bot trả lời tiểu sử người nổi tiếng, anime v...v
#   - <https://en.wikipedia.org/wiki/S%C6%A1n_T%C3%B9ng_M-TP>
#   - <https://en.wikipedia.org/wiki/Jujutsu_Kaisen>
from wikipediaapi import Wikipedia
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os

load_dotenv()
COLLECTION_NAME = "bio-collection"
client = chromadb.PersistentClient(path="./data")
client.heartbeat()

embedding_function = embedding_functions.DefaultEmbeddingFunction()

# Get a list of collection names (directly as strings)
existing_collections = client.list_collections()

# Check if the collection already exists
if COLLECTION_NAME in existing_collections:
    collection = client.get_collection(name=COLLECTION_NAME,
        embedding_function=embedding_function)
else:
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )

def get_wikipedia_doc(title: str, lang: str = 'en'):
    """Fetches Wikipedia content and stores it in the collection."""
    wiki = Wikipedia('HocCodeAI/0.0 (https://hoccodeai.com)', lang)
    page = wiki.page(title)

    if not page.exists():
        print(f"Error: Wikipedia page '{title}' not found.")
        return

    doc = page.text
    paragraphs = doc.split('\n\n')

    # Store paragraphs in the global collection
    for index, paragraph in enumerate(paragraphs):
        collection.add(documents=[paragraph], ids=[str(index)])

print("Welcome to the Wikipedia Bot! Ask me any topics such as Sơn Tùng M-TP, Jujutsu Kaisen, ...")
title = input("Enter Wikipedia page title: ")
get_wikipedia_doc(title)

while True:

    query =  input("Enter your question: ")

    if query.lower() == "exit":
        print("Exiting the bot. Goodbye!")
        break

    q = collection.query(query_texts=[query], n_results=3)
    CONTEXT = q["documents"][0]

    prompt = f"""
    Use the following CONTEXT to answer the QUESTION at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use an unbiased and journalistic tone.

    CONTEXT: {CONTEXT}

    QUESTION: {query}
    """

    client = OpenAI(
    base_url=os.getenv('URL_TOGETHER'),
    api_key=os.getenv('API_KEY_TOGETHER')
    )

    response = client.chat.completions.create(
        model=os.getenv("MODEL_2"),
        messages=[
            {"role": "user", "content": prompt},
        ]
    )

    print(f"Bot: {response.choices[0].message.content}")