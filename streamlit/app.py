import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Analyse des Avis Clients", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_json('beautifulsoup/merged_data.json')

        # Conversion des dates
        df["review_date"] = pd.to_datetime(df["review_date"], errors='coerce')
        df["scrap_date"] = pd.to_datetime(df["scrap_date"], errors='coerce')

        # Extraction de la vraie date d'expérience
        df["experience_date"] = df["experience_date"].str.extract(r'(\d{2} \w+ \d{4})')[0]
        df["experience_date"] = pd.to_datetime(df["experience_date"], format="%d %B %Y", errors='coerce')

        # Calcul des différences de jours
        df["diff_experience_review"] = (df["review_date"] - df["experience_date"]).dt.days
        df["diff_review_response"] = (pd.to_datetime(df["response_date"], errors='coerce') - df["review_date"]).dt.days

        return df

    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return pd.DataFrame()

def show_dashboard():
    st.title("📊 Dashboard d'Analyse des Avis Clients")

    # Charger les données
    df = load_data()
    if df.empty:
        st.warning("Aucune donnée disponible.")
        return

    # Filtrage par entreprise
    companies = df["company_name"].unique()
    selected_company = st.sidebar.selectbox("Sélectionnez une entreprise", options=companies)

    df_filtered = df[df["company_name"] == selected_company]

    # Indicateurs Clés
    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Nombre total d'avis", len(df_filtered))
    col2.metric("⭐ Note Moyenne", round(df_filtered["rating"].mean(), 2))
    col3.metric("⏳ Délai Moyen Expérience -> Avis", f"{df_filtered['diff_experience_review'].mean():.1f} jours")

    # Graphique de répartition des avis par note
    st.subheader("⭐ Répartition des Avis par Note")
    reviews_by_rating = df_filtered.groupby("rating").size()

    if not reviews_by_rating.empty:
        fig, ax = plt.subplots()
        ax.pie(reviews_by_rating, labels=reviews_by_rating.index, autopct='%1.1f%%',
               startangle=140, colors=sns.color_palette('Blues', len(reviews_by_rating)))
        ax.set_title("Distribution des Avis par Note")
        st.pyplot(fig)
    else:
        st.warning("Aucune donnée d'avis pour cette entreprise.")

    # Distribution du délai entre l'expérience et l'avis
    st.subheader("⏳ Délai entre l'Expérience et l'Avis")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(df_filtered["diff_experience_review"].dropna(), bins=10, kde=True, color="blue", ax=ax)
    ax.set_title("Distribution du Temps entre l'Expérience et l'Avis", fontsize=16)
    ax.set_xlabel("Jours", fontsize=14)
    ax.set_ylabel("Nombre d'Avis", fontsize=14)
    st.pyplot(fig)

    # Analyse des réponses entreprises
    st.subheader("📢 Réponses aux Avis")
    response_counts = df_filtered["response"].notna().value_counts()

    fig, ax = plt.subplots()
    ax.pie(response_counts, labels=["Sans réponse", "Répondu"], autopct='%1.1f%%',
           startangle=140, colors=["gray", "green"])
    ax.set_title("Répartition des Avis avec/sans Réponse")
    st.pyplot(fig)

    if df_filtered["diff_review_response"].notna().sum() > 0:
        st.subheader("⏳ Temps de Réponse de l'Entreprise")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.histplot(df_filtered["diff_review_response"].dropna(), bins=10, kde=True, color="red", ax=ax)
        ax.set_title("Distribution du Temps de Réponse de l'Entreprise", fontsize=16)
        ax.set_xlabel("Jours", fontsize=14)
        ax.set_ylabel("Nombre d'Avis", fontsize=14)
        st.pyplot(fig)

if __name__ == "__main__":
    show_dashboard()
