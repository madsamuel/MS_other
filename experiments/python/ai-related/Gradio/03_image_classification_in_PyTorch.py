import torch
import requests
from PIL import Image

# Import transforms first to avoid circular import
try:
    from torchvision import transforms
    print("Successfully imported transforms")
except Exception as e:
    print(f"Error importing transforms: {e}")
    raise

# Try to load model with better error handling
model = None
try:
    model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=True).eval()
    print("Successfully loaded model from PyTorch Hub")
except Exception as hub_error:
    print(f"Failed to load from hub: {hub_error}")
    try:
        # Import models separately and carefully
        import torchvision.models as models
        model = models.resnet18(pretrained=True).eval()
        print("Successfully loaded model from torchvision.models")
    except Exception as models_error:
        print(f"Failed to load from torchvision.models: {models_error}")
        print("Please try: pip install torch torchvision --force-reinstall")
        exit(1)

# Download human-readable labels for ImageNet.
response = requests.get("https://git.io/JJkYN")
labels = response.text.split("\n")

def predict(inp):
    try:
        print(f"Input received: {type(inp)}")
        inp = transforms.ToTensor()(inp).unsqueeze(0)
        print(f"Tensor shape: {inp.shape}")
        with torch.no_grad():
            prediction = torch.nn.functional.softmax(model(inp)[0], dim=0)
            confidences = {labels[i]: float(prediction[i]) for i in range(1000)}
        print("Prediction completed successfully")
        return confidences
    except Exception as e:
        print(f"Error in prediction: {e}")
        return {"Error": 1.0}

import gradio as gr
demo = gr.Interface(fn=predict,
       inputs=gr.Image(type="pil"),
       outputs=gr.Label(num_top_classes=3),
       examples=["https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg"])
demo.launch(debug=True)