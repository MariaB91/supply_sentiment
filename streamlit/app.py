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
        with open('beautifulsoup/reviews.json', 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
        with open('beautifulsoup/filtered_list.json', 'r', encoding='utf-8') as f:
            trust_data = json.load(f)
        
        marque_to_company = {item['marque']: item['liens_marque'] for item in trust_data if isinstance(item, dict)}
        trust_scores = {item['liens_marque']: float(item.get('trust_score', '0').replace(',', '.')) for item in trust_data if isinstance(item, dict)}

        df = pd.DataFrame(reviews_data)
        if 'review_date' in df.columns:
            df['review_date'] = pd.to_datetime(df['review_date'])
        return df, trust_scores, marque_to_company
    except FileNotFoundError as e:
        st.error(f"Erreur de chargement des fichiers: {str(e)}")
        return pd.DataFrame(), {}, {}

def create_trust_gauge(trust_score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=trust_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Trust Score", 'font': {'size': 24, 'color': 'black'}},  # Couleur du titre
        gauge={
            'axis': {'range': [0, 5], 'tickwidth': 1, 'tickcolor': 'black'},
            'bar': {'color': "#04AA6D"},  # Vert
            'steps': [
                {'range': [0, 2], 'color': '#FF4B4B'},  # Rouge
                {'range': [2, 4], 'color': '#FFA500'},  # Orange
                {'range': [4, 5], 'color': '#04AA6D'}  # Vert
            ]
        }
    ))
    fig.update_layout(height=350, margin={'t': 40, 'b': 0, 'l': 0, 'r': 0})  # Marges ajustées
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

    today = datetime.now()
    start_6m = today - timedelta(days=180)

    df_6m = df[df['review_date'] >= start_6m]

    col1, col2 = st.columns(2)

    # Évolution des notes par mois
    with col1:
        df_trend_6m = df_6m.groupby(df_6m['review_date'].dt.to_period('M'))['rating'].mean().reset_index()
        df_trend_6m['review_date'] = df_trend_6m['review_date'].dt.strftime('%Y-%m')  # Format mois-année

        fig_6m = px.line(df_trend_6m, x='review_date', y='rating', title="Évolution des notes (6 mois)", markers=True,
                         template="plotly_dark")  # Ajouter un thème sombre pour plus d'impact visuel
        fig_6m.update_xaxes(title="Mois", tickangle=45)
        fig_6m.update_yaxes(title="Note moyenne", range=[1, 5], showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig_6m.update_traces(line=dict(width=3, color='deepskyblue'))  # Améliorer l'aspect de la ligne
        st.plotly_chart(fig_6m, use_container_width=True)

    # Distribution des notes par semaine
    with col2:
        df_6m['week'] = df_6m['review_date'].dt.to_period('W').dt.start_time
        df_weekly_dist = df_6m.groupby([df_6m['week'], 'rating']).size().reset_index(name='count')

        fig_dist = px.line(df_weekly_dist, x='week', y='count', color='rating', 
                           title="Distribution des notes par semaine", markers=True,
                           template="plotly_dark")  # Thème sombre
        fig_dist.update_xaxes(title="Semaine", tickangle=45)
        fig_dist.update_yaxes(title="Nombre d'avis", showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig_dist.update_traces(line=dict(width=2))  # Améliorer les lignes
        st.plotly_chart(fig_dist, use_container_width=True)

    # Nombre de réponses et ratio
    df_6m['has_response'] = df_6m['response'].notna() & df_6m['response'].str.strip().ne('null')
    df_responses = df_6m.groupby(df_6m['review_date'].dt.to_period('M')).agg(
        total_reviews=('rating', 'count'),
        total_responses=('has_response', 'sum')
    ).reset_index()

    df_responses['response_ratio'] = df_responses['total_responses'] / df_responses['total_reviews'] * 100
    df_responses['review_date'] = df_responses['review_date'].dt.strftime('%Y-%m')  # Format mois-année

    fig_response = px.bar(df_responses, x='review_date', y='response_ratio',
                          title="Ratio de réponses aux avis par mois",
                          labels={'response_ratio': '% Réponses'},
                          text='response_ratio', 
                          color='response_ratio',
                          color_continuous_scale='Viridis',  # Palette de couleurs améliorée
                          template="plotly_dark")  # Thème sombre
    fig_response.update_traces(texttemplate='%{text:.1f}%', textposition='outside', width=0.8)
    fig_response.update_xaxes(title="Mois")
    fig_response.update_yaxes(title="Pourcentage de réponses (%)", showgrid=True, gridwidth=1, gridcolor='lightgray')
    st.plotly_chart(fig_response, use_container_width=True)

if __name__ == "__main__":
    show_dashboard()
