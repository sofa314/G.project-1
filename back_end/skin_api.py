from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from PIL import Image
import os

app = Flask(__name__)
CORS(app)

# Load the model
model = load_model('back_end/ml_models/skin_cancer_model20.h5')

# Define class labels
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

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(port=5001, debug=True)
