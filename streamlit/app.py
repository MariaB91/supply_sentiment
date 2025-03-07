import streamlit as st
import pandas as pd
import json
import requests

# Charger les données de confiance à partir du fichier JSON
@st.cache_data
def load_trust_data():
    try:
        with open("beautifulsoup/filtered_list.json", "r", encoding="utf-8") as f:
            trust_data = json.load(f)
        
        if not trust_data:
            st.error("Le fichier 'filtered_list.json' est vide ou mal formaté.")
            return {}, {}, {}

        df_trust = pd.DataFrame(trust_data)
        trust_scores = {
            item["marque"]: float(item.get("trust_score", "0").replace(",", ".")) for item in trust_data
        }
        reviews_count = {
            item["marque"]: int(item.get("reviews", 0)) for item in trust_data
        }
        links = {
            item["marque"]: item.get("liens_marque", "#") for item in trust_data
        }

        return trust_scores, reviews_count, links
    
    except FileNotFoundError:
        st.error("Le fichier 'filtered_list.json' est introuvable.")
        return {}, {}, {}
    except json.JSONDecodeError:
        st.error("Le fichier 'filtered_list.json' est mal formaté.")
        return {}, {}, {}
    except Exception as e:
        st.error(f"Une erreur inattendue s'est produite : {str(e)}")
        return {}, {}, {}

# Charger les données de prédiction (Exemple ici)
@st.cache_data
def load_data():
    try:
        return pd.read_json("Prediction/dashboard_data.json")
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return pd.DataFrame()

# Charger les données de confiance et les avis
trust_scores, reviews_count, links = load_trust_data()

# Vérifier si les données de confiance sont valides
if not trust_scores:
    st.stop()

# Charger les données de l'API
df = load_data()

# Sélectionner la marque depuis la sidebar
marque_selectionnee = st.sidebar.selectbox("Sélectionner une marque :", options=df["marque"].unique(), index=0)

# Filtrer les données selon la marque sélectionnée
df_filtered = df[df["marque"] == marque_selectionnee]
trust_score = trust_scores.get(marque_selectionnee, 0.0)
total_reviews = reviews_count.get(marque_selectionnee, 0)
marque_link = links.get(marque_selectionnee, "#")

# Créer une jauge pour afficher le trust score
def create_trust_gauge(trust_score):
    import plotly.graph_objects as go
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
    return fig

# Affichage du dashboard
st.title(f"📊 Dashboard d'Analyse des Avis Clients - {marque_selectionnee}")
st.subheader("📋 Informations générales")
col1, col2, col3 = st.columns(3)
col1.metric("Nombre total d'avis", total_reviews)
col2.metric("Trust Score", round(trust_score, 2))
col3.metric("Note Moyenne", round(df_filtered["rating"].mean(), 2))

st.subheader("🔹 Trust Score")
st.plotly_chart(create_trust_gauge(trust_score), use_container_width=True)

st.subheader("📊 Distribution des Avis par Note")
import plotly.express as px
fig_rating = px.histogram(df_filtered, x="rating", nbins=5, labels={"rating": "Note"},
                          title="Répartition des Avis Clients", color_discrete_sequence=["#636EFA"])
st.plotly_chart(fig_rating, use_container_width=True)

st.subheader("📅 Évolution des Avis au Fil du Temps")
df_filtered["review_date"] = pd.to_datetime(df_filtered["review_date"], errors="coerce")
df_time_series = df_filtered.groupby("review_date").size().reset_index(name="Nombre d'avis")

fig_time_series = px.line(df_time_series, x="review_date", y="Nombre d'avis", markers=True,
                          title="Tendance des Avis Clients", color_discrete_sequence=["#EF553B"])
st.plotly_chart(fig_time_series, use_container_width=True)

# Ajouter un bouton pour visiter le site de la marque
st.sidebar.markdown(f"### 🌐 Visiter le site de {marque_selectionnee}")
if st.sidebar.button("Visiter l'entreprise"):
    st.write(f"[Cliquez ici pour visiter {marque_selectionnee}](https://{marque_link})")

# Mention de la source des reviews Trustpilot
st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Source des Avis")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/a/af/Trustpilot_logo_2020.svg", width=100)
st.sidebar.markdown("Les avis proviennent de **Trustpilot**.")

# Prédiction de la note à partir d'un commentaire
st.subheader("📝 Prédiction de la Note à partir d'un Commentaire")
commentaire = st.text_area("Entrez votre commentaire ici")

if commentaire:
    API_URL = "https://supply-sentiment.onrender.com"
    try:
        response = requests.post(API_URL, json={"commentaire": commentaire})
        if response.status_code == 200:
            predicted_rating = response.json().get("prediction", "Erreur dans la réponse")
            st.write(f"Note prédite : {predicted_rating}")
        else:
            st.error(f"Erreur de l'API : {response.json().get('error', 'Problème inconnu')}")
    except Exception as e:
        st.error(f"Erreur lors de la requête à l'API : {e}")
