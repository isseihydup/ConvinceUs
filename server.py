pip install flask flask-socketio eventlet flask-cors

from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, emit
import random
import sqlite3
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS players(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room TEXT,
        name TEXT,
        role TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- TOPICS ----------
TOPICS = [f"Dark {place}" for place in
          ["Hospital", "Forest", "School", "Church", "Basement", "Mall"]] * 100

# ---------- ROUTE ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- SOCKET EVENTS ----------
@socketio.on("create_room")
def create_room(data):
    room = ''.join(random.choices(string.ascii_uppercase, k=4))
    join_room(room)
    emit("room_created", room)

@socketio.on("join_room")
def on_join(data):
    room = data["room"]
    name = data["name"]

    join_room(room)

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO players (room, name, role) VALUES (?, ?, ?)",
              (room, name, ""))
    conn.commit()
    conn.close()

    emit("player_joined", name, room=room)

@socketio.on("start_game")
def start_game(room):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT name FROM players WHERE room=?", (room,))
    players = [row[0] for row in c.fetchall()]

    topic = random.choice(TOPICS)
    random.shuffle(players)

    roles = {}
    for i, player in enumerate(players):
        role = "Imposter" if i == 0 else "Crew"
        roles[player] = role
        c.execute("UPDATE players SET role=? WHERE name=? AND room=?",
                  (role, player, room))

    conn.commit()
    conn.close()

    emit("game_started", {"topic": topic, "roles": roles}, room=room)

@socketio.on("vote")
def vote(data):
    emit("vote_update", data, room=data["room"])

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
