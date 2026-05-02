import requests
import time

BASE_URL = "http://localhost:5001"

print("Début du peuplement de la base de données")

#Création des genres
genres = ["Action", "Comédie", "Aventure", "Fantasy", "Mecha", "Tranche de vie", "Drame", "Romance", "Horreur", "Science-fiction", "Mystère", "Psychologique", "Surnaturel", "Sport", "Musical", "Historique", "Guerre", "Ecchi", "Harem", "Shounen", "Shoujo", "Seinen", "Josei"]
for g in genres:
    requests.post(f"{BASE_URL}/genres", json={"name": g})
print("Genres ajoutés.")

#Création des utilisateurs
utilisateurs = ["Nissi", "Jessy", "Jacques", "Sophie", "Léo"]
for u in utilisateurs:
    requests.post(f"{BASE_URL}/users", json={"pseudo": u})
print("Utilisateurs ajoutés.")

#Création des animes
animes = [
    {
        "name": "Gintama°",
        "synopsis": "La vie déjantée de Gintoki dans un monde de samouraïs et d'aliens. Le meilleur anime de tous les temps.",
        "status": "termine",
        "cover_url": "https://myanimelist.net/images/anime/3/72078.jpg",
        "genres": ["Action", "Comédie"]
    },
    {
        "name": "Your Lie in April",
        "synopsis": "Un pianiste prodige redécouvre la musique grâce à une violoniste excentrique. Un mélange poignant de romance et de drame.",
        "status": "termine",
        "cover_url": "https://cdn.myanimelist.net/images/anime/3/67177l.jpg",
        "genres": ["Romance", "Drame", "Musical"]
    }
]

for a in animes:
    requests.post(f"{BASE_URL}/animes", json=a)
print("Animes ajoutés.")

# Récupération des IDs générés par la base de données
users_data = requests.get(f"{BASE_URL}/users").json()
animes_data = requests.get(f"{BASE_URL}/animes").json()

# On cherche l'ID d'un compte et l'ID d'un anime pour les étapes suivantes
id_user = None
for u in users_data:
    if u['pseudo'] == 'Nissi':
        id_user = u['id']
        break 

id_anime = None
for a in animes_data:
    if a['name'] == 'Gintama°':
        id_anime = a['id']
        break

# On ajoute Gintama à la liste de Nissi, avec une note de 10/10
requests.post(
    f"{BASE_URL}/users/{id_user}/animes",
    json={
        "anime_id": id_anime,
        "statut": "Termine",
        "note": 10
    }
)
print("Gintama noté 10/10 pour l'utilisateur Nissi avec succès !")
print(" Allez voir http://localhost:5001/ !")