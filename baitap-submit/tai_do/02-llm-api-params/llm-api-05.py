'''
Dùng bot để... giải bài tập lập trình. Viết ứng dụng console cho phép bạn đưa câu hỏi vào, bot sẽ viết code Python/JavaScript. 
Sau đó, viết code lưu đáp án vào file final.py và chạy thử. (Dùng Python sẽ dễ hơn JavaScript nhé!)
'''
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
import re

client = OpenAI(
    base_url=os.getenv('URL_TOGETHER'),
    api_key=os.getenv('API_KEY_TOGETHER')
)

system_prompt = """
You are a technical leader who specializes in evaluating and solving programming problems using Python code.
Your task is to carefully analyze a given input document containing exercises.
Your goal is to generate Python code based on the input, refactor it to be clear and maintainable, add comments to explain the functionality of the code, 
and provide detailed explanations of each area of ​​the code. The output only code and format 
```python 
<code> 
```
"""

def clean_code_block(text):
    cleaned_text = re.sub(r'```(?:python)?\s*([\s\S]*?)\s*```', r'\1', text).strip()
    return cleaned_text

messages = [{"role": "system", "content": system_prompt}]
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
    input_file_name = input('- File name: ')
    with open(f"{input_file_name}.py", "w") as f:
        f.write(clean_code_block(bot_reply))
    input_message = input('- Your next question: ')

print("\n-- Goodbye! --")