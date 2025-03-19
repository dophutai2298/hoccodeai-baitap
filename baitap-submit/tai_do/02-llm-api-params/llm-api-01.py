'''
Viết một ứng dụng console đơn giản, người dùng gõ câu hỏi vào console, bot trả lời và in ra. 
Có thể dùng stream hoặc non-stream.
'''

from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    base_url=os.getenv('URL_TOGETHER'),
    api_key=os.getenv('API_KEY_TOGETHER')
)

input_message = input('- Your question: ')

response = client.chat.completions.create(
    model=os.getenv('MODEL'),
    messages=[{"role": "user", "content": input_message}],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content or '', end='', flush=True)

