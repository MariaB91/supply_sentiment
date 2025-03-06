import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from wordcloud import WordCloud
from collections import Counter
import mlflow

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
        with open('beautifulsoup/reviews.json', 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
        with open('beautifulsoup/filtered_list.json', 'r', encoding='utf-8') as f:
            trust_data = json.load(f)

        df = pd.DataFrame(reviews_data)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        trust_scores = {item['company']: float(item.get('trust_score', "0").replace(',', '.')) for item in trust_data}
        return df, trust_scores
    except FileNotFoundError as e:
        st.error(f"Erreur de chargement des fichiers: {str(e)}")
        return pd.DataFrame(), {}

@st.cache_resource
def load_model():
    try:
        model_path = "models/final_model"
        return mlflow.sklearn.load_model(model_path)
    except Exception as e:
        st.error(f"Erreur de chargement du modèle: {str(e)}")
        return None

def create_trust_gauge(trust_score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=trust_score,
        domain={'x': [0, 1], 'y': [0, 1]},
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

def show_dashboard():
    st.title("📊 Dashboard d'Analyse des Avis Clients")
    df, trust_scores = load_data()
    if df.empty:
        st.warning("Aucune donnée disponible.")
        return
    
    # Filtre par entreprise
    companies = df['company'].unique()
    selected_company = st.selectbox("Sélectionnez une entreprise", companies)
    df = df[df['company'] == selected_company]
    trust_score = trust_scores.get(selected_company, 0.0)
    
    # Affichage du trust score
    st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)
    
    # Filtre par période
    periode = st.selectbox("Période", ["7 jours", "30 jours", "12 mois"])
    today = datetime.now()
    start_date = today - timedelta(days=7 if periode == "7 jours" else 30 if periode == "30 jours" else 365)
    df = df[df['date'] >= start_date]
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre d'avis", len(df))
    col2.metric("Note moyenne", f"{df['rating'].mean():.1f}")
    col3.metric("Avis positifs", f"{(df['rating'] >= 4).mean():.1%}")
    
    # Graphiques
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.line(df, x='date', y='rating', title="Évolution des notes"))
    with col2:
        st.plotly_chart(px.histogram(df, x='rating', title="Répartition des notes"))
    
    # Word Cloud
    if 'review' in df.columns:
        text = ' '.join(df['review'].dropna())
        wordcloud = WordCloud(background_color='white').generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud)
        ax.axis('off')
        st.pyplot(fig)

def show_simulator():
    st.title("🔮 Simulateur d'Impact des Avis")
    model = load_model()
    df, trust_scores = load_data()
    selected_company = st.selectbox("Sélectionnez une entreprise", df['company'].unique())
    trust_score = trust_scores.get(selected_company, 0.0)
    df = df[df['company'] == selected_company]
    
    # Trust Score actuel
    st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)
    
    # Zone de saisie du review
    review = st.text_area("Entrez votre review :")
    if st.button("Analyser"):
        if review and model:
            prediction = model.predict([review])[0]
            df_sim = pd.concat([df, pd.DataFrame({'date': [datetime.now()], 'review': [review], 'rating': [prediction]})])
            new_avg = df_sim['rating'].mean()
            
            col1, col2 = st.columns(2)
            col1.metric("Note moyenne", f"{new_avg:.2f}", f"{new_avg - df['rating'].mean():.2f}")
            col2.metric("Avis positifs", f"{(df_sim['rating'] >= 4).mean():.1%}")
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=df['rating'], name="Avant"))
            fig.add_trace(go.Histogram(x=df_sim['rating'], name="Après"))
            st.plotly_chart(fig, use_container_width=True)

def main():
    page = st.sidebar.radio("Navigation", ["Dashboard", "Simulateur"])
    if page == "Dashboard":
        show_dashboard()
    else:
        show_simulator()

if __name__ == "__main__":
    main()
