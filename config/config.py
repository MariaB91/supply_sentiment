import os
from pathlib import Path

# Chemins du projet
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
MLFLOW_DIR = PROJECT_ROOT / "mlflow"

# Création des dossiers nécessaires
for dir_path in [DATA_DIR, MODELS_DIR, MLFLOW_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Configuration MongoDB
MONGO_CONFIG = {
    "host": "localhost",
    "port": 27017,
    "db_name": "supply_sentiment",
    "collection_name": "raw_reviews"
}

# Configuration Elasticsearch
ES_CONFIG = {
    "host": "localhost",
    "port": 9200,
    "index_name": "processed_reviews"
}

# Configuration MLflow
MLFLOW_TRACKING_URI = "sqlite:///mlflow/mlflow.db"
EXPERIMENT_NAME = "sentiment_analysis"