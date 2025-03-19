'''
Dịch nguyên 1 file dài từ ngôn ngữ này sang ngôn ngữ khác.
Viết prompt để set giọng văn, v...v
Đọc từ file gốc, sau đó cắt ra thành từng phần để dịch vì LLM có context size có hạn
Sau khi dịch xong, gom kết quả lại, ghi vào file mới.
'''

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv('URL_TOGETHER'),
    api_key=os.getenv('API_KEY_TOGETHER')
)
system_prompt = """
You are a sophisticated AI translator proficient in a multitude of languages. 
Your primary function is to accurately and effectively translate text from a source language to a specified target language, maintaining the original meaning, context, 
and tone as closely as possible. Output only responds new language, not any other text.
"""

input_message = input('- Input text: ')

def split_text(text):
    lines = text.split('.')
    chunks = []
    for i in range(0, len(lines), 2):
        combined = ".".join(lines[i:i+2]) 
        chunks.append(combined.strip().replace("\n",""))
    return chunks


messages = [{"role": "system", "content": system_prompt}]
input_message = split_text(input_message)
translated_text = ""

for i in range(len(input_message)):
    messages.append({"role": "user", "content": input_message[i]})  
    response = client.chat.completions.create(
        model=os.getenv('MODEL'),
        messages=messages,
    )

    bot_reply = response.choices[0].message.content
    translated_text += bot_reply

print("Result: ", translated_text)

