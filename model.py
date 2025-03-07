import torch
from PIL import Image
from pdf2image import convert_from_path
from transformers import AutoProcessor, AutoModelForCausalLM 

#image = Image.open("page_1.png")

images = convert_from_path("sample 5_languagepoint3_no comments.pdf")

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-large", torch_dtype=torch_dtype, trust_remote_code=True).to(device)
processor = AutoProcessor.from_pretrained("microsoft/Florence-2-large", trust_remote_code=True)

prompt = "<OCR>"

for i, image in enumerate(images):
    image.save(f'page_{i + 1}.png', 'PNG')
    input_image = Image.open(f"page_{i + 1}.png")

    print(f"Processing page {i+1}...")
    inputs = processor(text=prompt, images=input_image, return_tensors="pt").to(device, torch_dtype)

    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=4096,
        num_beams=3,
        do_sample=False
    )
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

    parsed_answer = processor.post_process_generation(generated_text, task="<OCR>", image_size=(input_image.width, input_image.height))

    if i == 0:
        with open("generated_text_5.txt", "w") as file:
            file.write(parsed_answer["<OCR>"])
    else:
        with open("generated_text_5.txt", "a") as file:
            file.write(parsed_answer["<OCR>"])

    print(f"Finish processing page {i + 1}")