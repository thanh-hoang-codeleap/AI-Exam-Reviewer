import requests
import json
from ocr_pdf import ocr_pdf
from tool import mistakes_detect

def main():
    file_path = "pdf_files/sample 5_languagepoint3_no comments.pdf"
    try:
        print("Extracting texts...")
        #text_file = ocr_pdf(file_path)
        text_file = "extracted_texts/sample_5_languagepoint3_no_comments.txt"
        with open(text_file, "r") as file_text:
            text = file_text.read()
        print("Reviewing texts...")
        mistakes = mistakes_detect(text)
        print("Result: ",mistakes)
        print("Saving result...")
        with open("mistakes.json", "w") as outfile:
            json.dump(mistakes, outfile)

    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    main()