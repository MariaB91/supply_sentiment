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
    page_title="Analyse des Avis Clients",
    page_icon="📊",
    layout="wide"
)

# Chargement des données et du modèle
@st.cache_data
def load_data():
    """Charge les données depuis les fichiers JSON"""
    try:
        # Chargement des reviews
        with open('data treatment/beautifulsoup/reviews.json', 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
        
        # Chargement du trust score
        with open('data treatment/beautifulsoup/filtered_list.json', 'r', encoding='utf-8') as f:
            trust_data = json.load(f)
            trust_score = trust_data.get('trust_score', 0.0)
        
        # Conversion en DataFrame
        df = pd.DataFrame(reviews_data)
        
        # Conversion des dates si nécessaire
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        return df, trust_score
        
    except FileNotFoundError as e:
        st.error(f"Erreur de chargement des fichiers: {str(e)}")
        return pd.DataFrame(), 0.0

@st.cache_resource
def load_model():
    """Charge le modèle de prédiction"""
    try:
        model_path = "models/final_model"
        return mlflow.sklearn.load_model(model_path)
    except Exception as e:
        st.error(f"Erreur de chargement du modèle: {str(e)}")
        return None

def create_trust_gauge(trust_score, reference_score=None):
    """Crée une jauge pour visualiser le trust score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta" if reference_score else "gauge+number",
        value = trust_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Trust Score", 'font': {'size': 24}},
        delta = {'reference': reference_score} if reference_score else None,
        gauge = {
            'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 0.3], 'color': '#FF4B4B'},
                {'range': [0.3, 0.7], 'color': '#FFA500'},
                {'range': [0.7, 1], 'color': '#04AA6D'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.7}}))
    
    fig.update_layout(
        paper_bgcolor = "white",
        height=300
    )
    return fig

def get_top_words(texts, n=10):
    """Extrait les n mots les plus fréquents"""
    words = ' '.join(texts).lower().split()
    return Counter(words).most_common(n)

def predict_rating(text, model):
    """Prédit le rating pour un nouveau commentaire"""
    if model is None:
        return 0, [0, 0, 0, 0, 0]
    prediction = model.predict([text])[0]
    probas = model.predict_proba([text])[0]
    return prediction, probas

def create_trend_chart(df, metric, title):
    """Crée un graphique de tendance"""
    fig = px.line(
        df,
        x='date',
        y=metric,
        title=title
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=metric.capitalize(),
        showlegend=True
    )
    return fig

def show_dashboard():
    st.title("📊 Dashboard d'Analyse des Avis Clients")
    
    # Chargement des données
    df, trust_score = load_data()
    
    if df.empty:
        st.warning("Aucune donnée n'est disponible pour l'analyse.")
        return
    
    # Affichage du trust score
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(
            create_trust_gauge(trust_score),
            use_container_width=True
        )
    
    # Filtres temporels
    col1, col2 = st.columns(2)
    with col1:
        periode = st.selectbox(
            "Période d'analyse",
            ["7 derniers jours", "30 derniers jours", "12 derniers mois"]
        )
    
    # Calcul de la période
    today = datetime.now()
    if periode == "7 derniers jours":
        start_date = today - timedelta(days=7)
        freq = 'D'
    elif periode == "30 derniers jours":
        start_date = today - timedelta(days=30)
        freq = 'W'
    else:
        start_date = today - timedelta(days=365)
        freq = 'M'
    
    df_period = df[df['date'] >= start_date]
    
    # KPIs principaux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Nombre total d'avis",
            len(df_period),
            f"{len(df_period) - len(df[df['date'] >= start_date - timedelta(days=7)])}"
        )
    
    with col2:
        avg_rating = df_period['rating'].mean()
        st.metric(
            "Note moyenne",
            f"{avg_rating:.1f}",
            f"{(avg_rating - df[df['date'] >= start_date - timedelta(days=7)]['rating'].mean()):.1f}"
        )
    
    with col3:
        positive_ratio = (df_period['rating'] >= 4).mean()
        st.metric(
            "Ratio d'avis positifs",
            f"{positive_ratio:.1%}",
            f"{(positive_ratio - (df[df['date'] >= start_date - timedelta(days=7)]['rating'] >= 4).mean()):.1%}"
        )
    
    with col4:
        response_rate = df_period['reponse'].notna().mean()
        st.metric(
            "Taux de réponse",
            f"{response_rate:.1%}",
            f"{(response_rate - df[df['date'] >= start_date - timedelta(days=7)]['reponse'].notna().mean()):.1%}"
        )
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            create_trend_chart(
                df_period.groupby(pd.Grouper(key='date', freq=freq))['rating'].mean().reset_index(),
                'rating',
                "Évolution des notes dans le temps"
            ),
            use_container_width=True
        )
    
    with col2:
        fig_dist = px.histogram(
            df_period,
            x='rating',
            title="Distribution des notes"
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    
    # Word Cloud et Top mots
    if 'commentaire' in df_period.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            wordcloud = WordCloud(background_color='white').generate(' '.join(df_period['commentaire'].fillna('')))
            fig, ax = plt.subplots()
            ax.imshow(wordcloud)
            ax.axis('off')
            st.pyplot(fig)
        
        with col2:
            top_words = get_top_words(df_period['commentaire'].fillna(''))
            fig_words = px.bar(
                x=[word for word, _ in top_words],
                y=[count for _, count in top_words],
                title="Top 10 mots les plus fréquents"
            )
            st.plotly_chart(fig_words, use_container_width=True)

def show_simulator():
    st.title("🔮 Simulateur d'Impact des Avis")
    
    # Chargement du modèle et des données
    model = load_model()
    df, trust_score = load_data()
    
    # Trust Score actuel
    current_trust = trust_score
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(
            create_trust_gauge(current_trust),
            use_container_width=True
        )
    
    # Zone de saisie du commentaire
    commentaire = st.text_area("Entrez votre commentaire :")
    
    if st.button("Analyser"):
        if commentaire:
            # Prédiction
            prediction, probas = predict_rating(commentaire, model)
            
            # Affichage du résultat
            st.subheader("Résultat de l'analyse")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Note prédite", f"{prediction} ⭐")
                
            with col2:
                st.metric("Confiance", f"{max(probas):.1%}")
            
            # Simulation avec le nouveau commentaire
            df_sim = df.copy()
            df_sim = pd.concat([
                df_sim,
                pd.DataFrame({
                    'date': [datetime.now()],
                    'commentaire': [commentaire],
                    'rating': [prediction]
                })
            ])
            
            # Impact sur les KPIs
            col1, col2, col3 = st.columns(3)
            
            with col1:
                old_avg = df['rating'].mean()
                new_avg = df_sim['rating'].mean()
                st.metric(
                    "Note moyenne",
                    f"{new_avg:.2f}",
                    f"{new_avg - old_avg:.2f}"
                )
            
            with col2:
                old_positive = (df['rating'] >= 4).mean()
                new_positive = (df_sim['rating'] >= 4).mean()
                st.metric(
                    "Ratio d'avis positifs",
                    f"{new_positive:.1%}",
                    f"{(new_positive - old_positive):.1%}"
                )
            
            # Visualisation de l'impact
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=df['rating'],
                name="Distribution actuelle",
                opacity=0.75
            ))
            fig.add_trace(go.Histogram(
                x=df_sim['rating'],
                name="Après le nouveau commentaire",
                opacity=0.75
            ))
            fig.update_layout(
                title="Impact sur la distribution des notes",
                barmode='overlay'
            )
            st.plotly_chart(fig, use_container_width=True)

def main():
    # Sidebar pour la navigation
    page = st.sidebar.radio("Navigation", ["Dashboard", "Simulateur"])
    
    if page == "Dashboard":
        show_dashboard()
    else:
        show_simulator()

if __name__ == "__main__":
    main()
