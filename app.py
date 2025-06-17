from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import tempfile
import mimetypes

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure your Gemini API key
genai.configure(api_key="AIzaSyDYu6DB7LLRuVeyq8mXofVjaQ9R8Akgnrw")  # Replace with your actual API key

@app.route('/ask', methods=['POST'])
def ask_ai():
    question = request.form.get("question", "").strip()
    file = request.files.get("attachment")

    if not question and not file:
        return jsonify({"answer": "Please enter a question or attach a PDF file."}), 400

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        if file and file.filename != '':
            # Save the uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name

            try:
                # Upload the PDF to Gemini
                mime_type, _ = mimetypes.guess_type(file.filename)
                uploaded_file = genai.upload_file(path=temp_file_path, mime_type=mime_type)

                # Prepare the content for the model
                prompt = question if question else "Please summarize the contents of this PDF."
                response = model.generate_content([uploaded_file, prompt])
                return jsonify({"answer": response.text})
            finally:
                # Clean up the temporary file
                os.remove(temp_file_path)
        else:
            # Handle text-only questions
            response = model.generate_content([question])
            return jsonify({"answer": response.text})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=8000)
