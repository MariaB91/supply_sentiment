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
        # Conversion de la colonne 'review_date' en datetime
        if 'review_date' in df.columns:
            df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
        return df, trust_scores, marque_to_company
    except FileNotFoundError as e:
        st.error(f"Erreur de chargement des fichiers: {str(e)}")
        return pd.DataFrame(), {}, {}

def create_trust_gauge(trust_score):
    # Graphique de type jauge pour afficher le trust score
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
    
    # Chargement des données
    df, trust_scores, marque_to_company = load_data()
    
    if df.empty:
        st.warning("Aucune donnée disponible.")
        return

    marque = st.sidebar.selectbox("Sélectionner une marque", options=list(marque_to_company.keys()))
    company_name = marque_to_company.get(marque, "")
    df = df[df['company_name'] == company_name]
    trust_score = trust_scores.get(company_name, 0.0)

    # Affichage du trust score
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)

    today = datetime.now()
    start_6m = today - timedelta(days=180)

    # Filtrer les données des 6 derniers mois
    df_6m = df[df['review_date'] >= start_6m]

    col1, col2 = st.columns(2)

    # Graphique de l'évolution des notes par mois
    with col1:
        df['month'] = df['review_date'].dt.to_period('M')  # Groupement par mois
        df_monthly = df.groupby('month')['rating'].mean().reset_index()

        fig_6m = px.line(df_monthly, x='month', y='rating', title="Évolution des Notes Moyennes par Mois", markers=True)
        fig_6m.update_xaxes(title="Mois", tickangle=-45)
        fig_6m.update_yaxes(title="Note Moyenne")
        fig_6m.update_layout(title_x=0.5, title_font_size=20, title_font_color="#004D40")
        st.plotly_chart(fig_6m, use_container_width=True)

    # Graphique de la répartition des notes par semaine
    with col2:
        df['week'] = df['review_date'].dt.to_period('W')  # Groupement par semaine
        df_weekly = df.groupby('week')['rating'].value_counts().unstack(fill_value=0).stack().reset_index(name='count')

        fig_weekly = px.bar(df_weekly, x='week', y='count', color='rating', title="Répartition des Notes par Semaine", labels={'count': 'Nombre d\'Avis'})
        fig_weekly.update_xaxes(title="Semaine")
        fig_weekly.update_yaxes(title="Nombre d'Avis")
        fig_weekly.update_layout(title_x=0.5, title_font_size=20, title_font_color="#004D40")
        st.plotly_chart(fig_weekly, use_container_width=True)

    # Graphique de la répartition des réponses (Réponses vs Non-réponses)
    df_6m['has_response'] = df_6m['response'].notna()
    responses = df_6m['has_response'].value_counts(normalize=True) * 100  # Ratio de réponses
    responses_fig = px.pie(values=responses, names=['Réponses', 'Non-réponses'], title="Répartition des Réponses aux Avis")
    responses_fig.update_layout(title_x=0.5, title_font_size=20, title_font_color="#004D40")
    st.plotly_chart(responses_fig, use_container_width=True)

    # Graphique du ratio de réponses mensuel
    df_responses = df_6m.groupby(df_6m['review_date'].dt.to_period('M')).agg(
        total_reviews=('rating', 'count'),
        total_responses=('has_response', 'sum')
    ).reset_index()

    df_responses['response_ratio'] = df_responses['total_responses'] / df_responses['total_reviews'] * 100
    df_responses['review_date'] = df_responses['review_date'].astype(str)

    fig_response = px.bar(df_responses, x='review_date', y='response_ratio', title="Ratio de Réponses aux Avis par Mois", labels={'response_ratio': '% Réponses'}, text='response_ratio')
    fig_response.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_response.update_xaxes(title="Mois")
    fig_response.update_yaxes(title="Pourcentage de Réponses (%)")
    fig_response.update_layout(title_x=0.5, title_font_size=20, title_font_color="#004D40")

    st.plotly_chart(fig_response, use_container_width=True)

if __name__ == "__main__":
    show_dashboard()
