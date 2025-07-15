import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_FILE = os.environ.get('CHAT_DB', 'chat.db')

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room TEXT NOT NULL,
        username TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# --- Helper Functions ---
def get_rooms():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT name, description FROM rooms')
    rooms = [{'name': row[0], 'description': row[1]} for row in c.fetchall()]
    conn.close()
    return rooms

def get_messages(room):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT username, message, timestamp FROM messages WHERE room=? ORDER BY id ASC', (room,))
    messages = [{'user': row[0], 'message': row[1], 'time': row[2]} for row in c.fetchall()]
    conn.close()
    return messages

def add_message(room, username, message):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.now().strftime('%H:%M:%S')
    c.execute('INSERT INTO messages (room, username, message, timestamp) VALUES (?, ?, ?, ?)',
              (room, username, message, timestamp))
    conn.commit()
    conn.close()
    return {'user': username, 'message': message, 'time': timestamp}

def add_room(name, description):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO rooms (name, description) VALUES (?, ?)', (name, description))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Room already exists
    conn.close()

# --- API Endpoints ---
@app.route('/rooms', methods=['GET'])
def api_rooms():
    return jsonify(get_rooms())

@app.route('/rooms/<room>/messages', methods=['GET'])
def api_get_messages(room):
    return jsonify(get_messages(room))

@app.route('/rooms/<room>/messages', methods=['POST'])
def api_post_message(room):
    data = request.get_json()
    username = data.get('user', 'Anonymous')
    message = data.get('message', '')
    if not message:
        return jsonify({'error': 'Empty message'}), 400
    msg = add_message(room, username, message)
    return jsonify(msg)

@app.route('/rooms', methods=['POST'])
def api_add_room():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    if not name:
        return jsonify({'error': 'Room name required'}), 400
    add_room(name, description)
    return jsonify({'success': True})

# --- Default Rooms (add on startup) ---
DEFAULT_ROOMS = [
    ("Bitcoin-Talk", "Bitcoin discussions and price analysis"),
    ("Ethereum-Dev", "Ethereum development and smart contracts"),
    ("DeFi-Trading", "Decentralized finance trading strategies"),
    ("NFT-Collectors", "NFT trading and collection discussions"),
    ("Technical-Analysis", "Technical analysis and chart patterns"),
    ("Crypto-News", "Latest cryptocurrency news and updates"),
    ("Mining-Pools", "Mining operations and pool discussions"),
    ("Security-Privacy", "Crypto security and privacy discussions"),
    ("Regulatory-News", "Crypto regulations and legal discussions"),
    ("Memecoins", "Meme coin discussions and trends"),
    ("Stablecoins", "Stablecoin trading and peg discussions"),
    ("Liquidity-Mining", "Liquidity mining and yield farming strategies"),
    ("Options-Trading", "Crypto options and derivatives trading"),
    ("Futures-Trading", "Crypto futures and perpetual contracts"),
    ("Fundamental-Analysis", "Fundamental analysis and project evaluation"),
    ("Sentiment-Analysis", "Market sentiment and social media analysis"),
    ("Whale-Watching", "Large wallet movements and whale tracking"),
    ("Institutional-Adoption", "Institutional crypto adoption and news"),
    ("Privacy-Coins", "Privacy-focused cryptocurrencies discussion"),
    ("Staking-Validators", "Staking and validator operations"),
    ("Darknet-Market", "Anonymous trading and privacy discussions"),
    ("ICO-IDO-Launches", "Initial coin offerings and token launches"),
    ("Metaverse-Gaming", "Metaverse and blockchain gaming discussions"),
    ("AI-Crypto", "Artificial Intelligence in crypto applications"),
    ("Green-Crypto", "Environmentally friendly crypto projects"),
    ("Quantum-Resistance", "Quantum-resistant cryptography discussions"),
    ("Central-Bank-Digital-Currencies", "CBDC discussions and implications"),
    ("Crypto-Education", "Educational content and learning resources"),
    ("Bug-Bounties", "Bug bounty programs and security research"),
    ("Crypto-Jobs", "Job opportunities in the crypto space"),
    ("Crypto-Philosophy", "Philosophical discussions about crypto and decentralization"),
    ("Cross-Chain-Bridges", "Cross-chain bridge discussions and risks"),
    ("DAO-Governance", "DAO governance and voting discussions"),
]

def ensure_default_rooms():
    for name, desc in DEFAULT_ROOMS:
        add_room(name, desc)

if __name__ == '__main__':
    init_db()
    ensure_default_rooms()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 