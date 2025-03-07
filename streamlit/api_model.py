import os
import mlflow.pyfunc
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Charger le modèle MLflow
MODEL_URI = "runs:/4a104d66b7ec4b9ea4c06064f3d275e9/final_model"  # Remplace avec le bon URI
model = mlflow.pyfunc.load_model(MODEL_URI)

@app.route("/")
def home():
    return "L'API de prédiction fonctionne !"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        commentaire = data.get("commentaire", "")

        if not commentaire:
            return jsonify({"error": "Aucun commentaire fourni"}), 400
        
        # Prédiction
        prediction = model.predict([commentaire])
        return jsonify({"prediction": prediction[0]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render attribue un port dynamique
    app.run(host="0.0.0.0", port=port)
