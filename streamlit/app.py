import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configuration de la page Streamlit
st.set_page_config(page_title="Analyse des Avis Clients", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    try:
        # Chargement des données JSON
        with open('beautifulsoup/reviews.json', 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
        with open('beautifulsoup/filtered_list.json', 'r', encoding='utf-8') as f:
            trust_data = json.load(f)
        
        marque_to_company = {item['marque']: item['liens_marque'] for item in trust_data if isinstance(item, dict)}
        trust_scores = {item['liens_marque']: float(item.get('trust_score', '0').replace(',', '.')) for item in trust_data if isinstance(item, dict)}

        df = pd.DataFrame(reviews_data)

        # Vérification des colonnes
        if 'review_date' not in df.columns or 'company_name' not in df.columns or 'rating' not in df.columns:
            st.error("Certaines colonnes nécessaires sont manquantes dans le DataFrame.")
            return pd.DataFrame(), {}, {}

        # Conversion des dates en datetime
        df['review_date'] = pd.to_datetime(df['review_date'], format='%d-%m-%Y', errors='coerce')
        df['response_date'] = pd.to_datetime(df['response_date'], format='%d-%m-%Y', errors='coerce')

        return df, trust_scores, marque_to_company

    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return pd.DataFrame(), {}, {}

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

def show_dashboard():
    st.title("📊 Dashboard d'Analyse des Avis Clients")
    
    # Charger les données
    df, trust_scores, marque_to_company = load_data()
    if df.empty:
        st.warning("Aucune donnée disponible.")
        return

    # Sélection de la marque
    marque = st.sidebar.selectbox("Sélectionner une marque", options=list(marque_to_company.keys()))
    company_name = marque_to_company.get(marque, "")
    
    if company_name:
        df = df[df['company_name'] == company_name]
    else:
        st.warning("Aucune entreprise trouvée pour cette marque.")
        return

    trust_score = trust_scores.get(company_name, 0.0)

    # Affichage du Trust Score sous forme de jauge
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)

    # Groupement des reviews par date
    grouped_reviews = df.groupby('review_date').size()
    grouped_reviews.index = pd.to_datetime(grouped_reviews.index, errors='coerce')
    grouped_reviews = grouped_reviews.sort_index()

    # Affichage des reviews dans un graphique
    st.subheader("📅 Évolution des Avis Clients")
    if not grouped_reviews.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(grouped_reviews.index, grouped_reviews.values, marker='o', color='skyblue', label='Nombre de Reviews')
        ax.set_title("Nombre de Reviews par Date", fontsize=16)
        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel("Nombre de Reviews", fontsize=14)
        plt.xticks(rotation=45)
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning("Aucune donnée de review disponible pour cette marque.")

    # Groupement des reviews par rating
    grouped_reviews_by_rating = df.groupby('rating').size()
    grouped_responses_by_rating = df[df['response_date'].notnull()].groupby('rating').size()

    # Affichage conditionnel des pie charts
    st.subheader("⭐ Répartition des Avis et Réponses par Note")

    col1, col2 = st.columns(2)

    with col1:
        if not grouped_reviews_by_rating.empty:
            st.subheader("Distribution des Avis par Note")
            fig, ax = plt.subplots()
            ax.pie(grouped_reviews_by_rating, labels=grouped_reviews_by_rating.index, autopct='%1.1f%%', 
                   startangle=140, colors=sns.color_palette('Blues', len(grouped_reviews_by_rating)))
            ax.set_title("Avis par Note")
            st.pyplot(fig)
        else:
            st.warning("Aucune donnée disponible pour la distribution des avis par note.")

    with col2:
        if not grouped_responses_by_rating.empty:
            st.subheader("Distribution des Réponses par Note")
            fig, ax = plt.subplots()
            ax.pie(grouped_responses_by_rating, labels=grouped_responses_by_rating.index, autopct='%1.1f%%', 
                   startangle=140, colors=sns.color_palette('Reds', len(grouped_responses_by_rating)))
            ax.set_title("Réponses par Note")
            st.pyplot(fig)
        else:
            st.warning("Aucune donnée disponible pour la distribution des réponses par note.")

if __name__ == "__main__":
    show_dashboard()
