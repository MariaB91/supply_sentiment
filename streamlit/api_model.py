import mlflow
import mlflow.pyfunc
from flask import Flask, request, jsonify

# Créez une instance de l'application Flask
app = Flask(__name__)

# Charger le modèle MLflow
mlflow.set_tracking_uri('http://localhost:5000')  # Assurez-vous que MLflow est configuré correctement
model_uri = 'runs:/4a104d66b7ec4b9ea4c06064f3d275e9/final_model'  # URI de votre modèle
model = mlflow.pyfunc.load_model(model_uri)

# Définir un endpoint pour la prédiction
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Récupérer le commentaire envoyé dans la requête JSON
        data = request.get_json()
        commentaire = data['commentaire']

        # Effectuer la prédiction
        prediction = model.predict([commentaire])

        # Retourner la prédiction dans la réponse
        return jsonify({'prediction': prediction[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Démarrer l'API Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # L'API sera accessible sur http://localhost:5001
