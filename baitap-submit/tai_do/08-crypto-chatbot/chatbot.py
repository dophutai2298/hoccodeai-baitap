'''
Hiện tại, chúng ta đang hardcode câu hỏi vào biến `question` trong code. Do đó, nó chỉ chạy 1 lần rồi ngừng.

Các bạn có thể biến nó thành 1 app hoàn chỉnh bằng các bước sau:

1. Bỏ tất cả vào vòng lặp while True.
2. Sau đó đọc câu hỏi từ phía người dùng bằng hàm `input` của Python `question = input("Có câu hỏi gì về không bạn ơi: ")`
3. Lần lượt add câu hỏi của người dùng và câu trả lời của bot vào `messages` để bot nhớ ngữ cảnh
4. Có thể update system prompt để LLM trả lời hài hước và vui tính hơn.

Bạn sẽ làm ra được con bot như hình dưới.

![demo](https://assets.hoccodeai.com/03.1-LLM-advanced/01-function-calling/imgs/stock-demo.webp)
'''

from dotenv import load_dotenv
from openai import OpenAI
import os
import inspect
from pydantic import TypeAdapter
import requests
import yfinance as yf
import json
import gradio as gr

def get_symbol(company: str) -> str:
    """
    Retrieve the stock symbol for a specified company using the Yahoo Finance API.
    :param company: The name of the company for which to retrieve the stock symbol, e.g., 'Nvidia'.
    :output: The stock symbol for the specified company.
    """
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": company, "country": "United States"}
    user_agents = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    res = requests.get(
        url=url,
        params=params,
        headers=user_agents)

    data = res.json()
    symbol = data['quotes'][0]['symbol']
    return symbol


def get_stock_price(symbol: str):
    """
    Retrieve the most recent stock price data for a specified company using the Yahoo Finance API via the yfinance Python library.
    :param symbol: The stock symbol for which to retrieve data, e.g., 'NVDA' for Nvidia.
    :output: A dictionary containing the most recent stock price data.
    """
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d", interval="1m")
    latest = hist.iloc[-1]
    return {
        "timestamp": str(latest.name),
        "open": latest["Open"],
        "high": latest["High"],
        "low": latest["Low"],
        "close": latest["Close"],
        "volume": latest["Volume"]
    }


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_symbol",
            "description": inspect.getdoc(get_symbol),
            "parameters": TypeAdapter(get_symbol).json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": inspect.getdoc(get_stock_price),
            "parameters": TypeAdapter(get_stock_price).json_schema(),
        },
    }
]

FUNCTION_MAP = {
    "get_symbol": get_symbol,
    "get_stock_price": get_stock_price
}


load_dotenv()
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


# Bắt đầu làm bài tập từ line này!

system_prompt = '''
You are a helpful assistant that can access external functions. 
The responses from these function calls will be appended to this dialogue. 
Please provide responses based on the information from these function calls.
You respond to the function call responses in a fun and humorous tone and reply according to the input language.
'''


def chat_logic(message, chat_history):
    messages = [
        { "role": "system", "content": system_prompt }
    ]
    for user_message, bot_message in chat_history:
        if user_message is not None:
            messages.append({"role": "user", "content": user_message})
            messages.append({"role": "assistant", "content": bot_message})

    # Thêm tin nhắn mới của user vào cuối cùng
    messages.append({"role": "user", "content": message})

    # Gọi API của OpenAI
    response = get_completion(messages)

    bot_message = response.choices[0].message.content
    if (bot_message is not None):
        chat_history.append([message, bot_message])
        yield "", chat_history
    else:
        first_choice = response.choices[0]
        finish_reason = first_choice.finish_reason
        while finish_reason != "stop":
            tool_call = first_choice.message.tool_calls[0]

            tool_call_function = tool_call.function
            tool_call_arguments = json.loads(tool_call_function.arguments)

            tool_function = FUNCTION_MAP[tool_call_function.name]
            result = tool_function(**tool_call_arguments)

            messages.append(first_choice.message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call_function.name,
                "content": json.dumps({"result": result})
            })

            # print("messages: ", messages)

            # Chờ kết quả từ LLM
            response = get_completion(messages)
            first_choice = response.choices[0]
            finish_reason = first_choice.finish_reason
            chat_history.append([message,first_choice.message.content])

        yield "", chat_history

    return "", chat_history



with gr.Blocks() as demo:
    gr.Markdown("# Chatbot thông minh bình thường thôi ^^")
    message = gr.Textbox(label="Có câu hỏi gì về không bạn ơi:")
    chatbot = gr.Chatbot(label="Chat Bot", height=600)
    message.submit(chat_logic, [message, chatbot], [message, chatbot])

demo.launch()

''' 
question = input("Có câu hỏi gì về không bạn ơi: ")
while question != "exit":
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    response = get_completion(messages)
    first_choice = response.choices[0]
    finish_reason = first_choice.finish_reason
    # Loop cho tới khi model báo stop và đưa ra kết quả
    while finish_reason != "stop":
        tool_call = first_choice.message.tool_calls[0]

        tool_call_function = tool_call.function
        tool_call_arguments = json.loads(tool_call_function.arguments)

        tool_function = FUNCTION_MAP[tool_call_function.name]
        result = tool_function(**tool_call_arguments)

        messages.append(first_choice.message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call_function.name,
            "content": json.dumps({"result": result})
        })

        # print("messages: ", messages)

        # Chờ kết quả từ LLM
        response = get_completion(messages)
        first_choice = response.choices[0]
        finish_reason = first_choice.finish_reason

    # In ra kết quả sau khi đã thoát khỏi vòng lặp
    print("Bot reply: ",first_choice.message.content)
    question = input("Có câu hỏi gì về không bạn ơi: ")
'''