from flask import Flask, request, jsonify, send_from_directory
import json
import os
from ocr_pdf import ocr_pdf

# Uncomment these when ready
#from ocr_pdf import ocr_pdf
#from tool import mistakes_detect

app = Flask(__name__, static_url_path='/static', static_folder='static')
UPLOAD_FOLDER = 'uploaded_files'
STATIC_DIR = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf'}

@app.route('/', methods=['GET'])
def home():
    return send_from_directory('.', 'index.html')

# Route for serving static files (CSS, JS, etc.)
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_DIR, path)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"})
    
    if file and allowed_file(file.filename):
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename.replace(" ", "_"))
        print(file_path)
        file.save(file_path)
        
        try:
            text_file_path = ocr_pdf(file_path)
            print(text_file_path)
            with open(text_file_path, "r") as text_file:
                content = text_file.read()
            text = content 
            
            # Detect mistakes in the extracted text (uncomment when ready)
            # mistakes = mistakes_detect(text)
            mistakes = ["sample mistake"] # Replace with actual mistake detection
            
            return jsonify({
                "success": True,
                "filename": file.filename,
                "text": text,
                "mistakes": mistakes
            })
        
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    return jsonify({"success": False, "error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)