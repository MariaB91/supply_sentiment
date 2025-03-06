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
            df['review_date'] = pd.to_datetime(df['review_date'], format='%d-%m-%Y', errors='coerce')  # Conversion en datetime
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

    today = datetime.now()
    start_6m = today - timedelta(days=180)

    df_6m = df[df['review_date'] >= start_6m]

    # Regroupement des avis par mois
    df_6m['month'] = df_6m['review_date'].dt.to_period('M')  # Extraire l'année et le mois

    # Répartition globale des réponses et non-réponses
    df_6m['has_response'] = df_6m['response'].notna()  # Création d'une colonne 'has_response' (True si réponse)

    responses_count = df_6m['has_response'].sum()
    no_responses_count = len(df_6m) - responses_count

    # Création du graphique pie chart global (réponses vs non-réponses)
    labels = ['Réponses', 'Non-réponses']
    sizes = [responses_count, no_responses_count]
    colors = ['#A1D6E2', '#FFB2A6']
    explode = (0.1, 0)  # Mettre en évidence le premier segment

    fig_pie_global = go.Figure(go.Pie(labels=labels, values=sizes, hole=0.3, marker=dict(colors=colors), textinfo='percent+label'))
    fig_pie_global.update_layout(title="Répartition globale des réponses et non-réponses", height=400)
    st.plotly_chart(fig_pie_global, use_container_width=True)

    # Répartition des réponses par mois
    df_responses_by_month = df_6m.groupby(['month', 'has_response']).size().unstack(fill_value=0)
    
    # Ajouter des colonnes 'Réponses' et 'Non-réponses' explicitement
    df_responses_by_month['Réponses'] = df_responses_by_month[True]  # Réponses
    df_responses_by_month['Non-réponses'] = df_responses_by_month[False]  # Non-réponses

    # Création du graphique pour chaque mois avec pie chart
    fig_pie_month = go.Figure()

    # Ajouter une trace pour chaque mois
    for month, data in df_responses_by_month.iterrows():
        fig_pie_month.add_trace(go.Pie(
            labels=['Réponses', 'Non-réponses'],
            values=[data['Réponses'], data['Non-réponses']],
            name=str(month),
            hole=0.3
        ))

    fig_pie_month.update_layout(
        title="Répartition des réponses par mois",
        height=500,
        grid=dict(rows=3, columns=2),
        showlegend=False
    )
    st.plotly_chart(fig_pie_month, use_container_width=True)

if __name__ == "__main__":
    show_dashboard()
