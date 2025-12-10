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
            return render_template_string("""
                <h2>Error: No file selected</h2>
                <a href="/">Go back</a>
            """)
        
        # Create temporary file and save audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1])
        temp_file_path = temp_file.name
        temp_file.close()  # Close the file before saving to it
        
        audio_file.save(temp_file_path)
        
        # Transcribe the audio file
        result = model.transcribe(temp_file_path)
        transcription = result["text"]
        
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass  # Ignore cleanup errors
        
        # Return HTML page with transcription
        return render_template_string("""
            <html>
            <head><title>Transcription Result</title></head>
            <body>
                <h2>Transcription Result:</h2>
                <p style="border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9;">
                    {{ transcription }}
                </p>
                <a href="/">Transcribe another file</a>
            </body>
            </html>
        """, transcription=transcription)
    
    except Exception as e:
        return render_template_string("""
            <h2>Error occurred during transcription:</h2>
            <p>{{ error }}</p>
            <a href="/">Go back</a>
        """, error=str(e))

if __name__ == "__main__":
    app.run(debug=True)