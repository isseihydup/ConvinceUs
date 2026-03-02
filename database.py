import sqlite3

DB_NAME = "database.db"

# ---------- CONNECT ----------
def connect():
    return sqlite3.connect(DB_NAME)


# ---------- INITIALIZE DATABASE ----------
def init_db():
    conn = connect()
    c = conn.cursor()

    # ROOMS
    c.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_code TEXT UNIQUE,
        status TEXT DEFAULT 'waiting'
    )
    """)

    # PLAYERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_code TEXT,
        name TEXT,
        role TEXT,
        alive INTEGER DEFAULT 1,
        FOREIGN KEY(room_code) REFERENCES rooms(room_code)
    )
    """)

    # VOTES
    c.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_code TEXT,
        voter TEXT,
        target TEXT,
        FOREIGN KEY(room_code) REFERENCES rooms(room_code)
    )
    """)

    # GAME HISTORY
    c.execute("""
    CREATE TABLE IF NOT EXISTS game_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_code TEXT,
        eliminated_player TEXT,
        eliminated_role TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# ---------- ROOM FUNCTIONS ----------
def create_room(room_code):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO rooms (room_code) VALUES (?)", (room_code,))
    conn.commit()
    conn.close()


def get_players(room_code):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT name FROM players WHERE room_code=? AND alive=1", (room_code,))
    players = [row[0] for row in c.fetchall()]
    conn.close()
    return players


# ---------- PLAYER FUNCTIONS ----------
def add_player(room_code, name):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players (room_code, name, role) VALUES (?, ?, '')",
              (room_code, name))
    conn.commit()
    conn.close()


def assign_role(room_code, name, role):
    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE players SET role=? WHERE room_code=? AND name=?",
              (role, room_code, name))
    conn.commit()
    conn.close()


def get_role(room_code, name):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT role FROM players WHERE room_code=? AND name=?",
              (room_code, name))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


# ---------- VOTING ----------
def cast_vote(room_code, voter, target):
    conn = connect()
    c = conn.cursor()

    # Remove old vote if exists
    c.execute("DELETE FROM votes WHERE room_code=? AND voter=?",
              (room_code, voter))

    # Insert new vote
    c.execute("INSERT INTO votes (room_code, voter, target) VALUES (?, ?, ?)",
              (room_code, voter, target))

    conn.commit()
    conn.close()


def count_votes(room_code):
    conn = connect()
    c = conn.cursor()
    c.execute("""
    SELECT target, COUNT(*) as total
    FROM votes
    WHERE room_code=?
    GROUP BY target
    ORDER BY total DESC
    """, (room_code,))
    results = c.fetchall()
    conn.close()
    return results


def eliminate_player(room_code):
    results = count_votes(room_code)
    if not results:
        return None

    top_player = results[0][0]

    conn = connect()
    c = conn.cursor()

    # Get role
    c.execute("SELECT role FROM players WHERE room_code=? AND name=?",
              (room_code, top_player))
    role = c.fetchone()[0]

    # Mark dead
    c.execute("UPDATE players SET alive=0 WHERE room_code=? AND name=?",
              (room_code, top_player))

    # Save history
    c.execute("""
    INSERT INTO game_results (room_code, eliminated_player, eliminated_role)
    VALUES (?, ?, ?)
    """, (room_code, top_player, role))

    # Clear votes
    c.execute("DELETE FROM votes WHERE room_code=?", (room_code,))

    conn.commit()
    conn.close()

    return top_player, role


# ---------- RESET ----------
def reset_votes(room_code):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM votes WHERE room_code=?", (room_code,))
    conn.commit()
    conn.close()
