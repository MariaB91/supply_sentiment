import streamlit as st
import json

# Charger les données de la marque (nom, lien, etc.)
@st.cache_data
def load_trust_data():
    with open("beautifulsoup/filtered_list.json", "r", encoding="utf-8") as f:
        trust_data = json.load(f)
    
    df_trust = pd.DataFrame(trust_data)
    trust_scores = {item["marque"]: float(item.get("trust_score", "0").replace(",", ".")) for item in trust_data}
    reviews_count = {item["marque"]: int(item.get("reviews", 0)) for item in trust_data}
    links = {item["marque"]: item.get("liens_marque", "#") for item in trust_data}

    return trust_scores, reviews_count, links

# Charger les données
trust_scores, reviews_count, links = load_trust_data()

# Sélection de la marque dans la sidebar
marque_selectionnee = st.sidebar.selectbox("Sélectionner une marque :", options=list(links.keys()), index=0)

# Liens de la marque
company_url = links.get(marque_selectionnee, "#")

# Partie principale de l'app
st.title(f"📊 Dashboard d'Analyse des Avis Clients - {marque_selectionnee}")

# Informations générales (exemple de KPI)
st.subheader("📋 Informations générales")
st.write(f"Trust Score : {trust_scores.get(marque_selectionnee, 0)}")
st.write(f"Nombre total d'avis : {reviews_count.get(marque_selectionnee, 0)}")

# Affichage du lien vers l'entreprise en bas de la sidebar
with st.sidebar:
    st.markdown("----")
    if company_url != "#":
        st.markdown(f"<a href='{company_url}' target='_blank' style='background-color: #04AA6D; color: white; padding: 10px; border-radius: 5px; text-align: center; display: block;'>Visiter l'entreprise</a>", unsafe_allow_html=True)
    else:
        st.write("Aucun lien disponible pour cette marque.")
    
    # Mention "source des reviews" avec le logo Trustpilot
    st.markdown("----")
    st.markdown(
        "<p style='font-size: 14px;'>Source des reviews : <a href='https://www.trustpilot.com/' target='_blank'><img src='https://upload.wikimedia.org/wikipedia/commons/a/a2/Trustpilot_logo_2021.svg' width='100'></a></p>",
        unsafe_allow_html=True
    )

# Exemple de graphique ou autre contenu pour la page principale
st.subheader("🔹 Distribution des Avis")
# Ajoutez ici d'autres éléments graphiques ou de données, comme la distribution des avis, etc.
