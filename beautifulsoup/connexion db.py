from sqlalchemy import create_engine

# Chemin de votre base SQLite
db_path = r"C:\Users\mbouc\Desktop\db\trustpilot.db"

# Créer une connexion à la base
engine = create_engine(f"sqlite:///{db_path}")

# Vérifier la connexion
try:
    with engine.connect() as connection:
        print("Connexion réussie à la base de données")
except Exception as e:
    print(f"Erreur de connexion : {e}")
