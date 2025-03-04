import json

# Chargement du fichier JSON existant
with open('list.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)


# Liste pour stocker les entrées filtrées
filtered_data = []

# Filtrage des données
for entry in data:
    reviews = entry.get('reviews')
    try:
        if reviews:  # Vérifie si la clé 'reviews' existe
            reviews = int(reviews)  # Convertit la valeur de reviews en entier
            if reviews > 10000:
                filtered_data.append(entry)
    except ValueError as e:
        # Gère les cas où les reviews ne sont pas des entiers
        print(f"Erreur de conversion des reviews: {e}")

# Écriture des données filtrées dans un nouveau fichier JSON
with open('filtered_list.json', 'w') as json_file:
    json.dump(filtered_data, json_file, indent=4)

print("Filtrage terminé. Données enregistrées en JSON.")
