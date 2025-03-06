import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
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

        # Vérification de l'existence de la colonne review_date
        if 'review_date' not in df.columns:
            st.error("'review_date' n'existe pas dans le DataFrame.")
            return pd.DataFrame(), {}, {}

        # Conversion des dates en datetime avec gestion des erreurs
        df['review_date'] = pd.to_datetime(df['review_date'], format='%d-%m-%Y', errors='coerce')  # Conversion en datetime
        df['response_date'] = pd.to_datetime(df['response_date'], format='%d-%m-%Y', errors='coerce')  # Conversion en datetime

        # Vérification après conversion des dates
        if df['review_date'].isnull().any():
            st.warning("Certaines valeurs dans 'review_date' sont invalides après conversion.")

        # Création des nouvelles colonnes pour regroupement
        df['review_month'] = df['review_date'].dt.to_period('M')  # Regrouper par mois
        df['review_week'] = df['review_date'].dt.to_period('W')   # Regrouper par semaine
        df['response_month'] = df['response_date'].dt.to_period('M')  # Regrouper par mois
        df['response_week'] = df['response_date'].dt.to_period('W')   # Regrouper par semaine

        # Ajout d'une colonne "has_response" pour savoir si un avis a une réponse
        df['has_response'] = df['response_date'].notna()

        return df, trust_scores, marque_to_company
    except FileNotFoundError as e:
        st.error(f"Erreur de chargement des fichiers: {str(e)}")
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

    # Sélection de la marque dans la sidebar
    marque = st.sidebar.selectbox("Sélectionner une marque", options=list(marque_to_company.keys()))
    company_name = marque_to_company.get(marque, "")
    df = df[df['company_name'] == company_name]
    trust_score = trust_scores.get(company_name, 0.0)

    # Affichage du Trust Score sous forme de jauge
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)

    # Vérifier l'existence de 'review_month' après transformation
    if 'review_month' not in df.columns:
        st.error("'review_month' n'existe pas dans le DataFrame après transformation. Vérifiez la conversion des dates.")
        return

    # Regroupement des données par mois
    df_monthly_reviews = df.groupby('review_month').size().reset_index(name='reviews_count')
    df_monthly_responses = df[df['has_response']].groupby('response_month').size().reset_index(name='responses_count')

    # Ajout d'une colonne pour les avis sans réponse
    df_monthly_no_responses = df[~df['has_response']].groupby('review_month').size().reset_index(name='no_responses_count')

    # Fusion des DataFrames
    df_reviews_responses = pd.merge(df_monthly_reviews, df_monthly_responses, how='left', on='review_month')
    df_reviews_responses = pd.merge(df_reviews_responses, df_monthly_no_responses, how='left', on='review_month')
    
    # Remplir les NaN par 0 pour les avis sans réponse
    df_reviews_responses['responses_count'].fillna(0, inplace=True)
    df_reviews_responses['no_responses_count'].fillna(0, inplace=True)

    # Création des graphiques
    col1, col2 = st.columns(2)

    # Graphique des avis par mois
    with col1:
        fig_reviews = px.line(df_reviews_responses, x='review_month', y='reviews_count', title="Évolution des Avis par Mois", markers=True)
        fig_reviews.update_xaxes(title="Mois")
        fig_reviews.update_yaxes(title="Nombre d'Avis")
        st.plotly_chart(fig_reviews, use_container_width=True)

    # Graphique des réponses par mois
    with col2:
        fig_responses = px.bar(df_reviews_responses, x='review_month', y='responses_count', title="Réponses aux Avis par Mois", labels={'responses_count': 'Nombre de Réponses'})
        fig_responses.update_xaxes(title="Mois")
        fig_responses.update_yaxes(title="Nombre de Réponses")
        st.plotly_chart(fig_responses, use_container_width=True)

    # Graphique des avis sans réponse
    with col2:
        fig_no_responses = px.bar(df_reviews_responses, x='review_month', y='no_responses_count', title="Avis sans Réponse par Mois", labels={'no_responses_count': 'Nombre d\'Avis sans Réponse'})
        fig_no_responses.update_xaxes(title="Mois")
        fig_no_responses.update_yaxes(title="Nombre d'Avis sans Réponse")
        st.plotly_chart(fig_no_responses, use_container_width=True)

if __name__ == "__main__":
    show_dashboard()
