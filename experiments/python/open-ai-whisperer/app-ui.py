import sys
import subprocess
import tempfile
import os

# Check and install required packages
required_packages = ['flask', 'openai-whisper']
for package in required_packages:
    try:
        if package == 'openai-whisper':
            import whisper
        else:
            __import__(package)
        print(f"{package} is already installed")
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

from flask import Flask, request, render_template_string
import whisper

app = Flask(__name__)
model = whisper.load_model("base")

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Audio Transcription</title>
    </head>
    <body>
        <h1>Audio Transcription Service</h1>
        <form action="/transcribe" method="post" enctype="multipart/form-data">
            <label for="audio">Select audio file:</label><br>
            <input type="file" id="audio" name="audio" accept="audio/*" required><br><br>
            <input type="submit" value="Transcribe">
        </form>
    </body>
    </html>
    """)

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        audio_file = request.files["audio"]
        if audio_file.filename == '':
            return {"error": "No file selected"}, 400
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as temp_file:
            audio_file.save(temp_file.name)
            
            # Transcribe the audio file
            result = model.transcribe(temp_file.name)
            
            # Clean up temporary file
            os.unlink(temp_file.name)
            
        return {"transcription": result["text"]}
    
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)