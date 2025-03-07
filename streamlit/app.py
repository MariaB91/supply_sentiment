import streamlit as st
import pandas as pd
import plotly.express as px
import json
import requests  # Utilisé pour appeler l'API

# URL de l'API déployée sur Render
API_URL = "https://supply-sentiment.onrender.com"

# Charger les données
@st.cache_data
def load_data():
    return pd.read_json("Prediction/dashboard_data.json")

@st.cache_data
def load_trust_data():
    with open("beautifulsoup/filtered_list.json", "r", encoding="utf-8") as f:
        trust_data = json.load(f)
    
    df_trust = pd.DataFrame(trust_data)
    trust_scores = {item["marque"]: float(item.get("trust_score", "0").replace(",", ".")) for item in trust_data}
    reviews_count = {item["marque"]: int(item.get("reviews", 0)) for item in trust_data}

    return trust_scores, reviews_count

# Charger les données
df = load_data()
trust_scores, reviews_count = load_trust_data()

# Sélection de la marque
marque_selectionnee = st.sidebar.selectbox("Sélectionner une marque :", options=df["marque"].unique(), index=0)

# Filtrer les données
df_filtered = df[df["marque"] == marque_selectionnee]
trust_score = trust_scores.get(marque_selectionnee, 0.0)
total_reviews = reviews_count.get(marque_selectionnee, 0)

# Fonction de jauge Trust Score
def create_trust_gauge(trust_score):
    import plotly.graph_objects as go
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
    return fig

# Affichage général
st.title(f"📊 Dashboard d'Analyse des Avis Clients - {marque_selectionnee}")
st.subheader("📋 Informations générales")
col1, col2, col3 = st.columns(3)
col1.metric("Nombre total d'avis", total_reviews)
col2.metric("Trust Score", round(trust_score, 2))
col3.metric("Note Moyenne", round(df_filtered["rating"].mean(), 2))

st.subheader("🔹 Trust Score")
st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)

st.subheader("📊 Distribution des Avis par Note")
fig_rating = px.histogram(df_filtered, x="rating", nbins=5, labels={"rating": "Note"},
                          title="Répartition des Avis Clients", color_discrete_sequence=["#636EFA"])
st.plotly_chart(fig_rating, use_container_width=True)

st.subheader("📅 Évolution des Avis au Fil du Temps")
df_filtered["review_date"] = pd.to_datetime(df_filtered["review_date"], errors="coerce")
df_time_series = df_filtered.groupby("review_date").size().reset_index(name="Nombre d'avis")

fig_time_series = px.line(df_time_series, x="review_date", y="Nombre d'avis", markers=True,
                          title="Tendance des Avis Clients", color_discrete_sequence=["#EF553B"])
st.plotly_chart(fig_time_series, use_container_width=True)

# Prédiction du rating
st.subheader("📝 Prédiction de la Note à partir d'un Commentaire")
commentaire = st.text_area("Entrez votre commentaire ici")

if commentaire:
    try:
        response = requests.post(API_URL, json={"commentaire": commentaire})
        if response.status_code == 200:
            predicted_rating = response.json()["prediction"]
            st.write(f"Note prédite : {predicted_rating}")
        else:
            st.error(f"Erreur de l'API : {response.json().get('error', 'Problème inconnu')}")
    except Exception as e:
        st.error(f"Erreur lors de la requête à l'API : {e}")
