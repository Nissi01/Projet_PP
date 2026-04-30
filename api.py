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




@app.route('/')
def home():
    return jsonify({"message": "Bienvenue sur l'API MyAnimeList !"}), 200

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
    
    return jsonify({"erreur:cette anime n'existe pas"}), 404

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


# --- LANCEMENT DU SERVEUR ---
if __name__ == '__main__':
    # Force Flask à écouter sur toutes les interfaces pour Docker
    app.run(host="0.0.0.0", port=5001, debug=True)