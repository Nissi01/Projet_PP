from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@db/myanimelist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Anime(db.Model):
    __tablename__ = 'animes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    synopsis = db.Column(db.Text)
    status = db.Column(db.String(20), default='en cours')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(50), nullable=False, unique=True)

class Genre(db.Model):
    __tablename__ = 'genres'
    name = db.Column(db.String(50), nullable=False, unique=True)


@app.route('/')
def home():
    return jsonify({"message": "Bienvenue sur l'API MyAnimeList !"}), 200

# API anime
@app.route('/animes/<int:id>', methods=['GET'])
def get_anime(id):
   
    anime = Anime.query.get(id) 

    if anime:
        return jsonify({
            "id": anime.id,
            "name": anime.name,
            "synopsis": anime.synopsis,
            "status": anime.status
        }), 200
    
    return jsonify({"erreur":"cette anime n'existe pas"}), 404

@app.route('/animes/<int:id>', methods=['PUT'])
def update_anime(id):
    # 1. On cherche l'anime dans la base
    anime = Anime.query.get(id) 

    # 2. Si l'anime n'existe pas, on s'arrête là
    if not anime:
        return jsonify({"erreur": "anime non trouvé"}), 404

    # 3. On récupère les données envoyées par l'utilisateur
    data = request.get_json()

    # 4. On met à jour les champs (en gardant l'ancienne valeur si le champ est absent)
    anime.name = data.get('name', anime.name)
    anime.synopsis = data.get('synopsis', anime.synopsis)
    anime.status = data.get('status', anime.status)

    # 5. On enregistre les modifications dans la base de données
    db.session.commit()

    # 6. On retourne l'objet mis à jour
    return jsonify({
        "id": anime.id,
        "name": anime.name,
        "synopsis": anime.synopsis,
        "status": anime.status
    }), 200

# Avoir la liste entiere des animes
@app.route('/animes', methods=['GET'])
def get_animes():
    result = []
    animes = Anime.query.all() # Récupère tous les animes de la base
    for a in animes:
        result.append({
            "id": a.id,
            "name": a.name,
            "synopsis": a.synopsis,
            "status": a.status
        })
    return jsonify(result), 200

# Ajouter un anime
@app.route('/animes', methods=['POST'])
def add_anime():
    data = request.get_json()
 
    if not data or not 'name' in data:
        return jsonify({"error": "Le champ 'name' est obligatoire"}), 400
        
    nouveau_anime = Anime(
        name=data['name'], 
        synopsis=data.get('synopsis', ''), 
        status=data.get('status', 'en cours')
    )
    
    db.session.add(nouveau_anime) 
    db.session.commit()           
    
    return jsonify({"message": "Anime ajouté avec succès !"}), 201

# Supprimer un anime
@app.route('/animes/<int:anime_id>', methods=['DELETE'])
def delete_anime(anime_id):
    del_anime = Anime.query.get(anime_id)
    
    if not del_anime:
        return jsonify({"error": "Anime non trouvé"}), 404
        
    db.session.delete(del_anime)
    db.session.commit()
    
    return jsonify({"message": f"L'anime {del_anime.name} a été supprimé avec succès !"}), 200

# API User 
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = next((s for s in User if s['id']==id), None)
    if user:
        return jsonify(user), 201
    return jsonify({"erreur : cette utilisateur n'existe pas"}), 404

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = next((s for s in User if s['id']==id), None)
    if not user:
        return jsonify({"erreur : cette utilisateur n'existe pas"}), 404
    data=request.get_json()
    user.update(data)
    return jsonify(user)

# Avoir la liste entiere des utilisateurs
@app.route('/users', methods=['GET'])
def get_users():
    result = []
    users = User.query.all()
    for a in users:
        result.append({
            "id": a.id,
            "pseudo": a.pseudo,
        })
    return jsonify(result), 200

# Ajouter un user
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    
    if not data or not 'pseudo' in data:
        return jsonify({"error": "Le pseudo est obligatoire"}), 400
        
    nouveau_user = User(pseudo=data['pseudo'])
    
    try:
        db.session.add(nouveau_user)
        db.session.commit()
        return jsonify({"message": f"Utilisateur {nouveau_user.pseudo} créé !"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Ce pseudo existe peut-être déjà."}), 400
    
# Supprimer un user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    del_user = User.query.get(user_id)
    
    if not del_user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
        
    db.session.delete(del_user)
    db.session.commit()
    
    return jsonify({"message": f"L'utilisateur {del_user.pseudo} a été supprimé avec succès !"}), 200

# --- LANCEMENT DU SERVEUR ---
if __name__ == '__main__':
    # Force Flask à écouter sur toutes les interfaces pour Docker
    app.run(host="0.0.0.0", port=5001, debug=True)
