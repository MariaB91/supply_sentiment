import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Configuration de la page
st.set_page_config(
    page_title="Analyse des Avis Clients",
    page_icon="📊",
    layout="wide"
)

# Chargement des données
@st.cache_data
def load_data():
    try:
        # Chargement des reviews
        with open('beautifulsoup/reviews.json', 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
        
        # Chargement des trust scores
        with open('beautifulsoup/filtered_list.json', 'r', encoding='utf-8') as f:
            trust_data = json.load(f)
        
        # Vérification de la structure des données
        trust_scores = {item['marque']: item.get('trust_score', 0.0) for item in trust_data if isinstance(item, dict)}
        
        df = pd.DataFrame(reviews_data)
        if 'review_date' in df.columns:
            df['review_date'] = pd.to_datetime(df['review_date'])
        
        return df, trust_scores
    except FileNotFoundError as e:
        st.error(f"Erreur de chargement des fichiers: {str(e)}")
        return pd.DataFrame(), {}

# Création d'une jauge pour le trust score
def create_trust_gauge(trust_score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=trust_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Trust Score", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 0.3], 'color': '#FF4B4B'},
                {'range': [0.3, 0.7], 'color': '#FFA500'},
                {'range': [0.7, 1], 'color': '#04AA6D'}
            ]
        }
    ))
    fig.update_layout(height=300)
    return fig

# Affichage du dashboard
def show_dashboard():
    st.title("📊 Dashboard d'Analyse des Avis Clients")
    
    df, trust_scores = load_data()
    if df.empty:
        st.warning("Aucune donnée disponible.")
        return
    
    # Sélection de la marque
    marque = st.sidebar.selectbox("Sélectionner une marque", options=list(trust_scores.keys()))
    df = df[df['marque'] == marque]
    trust_score = trust_scores.get(marque, 0.0)
    
    # Affichage du trust score
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)
    
    # Filtres de période
    today = datetime.now()
    start_6m = today - timedelta(days=180)
    start_1w = today - timedelta(days=7)
    
    df_6m = df[df['review_date'] >= start_6m]
    df_1w = df[df['review_date'] >= start_1w]
    
    # Évolution des notes (6 mois & semaine)
    col1, col2 = st.columns(2)
    
    with col1:
        df_trend_6m = df_6m.groupby(pd.Grouper(key='review_date', freq='M'))['rating'].mean().reset_index()
        fig_6m = px.line(df_trend_6m, x='review_date', y='rating', title="Évolution des notes (6 mois)")
        st.plotly_chart(fig_6m, use_container_width=True)
    
    with col2:
        df_trend_1w = df_1w.groupby(pd.Grouper(key='review_date', freq='W'))['rating'].mean().reset_index()
        fig_1w = px.line(df_trend_1w, x='review_date', y='rating', title="Évolution des notes (par semaine)")
        st.plotly_chart(fig_1w, use_container_width=True)

def main():
    page = st.sidebar.radio("Navigation", ["Dashboard"])
    if page == "Dashboard":
        show_dashboard()

if __name__ == "__main__":  
    main()
