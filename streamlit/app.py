import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration de la page
st.set_page_config(page_title="Analyse des Avis Clients", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_json('merged_data.json', lines=True)

        # Vérification des colonnes essentielles
        required_columns = {"review_title", "review_body", "rating", "reviews", "pays", "trust_score", 
                            "diff_experience_review", "diff_review_response", "review_month", "review_day"}
        if not required_columns.issubset(df.columns):
            st.error("Le fichier JSON ne contient pas toutes les colonnes nécessaires.")
            return pd.DataFrame()

        return df

    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return pd.DataFrame()

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
    df = load_data()
    if df.empty:
        st.warning("Aucune donnée disponible.")
        return

    # Filtrage par pays
    pays_list = df["pays"].unique()
    selected_pays = st.sidebar.selectbox("Sélectionnez un pays", options=pays_list)

    df_filtered = df[df["pays"] == selected_pays]

    # Trust Score moyen
    trust_score_moyen = df_filtered["trust_score"].mean()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(create_trust_gauge(trust_score_moyen), use_container_width=True)

    # Graphique des avis par jour du mois
    st.subheader("📅 Répartition des Avis par Jour du Mois")
    reviews_by_day = df_filtered.groupby("review_day").size()

    if not reviews_by_day.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x=reviews_by_day.index, y=reviews_by_day.values, palette="Blues", ax=ax)
        ax.set_title("Nombre d'Avis par Jour du Mois", fontsize=16)
        ax.set_xlabel("Jour du Mois", fontsize=14)
        ax.set_ylabel("Nombre d'Avis", fontsize=14)
        st.pyplot(fig)
    else:
        st.warning("Aucune donnée d'avis pour ce pays.")

    # Graphique des avis par rating
    st.subheader("⭐ Répartition des Avis par Note")
    reviews_by_rating = df_filtered.groupby("rating").size()

    if not reviews_by_rating.empty:
        fig, ax = plt.subplots()
        ax.pie(reviews_by_rating, labels=reviews_by_rating.index, autopct='%1.1f%%', 
               startangle=140, colors=sns.color_palette('Blues', len(reviews_by_rating)))
        ax.set_title("Distribution des Avis par Note")
        st.pyplot(fig)
    else:
        st.warning("Aucune donnée de répartition des avis par note.")

    # Temps entre l'expérience et le review
    st.subheader("⏳ Délai entre l'Expérience et l'Avis")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(df_filtered["diff_experience_review"], bins=10, kde=True, color="blue", ax=ax)
    ax.set_title("Distribution du Temps entre l'Expérience et l'Avis", fontsize=16)
    ax.set_xlabel("Jours", fontsize=14)
    ax.set_ylabel("Nombre d'Avis", fontsize=14)
    st.pyplot(fig)

    # Temps entre le review et la réponse
    st.subheader("⏳ Délai entre l'Avis et la Réponse")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(df_filtered["diff_review_response"], bins=10, kde=True, color="red", ax=ax)
    ax.set_title("Distribution du Temps entre l'Avis et la Réponse", fontsize=16)
    ax.set_xlabel("Jours", fontsize=14)
    ax.set_ylabel("Nombre d'Avis", fontsize=14)
    st.pyplot(fig)

if __name__ == "__main__":
    show_dashboard()
