# 2. Thay vì hardcode `doc = wiki.page('Hayao_Miyazaki').text`, sử dụng function calling để:
#   - Lấy thông tin cần tìm từ câu hỏi
#   - Dùng `wiki.page` để lấy thông tin về
#   - Sử dụng RAG để có kết quả trả lời đúng.
from wikipediaapi import Wikipedia
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os
import inspect
import json
from pydantic import TypeAdapter
import gradio as gr

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
    """
    Retrieve the specified Wikipedia page for using the library wikipediaapi by get title page
    :param title: The name of the page for which to retrieve the Wikipedia page,, e.g., 'Hồ Chí Minh'.
    :output: All detail content of this title in Wikipedia  get by library wikipediaapi
    """
    wiki = Wikipedia('HocCodeAI/0.0 (https://hoccodeai.com)', lang)
    page = wiki.page(title)

    if not page.exists():
        return f"Error: Wikipedia page '{title}' not found."

    doc = page.text
    # Split the document into paragraphs
    paragraphs = doc.split('\n\n')
    return paragraphs


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_wikipedia_doc",
            "description": inspect.getdoc(get_wikipedia_doc),
            "parameters": TypeAdapter(get_wikipedia_doc).json_schema(),
        },
    }
]


FUNCTION_MAP = {
    "get_wikipedia_doc": get_wikipedia_doc
}


system_prompt = '''
You are a helpful assistant that can access external functions. 
The responses from these function calls will be appended to this dialogue. 
Please provide responses based on the information from these function calls.
You respond to the function call responses in a fun and humorous tone and reply according to the input language.
'''

messages = [
    { "role": "system", "content": system_prompt }
]

client = OpenAI(
    base_url=os.getenv('URL_TOGETHER'),
    api_key=os.getenv('API_KEY_TOGETHER')
)


def get_completion(messages):
    response = client.chat.completions.create(
        model=os.getenv("MODEL_3"),
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.2
    )
    return response



def chat_logic(message, chat_history):
    messages = [
        { "role": "system", "content": system_prompt }
    ]

    for user_message, bot_message in chat_history:
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": bot_message})

    messages.append({"role": "user", "content": message})

    response = get_completion(messages)
    
    bot_message = response.choices[0].message.content

    if (bot_message is not None):
        chat_history.append((message, bot_message))
        yield "",chat_history

    else:
        # Call the function to get the Wikipedia document
        first_choice = response.choices[0]
        tool_call = first_choice.message.tool_calls[0]

        tool_call_function = tool_call.function
        tool_call_arguments = json.loads(tool_call_function.arguments)

        tool_function = FUNCTION_MAP[tool_call_function.name]
        result = tool_function(**tool_call_arguments)

        # Store paragraphs in the global collection
        for index, paragraph in enumerate(result):
            collection.add(documents=[paragraph], ids=[str(index)])
        

        q = collection.query(query_texts=[message], n_results=3)
        CONTEXT = q["documents"][0]

        prompt = f"""
        Use the following CONTEXT to answer the QUESTION at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Use an unbiased and journalistic tone.

        CONTEXT: {CONTEXT}

        QUESTION: {message}
        """

        messages.append(first_choice.message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call_function.name,
            "content": prompt
        })


        final_response = client.chat.completions.create(
        model=os.getenv("MODEL_3"),
        messages=messages
        )
        print(f"-  Bot: {final_response.choices[0].message.content}.")
        chat_history.append([message,final_response.choices[0].message.content])
        yield "", chat_history

    return "", chat_history


with gr.Blocks() as demo:
    gr.Markdown("# Chatbot smart Wikipedia ^^")
    message = gr.Textbox(label="Do you have any question:")
    chatbot = gr.Chatbot(label="Chat Bot", height=700)
    message.submit(chat_logic, [message, chatbot], [message, chatbot])

demo.launch()

'''
while True:
    question = input("Enter your question: ")
    if question.lower() == "exit":
        print("Exiting the bot. Goodbye!")
        break

    messages.append({"role": "user", "content": question})
    response = get_completion(messages)
    first_choice = response.choices[0]
    finish_reason = first_choice.finish_reason

    tool_call = first_choice.message.tool_calls[0]

    tool_call_function = tool_call.function
    tool_call_arguments = json.loads(tool_call_function.arguments)

    tool_function = FUNCTION_MAP[tool_call_function.name]
    result = tool_function(**tool_call_arguments)

    # Store paragraphs in the global collection
    for index, paragraph in enumerate(result):
        collection.add(documents=[paragraph], ids=[str(index)])


    q = collection.query(query_texts=[question], n_results=3)
    CONTEXT = q["documents"][0]

    prompt = f"""
    Use the following CONTEXT to answer the QUESTION at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use an unbiased and journalistic tone.

    CONTEXT: {CONTEXT}

    QUESTION: {question}
    """

    response = client.chat.completions.create(
        model=os.getenv("MODEL_2"),
        messages=[
            {"role": "user", "content": prompt},
        ]
    )

    print(f"Bot: {response.choices[0].message.content}.")

'''





