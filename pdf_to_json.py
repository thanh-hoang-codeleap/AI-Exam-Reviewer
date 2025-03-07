from pdf2image import convert_from_path

images = convert_from_path("sample1_bad hand writing_Languagepoint_3 (anonym)_no comments.pdf")

for i, image in enumerate(images):
    image.save(f'page_{i + 1}.png', 'PNG')