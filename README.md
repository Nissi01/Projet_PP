# Projet_PP
OTOULI Nissi
ZHANG Jacques
BRIET Jessy 

Reproduction d'un MyAnimeList

Cette application permet aux utilisateurs de créer un compte, d'explorer une base de données d'animes, et de gérer leur liste personnelle avec des statuts de visionnage et des notes.

## Architecture

Back-End : Python avec le micro-framework Flask.
Base de données : MySQL (version 8.0).
ORM : Flask-SQLAlchemy pour une interaction sécurisée et orientée objet avec la base de données.
Front-End : HTML/CSS/JS natif servi par l'API Flask.
DevOps : Docker & Docker Compose pour un déploiement instantané.


### Prérequis
Application : Docker Desktop(https://www.docker.com/products/docker-desktop) installé et en cours d'exécution.
Git installé.(Pour l'instant, on fait juste la version GIT)

### Démarrage
Clonez le dépôt sur votre machine locale :
   git clone https://github.com/Nissi01/Projet_PP.git
   cd Projet_PP
   docker-compose up --build
Accédez à l'application web via un navigateur :
http://localhost:5001/


### Documentation de l'API 

Animes 
GET /animes : Récupère la liste de tous les animes.
GET /animes/<id> : Récupère les détails d'un anime à cette ID.
POST /animes : Ajoute un nouvel anime.

Utilisateurs & Listes
GET /users : Liste tous les utilisateurs enregistrés.
POST /users : Crée un nouvel utilisateur (Nécessite le champ pseudo).
GET /users/<user_id>/animes : Affiche la liste personnelle d'un utilisateur.
POST /users/<user_id>/animes : Ajoute un anime à la liste de l'utilisateur (avec gestion du statut et de la note).
GET /users/<user_id>/profile : Récupère les détails du profil (bio, avatar).
POST /users/<user_id>/profile : Crée ou met à jour le profil de l'utilisateur.
