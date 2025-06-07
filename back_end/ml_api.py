from flask import Flask, request, jsonify
from flask_cors import CORS 
import joblib
import numpy as np
import os

app = Flask(__name__)
CORS(app, origins=["https://sofa314.github.io"])

# Use absolute paths to load models (fixes FileNotFoundError on Railway)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HEART_MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "gradin_boost_model.pkl")
BREAST_MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "decision_tree_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "ml_models", "scaler (1).pkl")

# Load the models
heart_model = joblib.load(HEART_MODEL_PATH)  # heart
breast_model = joblib.load(BREAST_MODEL_PATH)  # breast
scaler = joblib.load(SCALER_PATH)  # if needed

# Route لتوقع مرض القلب
@app.route('/predict-heart', methods=['POST'])
def predict_heart():
    data = request.json
    features = np.array(data['features']).reshape(1, -1)
    features = scaler.transform(features)  # scaling لو الموديل محتاجه
    prediction = heart_model.predict(features)
    return jsonify({'prediction': int(prediction[0])})



# Route لتوقع سرطان الثدي
@app.route('/predict-breast', methods=['POST'])
def predict_breast():
    data = request.get_json()

    # استخرج القيم واحدة واحدة
    clump_thickness = data['clump_thickness']
    uniformity_cell_size = data['uniformity_cell_size']
    uniformity_cell_shape = data['uniformity_cell_shape']
    marginal_adhesion = data['marginal_adhesion']
    single_epithelial_cell_size = data['single_epithelial_cell_size']
    bare_nuclei = data['bare_nuclei']
    bland_chromatin = data['bland_chromatin']
    normal_nucleoli = data['normal_nucleoli']
    mitoses = data['mitoses']

    features = np.array([
        clump_thickness,
        uniformity_cell_size,
        uniformity_cell_shape,
        marginal_adhesion,
        single_epithelial_cell_size,
        bare_nuclei,
        bland_chromatin,
        normal_nucleoli,
        mitoses
    ]).reshape(1, -1)

    prediction = breast_model.predict(features)[0]
    result = "Malignant" if prediction == 4 else "Benign"
    return jsonify({"prediction": result})


# Run the server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5002))
    app.run(host='0.0.0.0', port=port, debug=True)