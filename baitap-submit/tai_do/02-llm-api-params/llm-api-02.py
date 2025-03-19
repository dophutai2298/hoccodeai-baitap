'''
Cải tiến ứng dụng chat: Sau mỗi câu hỏi và trả lời,
ta lưu vào array messages và tiếp tục gửi lên API để bot nhớ nội dung trò chuyện.
'''

from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    base_url=os.getenv('URL_TOGETHER'),
    api_key=os.getenv('API_KEY_TOGETHER')
)

messages = []
input_message = input('- Your question: ')
while input_message != "exit":
    messages.append({"role": "user", "content": input_message})

    response = client.chat.completions.create(
        model=os.getenv('MODEL'),
        messages=messages,
        stream=True
    )

    bot_reply = ""
    for chunk in response:
        bot_reply += chunk.choices[0].delta.content 

    messages.append({"role": "assistant", "content": bot_reply})

    print("- Bot: ",bot_reply)

    input_message = input('- Your question: ')

print("\n-- Goodbye! --")

