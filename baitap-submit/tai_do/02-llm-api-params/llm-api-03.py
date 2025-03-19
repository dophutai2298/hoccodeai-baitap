'''
Tóm tắt website. Dán link website vào console, bot sẽ tóm tắt lại nội dung của website đó.
Người dùng dán link https://tuoitre.vn/cac-nha-khoa-hoc-nga-bao-tu-manh-nhat-20-nam-sap-do-bo-trai-dat-2024051020334196.htm vào console
Sử dụng requests để lấy nội dung website.
Dùng thư viện beautifulsoup4 để parse HTML. (Bạn có thể hardcode lấy thông tin từ div có id là main-detail ở vnexpress)
Bạn cũng có thể thay bước 2-3 bằng cách dùng https://jina.ai/reader/, thên r.jina.ai để lấy nội dung website.
Viết prompt và gửi nội dung đã parse lên API để tóm tắt. (Xem lại bài prompt engineering nha!)
'''

from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

client = OpenAI(
    base_url=os.getenv('URL_TOGETHER'),
    api_key=os.getenv('API_KEY_TOGETHER')
)


def get_website_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_detail = soup.find("div",id='main-detail')
    if main_detail:
        paragraphs = main_detail.find_all("p")
        content = "\n".join([p.text for p in paragraphs])
        return content.strip()
    else:
        return "Not found."

messages = []
system_prompt = """
You are a Reader. Your task is to read the provided text and summarize the main content.
"""
input_message = input('- Link website: ')
website_content = get_website_content(input_message)

response = client.chat.completions.create(
    model=os.getenv('MODEL'),
    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": website_content}],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content or '', end='', flush=True)


print("\n-- Goodbye! --")

