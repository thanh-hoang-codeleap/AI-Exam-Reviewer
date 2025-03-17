import os
from pdf2image import convert_from_path
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

def ocr_pdf(file_path: str) -> str:
    # Convert PDF pages to images
    images = convert_from_path(file_path)

    # Initialize Azure ImageAnalysisClient
    client = ImageAnalysisClient(
        endpoint=os.getenv("END_POINT"),
        credential=AzureKeyCredential(os.getenv("API_KEY"))
    )
    visual_features =[
        VisualFeatures.READ,
    ]
    file_name = os.path.basename(file_path)[:-4].replace(" ", "_")
    output_file = f'extracted_texts/{file_name}.txt'
    if os.path.exists(output_file):
        os.remove(output_file)

    images_folder = f"images_from_pdf/{file_name}"
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    # Process each image (PDF page) for OCR
    for i, image in enumerate(images):
        image_path = f'{images_folder}/page_{i + 1}.png'
        image.save(image_path, 'PNG')

        with open(image_path, "rb") as f:
            image_data = f.read()

        try:
            print(f"Processing page {i + 1}...") 

            # Call Azure OCR API
            result = client.analyze(
                image_data=image_data,
                visual_features=visual_features,
                language="en"
            )

            if result.read is not None:
                print("Saving text...")
                with open(output_file, "a") as file:
                    for line in result.read.blocks[0].lines:
                        file.write(line.text)
                        file.write(" ")
                        #print(line.text)
                        # print(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
                        # for word in line.words:
                        #     print(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")
            print(f"Finish processing page {i + 1}")

        except HttpResponseError as e:
            print(f"Status code: {e.status_code}")
            print(f"Reason: {e.reason}")
            print(f"Message: {e.error.message}")
    return output_file