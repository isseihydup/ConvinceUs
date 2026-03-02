from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, emit
import random, string
from database import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

init_db()

TOPICS = ["Abandoned Hospital", "Dark Forest", "Empty School",
          "Haunted Church", "Silent Basement", "Dead Mall"] * 100

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("create_room")
def create_room():
    room = ''.join(random.choices(string.ascii_uppercase, k=4))
    join_room(room)
    emit("room_created", room)

@socketio.on("join_room")
def join(data):
    room = data["room"]
    name = data["name"]

    join_room(room)
    add_player(room, name)
    emit("player_joined", name, room=room)

@socketio.on("start_game")
def start_game(room):
    players = get_players(room)
    topic = random.choice(TOPICS)
    random.shuffle(players)

    for i, player in enumerate(players):
        role = "Imposter" if i == 0 else "Crew"
        assign_role(room, player, role)

    emit("game_started", topic, room=room)

@socketio.on("vote")
def vote(data):
    room = data["room"]
    voter = data["voter"]
    target = data["target"]

    cast_vote(room, voter, target)

    results = eliminate(room)
    if results:
        emit("eliminated", {"player": results[0], "role": results[1]}, room=room)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
