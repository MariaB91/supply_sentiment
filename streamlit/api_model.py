import os
import mlflow
import mlflow.pyfunc
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Assurez-vous que l'URI de suivi MLflow est correctement configuré
# Remplacez l'URL ci-dessous par l'URL de votre serveur MLflow
mlflow.set_tracking_uri("http://localhost:5000")  # Utilisez l'URL de votre serveur MLflow ici

# Charger le modèle à partir de l'URI mlflow-artifacts
MODEL_URI = "mlflow-artifacts:/703686963448022104/4a104d66b7ec4b9ea4c06064f3d275e9/artifacts/final_model/MLmodel"
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
