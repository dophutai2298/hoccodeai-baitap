'''
Hãy viết 1 ứng dụng console:
- Nhận đầu vào là 1 prompt, chiều ngang, chiều cao của ảnh.
- Sử dụng `DiffusionPipeline` để tạo hình ảnh từ prompt đó và lưu vào máy nha!
'''

from diffusers import DiffusionPipeline
import torch


pipeline = DiffusionPipeline.from_pretrained("sd-legacy/stable-diffusion-v1-5",
use_safetensors=True,
safety_checker=None,
requires_safety_checker=False,
torch_dtype=torch.float16,
)

device = "cuda" if torch.cuda.is_available() else "cuda"
pipeline.to(device)

prompt = input('- Describe your image: ')
while prompt != "exit":
    width = input('- Width of your image: ')
    height = input('- Height of your image: ')
    if int(width) % 8 == 0 and int(height) % 8 == 0:
        image = pipeline(prompt=prompt,num_inference_steps=20,
        width=int(width),
        height=int(height)).images[0]
        image.show() 
        image.save("output.png")
        prompt = input('\n- Describe your image: ')
    else:
        print("\n Width and Height have to be divisible by 8 ")