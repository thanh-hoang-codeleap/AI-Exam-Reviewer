from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

from ocr_pdf import ocr_pdf
from tool import mistakes_detect, process_output

# Initialize Flask app
app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Directory setup
UPLOAD_FOLDER = 'uploaded_files'
STATIC_DIR = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf'}

# Homepage route (serves index.html)
@app.route('/', methods=['GET'])
def home():
    return send_from_directory('.', 'index.html')

# Route for serving static files (CSS, JS, etc.)
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_DIR, path)

# Check if uploaded file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# File upload endpoint
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
        file.save(file_path)
        
        try:
            print("Running OCR...")
            text_file_path = ocr_pdf(file_path)

            # Read extracted text
            with open(text_file_path, "r") as text_file:
                text = text_file.read()
            
            print("Processing text...")
            # Detect mistakes in the extracted text 
            mistakes_1, mistakes_2 = mistakes_detect(text)
            print(f"First half: {mistakes_1}")
            print(f"Second half: {mistakes_2}")

            mistakes = process_output(mistakes_1, mistakes_2)

            # Save processed mistakes to JSON
            with open("mistakes.json", "w") as outfile:
                json.dump(mistakes, outfile)

            # with open("mistakes.json", "r") as file_json:
            #     data = json.load(file_json)
            
            return jsonify({
                "success": True,
                "filename": file.filename,
                "text": text,
            })
        
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    return jsonify({"success": False, "error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)