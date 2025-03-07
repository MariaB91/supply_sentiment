import streamlit as st
import mlflow
import mlflow.pyfunc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Configuration de la page Streamlit
st.set_page_config(page_title="Analyse des Avis Clients", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    """Charge les données des avis depuis prediction/dashboard_data.json"""
    df = pd.read_json("Prediction/dashboard_data.json")
    return df

@st.cache_data
def load_trust_data():
    """Charge les Trust Scores depuis beautifulsoup/filtered_list.json"""
    with open("beautifulsoup/filtered_list.json", "r", encoding="utf-8") as f:
        trust_data = json.load(f)

    df_trust = pd.DataFrame(trust_data)
    trust_scores = {item["marque"]: float(item.get("trust_score", "0").replace(",", ".")) for item in trust_data}
    reviews_count = {item["marque"]: int(item.get("reviews", 0)) for item in trust_data}

    return trust_scores, reviews_count

# Charger les données
df = load_data()
trust_scores, reviews_count = load_trust_data()

# Vérifier si le DataFrame est vide
if df.empty:
    st.error("Le fichier JSON des avis est vide ou n'a pas pu être chargé.")
    st.stop()

# ✅ Ajouter un filtre par marque dans la sidebar
marque_selectionnee = st.sidebar.selectbox(
    "Sélectionner une marque :", 
    options=df["marque"].unique(),
    index=0
)

# Filtrer les données selon la marque sélectionnée
df_filtered = df[df["marque"] == marque_selectionnee]

# Récupérer le Trust Score et le nombre d’avis
trust_score = trust_scores.get(marque_selectionnee, 0.0)
total_reviews = reviews_count.get(marque_selectionnee, 0)

# 📌 **Créer une jauge pour le Trust Score**
def create_trust_gauge(trust_score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=trust_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Trust Score", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 5]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 2], 'color': '#FF4B4B'},
                {'range': [2, 4], 'color': '#FFA500'},
                {'range': [4, 5], 'color': '#04AA6D'}
            ]
        }
    ))
    fig.update_layout(height=300)
    return fig

# 📌 **Charger le modèle depuis MLflow**
def load_mlflow_model():
    # Remplacez l'URL et l'URI par votre propre modèle MLflow
    model_uri = "mlflow-artifacts:/703686963448022104/4a104d66b7ec4b9ea4c06064f3d275e9/artifacts/final_model/model.pkl"
    model = mlflow.pyfunc.load_model(model_uri)
    return model

# Charger le modèle
model = load_mlflow_model()

# Fonction de prédiction
def predict_rating(commentaire):
    # Effectuer la prédiction
    prediction = model.predict([commentaire])
    return prediction[0]  # Retourner la première prédiction (car on envoie une liste)

# Titre du Dashboard
st.title(f"📊 Dashboard d'Analyse des Avis Clients - {marque_selectionnee}")

# 📋 **Résumé des statistiques**
st.subheader("📋 Informations générales")
col1, col2, col3 = st.columns(3)
col1.metric("Nombre total d'avis", total_reviews)
col2.metric("Trust Score", round(trust_score, 2))
col3.metric("Note Moyenne", round(df_filtered["rating"].mean(), 2))

# 📌 **Affichage de la jauge du Trust Score**
st.subheader("🔹 Trust Score")
st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)

# 📌 **Distribution des avis par note (rating)**
st.subheader("📊 Distribution des Avis par Note")
fig_rating = px.histogram(
    df_filtered, x="rating", nbins=5, labels={"rating": "Note"},
    title="Répartition des Avis Clients", color_discrete_sequence=["#636EFA"]
)
st.plotly_chart(fig_rating, use_container_width=True)

# 📌 **Évolution des avis dans le temps**
st.subheader("📅 Évolution des Avis au Fil du Temps")
df_filtered["review_date"] = pd.to_datetime(df_filtered["review_date"], errors="coerce")
df_time_series = df_filtered.groupby("review_date").size().reset_index(name="Nombre d'avis")

fig_time_series = px.line(
    df_time_series, x="review_date", y="Nombre d'avis", markers=True,
    title="Tendance des Avis Clients",
    color_discrete_sequence=["#EF553B"]
)
st.plotly_chart(fig_time_series, use_container_width=True)

# --- Page de simulation (prédiction à partir du commentaire) ---
st.sidebar.subheader("💬 Simulation de Prédiction")

# Formulaire pour entrer un commentaire
commentaire = st.text_area("Entrez un commentaire pour prédire la note :")

# Prédiction quand l'utilisateur soumet le commentaire
if commentaire:
    rating_predicted = predict_rating(commentaire)
    st.subheader(f"Rating prédit pour ce commentaire : {rating_predicted:.2f}")
