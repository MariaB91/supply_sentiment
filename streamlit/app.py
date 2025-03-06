import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page Streamlit
st.set_page_config(page_title="Analyse des Avis Clients", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    """Charge les données depuis le fichier JSON"""
    df = pd.read_json("Prediction/dashboard_data.json")
    return df

# Charger les données
df = load_data()

# Vérifier si le DataFrame est vide
if df.empty:
    st.error("Le fichier JSON est vide ou n'a pas pu être chargé.")
    st.stop()

# ✅ Ajouter un filtre par marque dans la sidebar
marque_selectionnee = st.sidebar.selectbox(
    "Sélectionner une marque :", 
    options=df["marque"].unique(),
    index=0
)

# Filtrer les données selon la marque sélectionnée
df_filtered = df[df["marque"] == marque_selectionnee]

st.title(f"📊 Dashboard d'Analyse des Avis Clients - {marque_selectionnee}")

# Afficher un résumé des données filtrées
st.subheader("📋 Informations générales")
col1, col2, col3 = st.columns(3)
col1.metric("Nombre total d'avis", df_filtered.shape[0])
col2.metric("Trust Score Moyen", round(df_filtered["trust_score"].mean(), 2))
col3.metric("Note Moyenne", round(df_filtered["rating"].mean(), 2))

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

# 📌 **Analyse des catégories de réponse (Si disponible)**
if "cat_response" in df_filtered.columns:
    st.subheader("📧 Catégories de Réponses des Entreprises")
    fig_response = px.histogram(
        df_filtered, x="cat_response", title="Répartition des Réponses",
        color_discrete_sequence=["#00CC96"]
    )
    st.plotly_chart(fig_response, use_container_width=True)
