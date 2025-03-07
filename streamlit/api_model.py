import joblib
from flask import Flask, request, jsonify
import logging

# Initialiser l'application Flask
app = Flask(__name__)

# Charger le modèle
try:
    model = joblib.load('Prediction/models/final_model/MLmodel')  # Assurez-vous que le chemin est correct
    logging.info("Modèle chargé avec succès.")
except Exception as e:
    logging.error(f"Erreur lors du chargement du modèle : {e}")

# Route pour prédire (accepte POST)
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Récupérer les données envoyées en JSON
        data = request.get_json()
        commentaire = data.get('commentaire', '')  # Extraire le commentaire

        if not commentaire:
            return jsonify({'error': 'Le commentaire est vide'}), 400

        # Si vous devez pré-traiter le commentaire (par exemple avec un vectorizer)
        # Prétraitement du commentaire ici si nécessaire
        # Exemple avec un vectorizer :
        # X_input = vectorizer.transform([commentaire])

        # Faire la prédiction
        prediction = model.predict([commentaire])  # Utilisez votre modèle pour prédire

        return jsonify({'prediction': prediction[0]})  # Retourner la prédiction

    except Exception as e:
        logging.error(f"Erreur dans la prédiction : {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Permet d'écouter sur toutes les adresses IP
