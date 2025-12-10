import sys
import subprocess
import tempfile
import os
from io import BytesIO

# Check and install required packages
required_packages = ['flask', 'openai']
for package in required_packages:
    try:
        __import__(package)
        print(f"{package} is already installed")
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

from flask import Flask, request, render_template_string, send_file
import openai

app = Flask(__name__)

# Set your OpenAI API key here
openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Text to Speech</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; }
            form { border: 1px solid #ccc; padding: 20px; border-radius: 5px; }
            input, textarea { width: 100%; margin: 10px 0; padding: 8px; }
            button { background-color: #4CAF50; color: white; padding: 10px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Text to Speech Converter</h1>
        <form action="/convert" method="post" enctype="multipart/form-data">
            <label for="text_input">Enter text:</label><br>
            <textarea id="text_input" name="text_input" rows="5" placeholder="Or upload a file instead..."></textarea><br>
            
            <label for="text_file">Or upload a text file:</label><br>
            <input type="file" id="text_file" name="text_file" accept=".txt"><br>
            
            <label for="voice">Select voice:</label><br>
            <select id="voice" name="voice" style="width: 100%; padding: 8px;">
                <option value="alloy">Alloy</option>
                <option value="echo">Echo</option>
                <option value="fable">Fable</option>
                <option value="onyx">Onyx</option>
                <option value="nova">Nova</option>
                <option value="shimmer">Shimmer</option>
            </select><br>
            
            <button type="submit">Convert to Speech</button>
        </form>
    </body>
    </html>
    """)

@app.route("/convert", methods=["POST"])
def convert_to_speech():
    try:
        text_input = request.form.get("text_input", "").strip()
        text_file = request.files.get("text_file")
        voice = request.form.get("voice", "alloy")
        
        # Get text from input or file
        if text_file and text_file.filename != '':
            text_input = text_file.read().decode('utf-8')
        
        if not text_input:
            return render_template_string("""
                <h2>Error: No text provided</h2>
                <p>Please enter text or upload a file.</p>
                <a href="/">Go back</a>
            """)
        
        # Call OpenAI TTS API
        response = openai.Audio.create(
            model="tts-1",
            voice=voice,
            input=text_input
        )
        
        # Return audio file
        return send_file(
            BytesIO(response.content),
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="output.mp3"
        )
    
    except Exception as e:
        return render_template_string("""
            <h2>Error occurred during conversion:</h2>
            <p>{{ error }}</p>
            <a href="/">Go back</a>
        """, error=str(e))

if __name__ == "__main__":
    app.run(debug=True)