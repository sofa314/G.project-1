from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
from PIL import Image

app = Flask(__name__)
CORS(app, origins=["https://sofa314.github.io"])

# Use absolute path for model loading
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "skin_cancer_model20.h5")
model = load_model(MODEL_PATH)

class_labels = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']

@app.route('/predict-skin', methods=['POST'])
def predict_skin():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    image = Image.open(image_file).resize((28, 28))
    image = image.convert("RGB")
    image_array = img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0)
    image_array /= 255.0

    prediction = model.predict(image_array)
    predicted_class = class_labels[np.argmax(prediction)]

    return jsonify({
        'predicted_class': predicted_class,
        'confidence': float(np.max(prediction))
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
