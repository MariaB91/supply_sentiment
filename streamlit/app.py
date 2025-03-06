import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import mlflow
import json
from wordcloud import WordCloud
from collections import Counter

# Configuration de la page
st.set_page_config(
    page_title="📊 Analyse des Avis Clients",
    page_icon="📈",
    layout="wide"
)

# Chargement des données
@st.cache_data
def load_data():
    try:
        with open('beautifulsoup/reviews.json', 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
        with open('beautifulsoup/filtered_list.json', 'r', encoding='utf-8') as f:
            trust_data = json.load(f)

        # Convertir les données en DataFrame
        df = pd.DataFrame(reviews_data)

        # Vérifier et convertir les dates si la colonne 'review_date' existe
        if 'review_date' in df.columns:
            df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')  # 'review_date' est la colonne correcte ici

        # Charger les scores de confiance des entreprises
        trust_scores = {
            item['company']: float(item.get('trust_score', "0").replace(',', '.'))
            for item in trust_data if isinstance(item, dict) and 'company' in item
        }
        return df, trust_scores
    except FileNotFoundError as e:
        st.error(f"Erreur de chargement des fichiers: {str(e)}")
        return pd.DataFrame(), {}

@st.cache_resource
def load_model():
    try:
        return mlflow.sklearn.load_model("Prediction/models/final_model")
    except Exception as e:
        st.error(f"Erreur de chargement du modèle: {str(e)}")
        return None

# Fonction pour créer le gauge du score de confiance
def create_trust_gauge(trust_score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=trust_score,
        title={'text': "Trust Score"},
        gauge={
            'axis': {'range': [0, 1]},
            'steps': [
                {'range': [0, 0.3], 'color': '#FF4B4B'},
                {'range': [0.3, 0.7], 'color': '#FFA500'},
                {'range': [0.7, 1], 'color': '#04AA6D'}
            ]
        }
    ))
    return fig

# Page du Dashboard
def show_dashboard():
    st.title("📊 Dashboard d'Analyse des Avis Clients")
    df, trust_scores = load_data()

    if df.empty:
        st.warning("Aucune donnée disponible.")
        return

    # Sidebar
    st.sidebar.header("⚙️ Filtres")
    companies = list(trust_scores.keys())
    
    # Défini la variable selected_company dans le scope de la fonction show_dashboard
    selected_company = st.sidebar.selectbox("🏢 Sélectionnez une entreprise", companies)
    df = df[df['company'] == selected_company] if 'company' in df.columns else df

    # Récupérer le score de confiance pour l'entreprise sélectionnée
    trust_score = trust_scores.get(selected_company, 0.0)
    st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📝 Nombre total d'avis", len(df))
    col2.metric("⭐ Note moyenne", f"{df['rating'].mean():.1f}")
    col3.metric("👍 Avis positifs", f"{(df['rating'] >= 4).mean():.1%}")
    col4.metric("📩 Taux de réponse", f"{df['response'].notna().mean():.1%}")
    
    # Graphiques
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.line(df, x='review_date', y='rating', title="📈 Évolution des notes"))
    with col2:
        st.plotly_chart(px.histogram(df, x='rating', title="📊 Distribution des notes"))

    # WordCloud
    col1, col2 = st.columns(2)
    with col1:
        wordcloud = WordCloud(background_color='white').generate(' '.join(df['review'].fillna('')))  # Assurez-vous que 'review' est la bonne colonne
        fig, ax = plt.subplots()
        ax.imshow(wordcloud)
        ax.axis('off')
        st.pyplot(fig)
    with col2:
        top_words = Counter(' '.join(df['review'].fillna('')).lower().split()).most_common(10)  # 'review' doit être la bonne colonne
        st.plotly_chart(px.bar(x=[w for w, _ in top_words], y=[c for _, c in top_words], title="🔝 Mots les plus fréquents"))

# Page de simulation
def show_simulator():
    st.title("🔮 Simulateur d'Impact des Avis")
    model = load_model()
    df, trust_scores = load_data()

    # Vérification des colonnes disponibles dans le DataFrame
    st.write("Colonnes du DataFrame:", df.columns)

    selected_company = st.sidebar.selectbox("🏢 Entreprise à simuler", list(trust_scores.keys()))
    trust_score = trust_scores.get(selected_company, 0.0)
    st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)

    review = st.text_area("📝 Entrez votre review :")
    if st.button("🔍 Analyser"):
        if review and model:
            prediction = model.predict([review])[0]
            st.metric("⭐ Note prédite", prediction)

# Fonction principale
def main():
    page = st.sidebar.radio("🔍 Navigation", ["📊 Dashboard", "🔮 Simulateur"])
    if page == "📊 Dashboard":
        show_dashboard()
    else:
        show_simulator()

if __name__ == "__main__":
    main()
