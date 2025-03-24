'''
1. Thay vì tự viết object `tools`, hãy xem lại bài trước, sửa code và dùng `inspect` và `TypeAdapter` để define `tools` hơn
2. Trong bài giảng, chúng ta đã define sẵn hàm `view_website`.
    - Tìm hiểu về [JinaAI](https://jina.ai/reader/?ref={{userIdReversed}})
    - Implement hàm `view_website`, sử dụng `requests` và JinaAI để đọc markdown từ URL

    ![jina](https://assets.hoccodeai.com/03.1-LLM-advanced/01-function-calling/imgs/jina-hint.jpg)
    - Dùng function calling để khi người dùng yêu cầu tóm tắt trang web, chạy hàm `view_website` để lấy markdown từ website về cho LLM tóm tắt
'''

import json
from openai import OpenAI
import os
from dotenv import load_dotenv
import inspect
from pydantic import TypeAdapter
import requests


load_dotenv()

def get_current_weather(location: str, unit: str='celsius'):
    """
    Get the current weather in a given location
    :param prompt: The parameters are the location to get the city name; the unit is Celsius or Fahrenheit, which is the temperature unit.
    :output: The temperature in the location input
    """
    format_location = location.lower().replace(" ", "")
    url_get_lat_lon = f"https://nominatim.openstreetmap.org/search?q={format_location}&format=json"
    headers = {"User-Agent": "Function-calling/1.0"} 

    response = requests.get(url_get_lat_lon, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            response_temperature = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={data[0]["lat"]}&longitude={data[0]["lon"]}&current_weather=true&temperature_unit={unit}')
            if response_temperature.status_code == 200:
                data_temp = response_temperature.json()
                get_temperature = data_temp.get("current_weather", {}).get("temperature")
                return f'Ở {location} có nhiệt độ là {get_temperature} {unit}'
    else:
        print(f"Lỗi {response.status_code}: {response.text}")
        return "Vị trí chưa chính xác"


def view_website(url: str):
    """
    Summarize website content through input url
    :param prompt: The parameter is URL to get content
    :output: All content is taken from URL
    """
    headers = {
    'Authorization': f'Bearer {os.getenv("AUTHORIZATION_JINA")}'
    }
    url_w_jina = f'https://r.jina.ai/{url}'
    response = requests.get(url_w_jina, headers=headers)
    if response.status_code != 200:
        print(f"Không thể truy cập {url}")
        return None
    return response.text



function_calling = {
    "current_weather_function" : {
        "name": "get_current_weather",
        "description": inspect.getdoc(get_current_weather),
        "parameters": TypeAdapter(get_current_weather).json_schema(),
    },
    "view_website_function" : {
        "name": "view_website",
        "description": inspect.getdoc(view_website),
        "parameters": TypeAdapter(view_website).json_schema(),
    },
}


tools = [
    {
        "type":"function",
        "function": function_calling['current_weather_function']
    },
      {
        "type":"function",
        "function": function_calling['view_website_function']
    }
]

client = OpenAI(
    base_url=os.getenv('URL_TOGETHER'),
    api_key=os.getenv('API_KEY_TOGETHER')
)

system_prompt = '''
You are a helpful assistant that can access external functions. 
The responses from these function calls will be appended to this dialogue. 
Please provide responses based on the information from these function calls.
You respond to the response of the function calls in a fun and humorous tone.
'''

function_list = {
    "get_current_weather": get_current_weather,
    "view_website": view_website
}

input_message = input('- Câu hỏi của bạn: ')

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": input_message}
]


response = client.chat.completions.create(
    model=os.getenv("MODEL_2"),
    messages=messages,
    tools=tools
)



tool_call = response.choices[0].message.tool_calls[0]
arguments = json.loads(tool_call.function.arguments)

if tool_call.function.name in function_list:
    function_to_call = function_list[tool_call.function.name]
    result = function_to_call(**arguments) 

    # Gửi kết quả lên cho LLM
    messages.append(response.choices[0].message)
    messages.append({
        "role": "tool",
        "content": result,
        "tool_call_id": tool_call.id
    })

    final_response = client.chat.completions.create(
        model=os.getenv("MODEL_2"),
        messages=messages
    )
    print(f"Bot reply: {final_response.choices[0].message.content}.")

