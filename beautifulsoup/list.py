# data treatment/BeautifulSoup/list.py  
class LinkCollector:
    def __init__(self):
        self.base_url = "..."
        self.headers = {...}
    
    def collect_links(self):
        """Collecte tous les liens des entreprises"""
        # Votre code existant
        return links

# data treatment/BeautifulSoup/filtered_list.py
class LinkFilter:
    def __init__(self):
        self.min_reviews = 1000
    
    def filter_links(self, links):
        """Filtre les liens avec >1000 reviews"""
        # Votre code existant
        return filtered_links

# data treatment/BeautifulSoup/reviews.py
class ReviewScraper:
    def __init__(self):
        self.headers = {...}
    
    def scrape_reviews(self, filtered_links):
        """Scrape les reviews des liens filtrés"""
        # Votre code existant
        return reviews

# data treatment/BeautifulSoup/main.py
def run_scraping_pipeline():
    # Initialisation
    collector = LinkCollector()
    filter = LinkFilter()
    scraper = ReviewScraper()
    
    # Pipeline
    links = collector.collect_links()
    filtered_links = filter.filter_links(links)
    reviews = scraper.scrape_reviews(filtered_links)
    
    # Sauvegarde
    save_to_csv(reviews, "data/raw/reviews.csv")