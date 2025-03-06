import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

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

        # Conversion des dates en datetime
        df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
        df['response_date'] = pd.to_datetime(df['response_date'], errors='coerce')

        # Création des nouvelles colonnes pour regroupement
        df['review_month'] = df['review_date'].dt.to_period('M')  # Regrouper par mois
        df['review_week'] = df['review_date'].dt.to_period('W')   # Regrouper par semaine
        df['response_month'] = df['response_date'].dt.to_period('M')  # Regrouper par mois
        df['response_week'] = df['response_date'].dt.to_period('W')   # Regrouper par semaine

        # Vérification des nouvelles colonnes
        st.write("Colonnes disponibles dans le DataFrame :")
        st.write(df.columns)

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
    
    df, trust_scores, marque_to_company = load_data()
    if df.empty:
        st.warning("Aucune donnée disponible.")
        return

    marque = st.sidebar.selectbox("Sélectionner une marque", options=list(marque_to_company.keys()))
    company_name = marque_to_company.get(marque, "")
    df = df[df['company_name'] == company_name]
    trust_score = trust_scores.get(company_name, 0.0)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)

    # Vérification des premières lignes du DataFrame après la transformation des dates
    st.write("Aperçu des données après transformation des dates :")
    st.write(df.head())

    # Vérification des colonnes disponibles avant la fusion
    st.write("Colonnes disponibles pour la fusion :")
    st.write(df.columns)

    # Groupe des avis par mois
    df_monthly_reviews = df.groupby('review_month').size().reset_index(name='reviews_count')

    # Groupe des réponses par mois
    df_monthly_responses = df[df['response_date'].notna()].groupby('response_month').size().reset_index(name='responses_count')

    # Vérification avant la fusion
    st.write("Aperçu des données regroupées par mois :")
    st.write(df_monthly_reviews.head())
    st.write(df_monthly_responses.head())

    # Merge des deux DataFrames
    df_reviews_responses = pd.merge(df_monthly_reviews, df_monthly_responses, how='left', on='review_month')
    df_reviews_responses['responses_count'].fillna(0, inplace=True)  # Remplir les NaN par 0
    
    col1, col2 = st.columns(2)
    
    # Évolution des avis par mois
    with col1:
        fig_reviews = px.line(df_reviews_responses, x='review_month', y='reviews_count', title="Évolution des Avis par Mois", markers=True)
        fig_reviews.update_xaxes(title="Mois")
        fig_reviews.update_yaxes(title="Nombre d'Avis")
        st.plotly_chart(fig_reviews, use_container_width=True)
    
    # Répartition des réponses par mois
    with col2:
        fig_responses = px.bar(df_reviews_responses, x='review_month', y='responses_count', title="Réponses aux Avis par Mois", labels={'responses_count': 'Nombre de Réponses'})
        fig_responses.update_xaxes(title="Mois")
        fig_responses.update_yaxes(title="Nombre de Réponses")
        st.plotly_chart(fig_responses, use_container_width=True)

    # Graphique de distribution des notes par semaine
    df_weekly_reviews = df.groupby('review_week')['rating'].mean().reset_index(name='average_rating')

    col1, col2 = st.columns(2)
    with col1:
        fig_rating_weekly = px.line(df_weekly_reviews, x='review_week', y='average_rating', title="Évolution des Notes Moyennes par Semaine", markers=True)
        fig_rating_weekly.update_xaxes(title="Semaine")
        fig_rating_weekly.update_yaxes(title="Note Moyenne")
        st.plotly_chart(fig_rating_weekly, use_container_width=True)

    # Distribution des notes sur toutes les périodes
    with col2:
        fig_rating_dist = px.histogram(df, x='rating', nbins=5, title="Distribution des Notes", labels={'rating': 'Notes'})
        fig_rating_dist.update_xaxes(title="Notes (1-5)")
        fig_rating_dist.update_yaxes(title="Nombre d'Avis")
        st.plotly_chart(fig_rating_dist, use_container_width=True)

if __name__ == "__main__":
    show_dashboard()
