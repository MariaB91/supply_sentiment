import json
from list import LinkCollector
from filtered_list import LinkFilter
from reviews import ReviewScraper

def run_scraping_pipeline():
    # Initialisation des classes
    collector = LinkCollector()
    filter = LinkFilter()
    scraper = ReviewScraper()

    # 1. Collecte des liens des entreprises
    category_url = "https://www.trustpilot.com/categories"  # Remplacer par l'URL de catégorie spécifique
    links = collector.collect_links(category_url)

    # 2. Filtrage des entreprises avec plus de 10 000 avis
    filtered_links = filter.filter_links(links)

    # 3. Scraping des avis
    reviews = scraper.scrape_reviews(filtered_links)

    # 4. Sauvegarde des données dans un fichier JSON
    output_path = "reviews.json"
    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(reviews, outfile, indent=4, ensure_ascii=False)
        print(f"Scraping terminé ! Données enregistrées dans {output_path}.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données : {e}")

if __name__ == "__main__":
    run_scraping_pipeline()