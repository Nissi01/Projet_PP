from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import time
from flask_cors import CORS

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@db/myanimelist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── Table de liaison anime ↔ genre ──────────────────────────────────────────
anime_genres = db.Table('anime_genres',
    db.Column('anime_id', db.Integer, db.ForeignKey('animes.id'), primary_key=True),
    db.Column('genre_name', db.String(50), db.ForeignKey('genres.name'), primary_key=True)
)

class Anime(db.Model):
    __tablename__ = 'animes'
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    synopsis = db.Column(db.Text)
    status   = db.Column(db.String(20), default='en cours')
    genres   = db.relationship('Genre', secondary=anime_genres, backref='animes', lazy='subquery')

class User(db.Model):
    __tablename__ = 'users'
    id     = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(50), nullable=False, unique=True)

class Genre(db.Model):
    __tablename__ = 'genres'
    name = db.Column(db.String(50), primary_key=True)

class UserAnime(db.Model):
    __tablename__ = 'user_animes'
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'),  primary_key=True)
    anime_id = db.Column(db.Integer, db.ForeignKey('animes.id'), primary_key=True)
    statut   = db.Column(db.String(30), default='À voir')
    note     = db.Column(db.Integer, nullable=True)  # 1-10
    user     = db.relationship('User',  backref='liste_animes')
    anime    = db.relationship('Anime', backref='dans_listes')


def anime_to_dict(a):
    return {
        "id": a.id, "name": a.name,
        "synopsis": a.synopsis, "status": a.status,
        "genres": [g.name for g in a.genres],
    }

def user_anime_to_dict(ua):
    return {
        "user_id":  ua.user_id,
        "anime_id": ua.anime_id,
        "anime_name": ua.anime.name,
        "anime_status": ua.anime.status,
        "anime_genres": [g.name for g in ua.anime.genres],
        "statut": ua.statut,
        "note":   ua.note,
    }


# ─── Frontend ─────────────────────────────────────────────────────────────────
@app.route('/')
def frontend():
    return send_from_directory('static', 'index.html')


# ─── API Anime ────────────────────────────────────────────────────────────────
@app.route('/animes', methods=['GET'])
def get_animes():
    return jsonify([anime_to_dict(a) for a in Anime.query.all()]), 200

@app.route('/animes/<int:id>', methods=['GET'])
def get_anime(id):
    a = Anime.query.get(id)
    if a: return jsonify(anime_to_dict(a)), 200
    return jsonify({"erreur": "anime non trouvé"}), 404

@app.route('/animes', methods=['POST'])
def add_anime():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Le champ 'name' est obligatoire"}), 400
    a = Anime(name=data['name'], synopsis=data.get('synopsis', ''), status=data.get('status', 'en cours'))
    for gn in data.get('genres', []):
        g = Genre.query.get(gn)
        if g: a.genres.append(g)
    db.session.add(a)
    db.session.commit()
    return jsonify(anime_to_dict(a)), 201

@app.route('/animes/<int:id>', methods=['PUT'])
def update_anime(id):
    a = Anime.query.get(id)
    if not a: return jsonify({"erreur": "anime non trouvé"}), 404
    data = request.get_json()
    a.name = data.get('name', a.name)
    a.synopsis = data.get('synopsis', a.synopsis)
    a.status = data.get('status', a.status)
    if 'genres' in data:
        a.genres = []
        for gn in data['genres']:
            g = Genre.query.get(gn)
            if g: a.genres.append(g)
    db.session.commit()
    return jsonify(anime_to_dict(a)), 200

@app.route('/animes/<int:id>', methods=['DELETE'])
def delete_anime(id):
    a = Anime.query.get(id)
    if not a: return jsonify({"error": "Anime non trouvé"}), 404
    db.session.delete(a)
    db.session.commit()
    return jsonify({"message": f"'{a.name}' supprimé"}), 200


# ─── API User ─────────────────────────────────────────────────────────────────
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify([{"id": u.id, "pseudo": u.pseudo} for u in User.query.all()]), 200

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    if not data or 'pseudo' not in data:
        return jsonify({"error": "Le pseudo est obligatoire"}), 400
    u = User(pseudo=data['pseudo'])
    try:
        db.session.add(u)
        db.session.commit()
        return jsonify({"message": f"Utilisateur {u.pseudo} créé !"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Ce pseudo existe peut-être déjà."}), 400

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    u = User.query.get(id)
    if not u: return jsonify({"error": "Utilisateur non trouvé"}), 404
    db.session.delete(u)
    db.session.commit()
    return jsonify({"message": f"'{u.pseudo}' supprimé"}), 200


# ─── API Liste utilisateur ────────────────────────────────────────────────────
@app.route('/users/<int:user_id>/animes', methods=['GET'])
def get_user_animes(user_id):
    u = User.query.get(user_id)
    if not u: return jsonify({"error": "Utilisateur non trouvé"}), 404
    return jsonify([user_anime_to_dict(ua) for ua in u.liste_animes]), 200

@app.route('/users/<int:user_id>/animes', methods=['POST'])
def add_user_anime(user_id):
    u = User.query.get(user_id)
    if not u: return jsonify({"error": "Utilisateur non trouvé"}), 404
    data = request.get_json()
    if not data or 'anime_id' not in data:
        return jsonify({"error": "anime_id requis"}), 400
    existing = UserAnime.query.get((user_id, data['anime_id']))
    if existing:
        return jsonify({"error": "Cet anime est déjà dans la liste"}), 400
    ua = UserAnime(
        user_id=user_id,
        anime_id=data['anime_id'],
        statut=data.get('statut', 'À voir'),
        note=data.get('note', None)
    )
    db.session.add(ua)
    db.session.commit()
    return jsonify(user_anime_to_dict(ua)), 201

@app.route('/users/<int:user_id>/animes/<int:anime_id>', methods=['PUT'])
def update_user_anime(user_id, anime_id):
    ua = UserAnime.query.get((user_id, anime_id))
    if not ua: return jsonify({"error": "Entrée non trouvée"}), 404
    data = request.get_json()
    ua.statut = data.get('statut', ua.statut)
    if 'note' in data:
        note = data['note']
        if note is not None and not (1 <= int(note) <= 10):
            return jsonify({"error": "La note doit être entre 1 et 10"}), 400
        ua.note = note
    db.session.commit()
    return jsonify(user_anime_to_dict(ua)), 200

@app.route('/users/<int:user_id>/animes/<int:anime_id>', methods=['DELETE'])
def delete_user_anime(user_id, anime_id):
    ua = UserAnime.query.get((user_id, anime_id))
    if not ua: return jsonify({"error": "Entrée non trouvée"}), 404
    db.session.delete(ua)
    db.session.commit()
    return jsonify({"message": "Retiré de la liste"}), 200


# ─── API Genre ────────────────────────────────────────────────────────────────
@app.route('/genres', methods=['GET'])
def get_genres():
    return jsonify([{"name": g.name} for g in Genre.query.all()]), 200

@app.route('/genres', methods=['POST'])
def add_genre():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Le champ 'name' est obligatoire"}), 400
    g = Genre(name=data['name'])
    try:
        db.session.add(g)
        db.session.commit()
        return jsonify({"message": f"Genre '{g.name}' ajouté !"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Ce genre existe déjà."}), 400


# ─── Lancement ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    connected = False
    while not connected:
        try:
            with app.app_context():
                db.create_all()
            connected = True
        except Exception as e:
            print("En attente de MySQL...")
            time.sleep(2)
    app.run(host="0.0.0.0", port=5001, debug=True)
