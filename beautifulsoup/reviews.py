import datetime
import requests
from bs4 import BeautifulSoup as bs
import json
import logging

# Configuration du logging
logging.basicConfig(filename='scraping_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Fonction pour extraire une date depuis une balise <time> ou <p>
def extract_date_from_tag(review, tag_name, class_name=None, is_datetime=False, experience_text=False):
    try:
        if class_name:
            tag = review.find(tag_name, class_=class_name)
        else:
            tag = review.find(tag_name)

        if tag:
            if is_datetime and 'datetime' in tag.attrs:
                return datetime.datetime.strptime(tag['datetime'][:10], "%Y-%m-%d").date()
            elif experience_text:
                # Extraire tout le texte contenu dans le <p> qui contient la date d'expérience
                return tag.text.strip()  # Récupérer tout le texte contenu dans le <p>
            else:
                return datetime.datetime.strptime(tag.text.strip(), "%d %B %Y").date()
        return None
    except Exception as e:
        logging.error(f"Erreur d'extraction de date : {e}")
        return None

# Fonction pour extraire la note à partir de l'attribut "alt" de l'image
def extract_rating_from_tag(review):
    try:
        rating_tag = review.find('div', class_='star-rating_starRating__4rrcf')
        if rating_tag:
            img = rating_tag.find('img')
            if img and 'alt' in img.attrs:
                return int(img['alt'].split(' ')[1])  # Extrait "5" de "Noté 5 sur 5 étoiles"
        return None
    except Exception as e:
        logging.error(f"Erreur d'extraction de la note : {e}")
        return None

# Fonction pour sérialiser les objets non pris en charge par JSON
def custom_json_serializer(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()  # Convertir en chaîne ISO
    raise TypeError(f"Type {type(obj)} non sérialisable")

# Chargement du fichier JSON contenant les liens des marques
with open('filtered_list.json', 'r', encoding='utf-8') as f:
    data_json = json.load(f)

# Liste pour stocker tous les avis
all_reviews = []

# Scraping
for lien_cat in set(item['categorie'] for item in data_json):
    df_marque = [item for item in data_json if item['categorie'] == lien_cat]
    for marque in df_marque:
        lien_c = marque['liens_marque']
        print(f"Scraping de la marque {lien_c} dans la catégorie {lien_cat}")

        for X in range(1, 21):  # Limite à 20 pages
            lien = f'https://fr.trustpilot.com/review/{lien_c}?page={X}'
            print(f"Scraping de la page {X} de {lien}")

            try:
                page = requests.get(lien, timeout=10)
                soup = bs(page.content, "lxml")
            except Exception as e:
                logging.error(f"Erreur lors du téléchargement de la page {X} de {lien}: {e}")
                continue

            try:
                company = soup.find('h1', class_='typography_default__hIMlQ').text.strip()
            except:
                company = None

            for avis in soup.find_all('div', class_='styles_cardWrapper__LcCPA'):
                try:
                    user_name = avis.find('span', class_='typography_heading-xxs__QKBS8').text.strip() if avis.find('span', class_='typography_heading-xxs__QKBS8') else None
                    review_title = avis.find('h2').text.strip() if avis.find('h2') else None
                    review_body = avis.find('p').text.strip() if avis.find('p') else None

                    # Extraction de la note
                    rating = extract_rating_from_tag(avis)

                    # Date d'expérience (extraction de tout le contenu du <p>)
                    experience_date = extract_date_from_tag(
                        avis, 'p',
                        class_name='typography_body-m__xgxZ_ typography_appearance-default__AAY17',
                        is_datetime=False,
                        experience_text=True  # Récupérer tout le texte du <p>
                    )

                    # Date de publication de l'avis
                    review_date = extract_date_from_tag(
                        avis, 'time',
                        class_name=None,
                        is_datetime=True
                    )

                    # Date de réponse
                    response_date = extract_date_from_tag(
                        avis, 'time',
                        class_name='typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_replyDate__Iem0_',
                        is_datetime=True
                    )

                    response_text = None
                    response_div = avis.find('div', class_='styles_content__Hl2Mi')
                    if response_div:
                        response_text = response_div.find('p').text.strip() if response_div.find('p') else None

                    # Ajouter les données de l'avis au dictionnaire
                    all_reviews.append({
                        'categorie_bis': lien_cat,
                        'company_name': lien_c,
                        'user_name': user_name,
                        'review_title': review_title,
                        'review_body': review_body,
                        'response': response_text,
                        'response_date': response_date,
                        'rating': rating,
                        'experience_date': experience_date,
                        'review_date': review_date,
                        'site_url': lien,
                        'scrap_date': datetime.datetime.now().strftime("%Y-%m-%d")
                    })
                except Exception as e:
                    logging.error(f"Erreur lors de l'extraction d'un avis : {e}")

# Sauvegarde des données dans un fichier JSON
output_path = 'reviews.json'
try:
    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(all_reviews, outfile, indent=4, ensure_ascii=False, default=custom_json_serializer)
    print(f"Scraping terminé ! Données enregistrées dans {output_path}.")
except Exception as e:
    print(f"Erreur lors de la sauvegarde des données : {e}")
    logging.error(f"Erreur lors de la sauvegarde des données : {e}")
