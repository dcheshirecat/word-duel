import random
import string
import urllib.request
import urllib.parse
import json
import threading

# Firebase project details
PROJECT_ID = "thewordgame-2c3ec"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

def _request(method, url, data=None):
    """Make a REST request to Firebase."""
    try:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req_data = json.dumps(data).encode() if data else None
        req = urllib.request.Request(
            url,
            data=req_data,
            method=method,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Firebase request error: {e}")
        return None

def _to_firestore(value):
    """Convert Python value to Firestore format."""
    if isinstance(value, str):
        return {"stringValue": value}
    elif isinstance(value, bool):
        return {"booleanValue": value}
    elif isinstance(value, int):
        return {"integerValue": str(value)}
    elif isinstance(value, list):
        return {"arrayValue": {"values": [_to_firestore(v) for v in value]}}
    elif isinstance(value, dict):
        return {"mapValue": {"fields": {k: _to_firestore(v) for k, v in value.items()}}}
    elif value is None:
        return {"nullValue": None}
    return {"stringValue": str(value)}

def _from_firestore(fields):
    """Convert Firestore format to Python dict."""
    result = {}
    for key, value in fields.items():
        if "stringValue" in value:
            result[key] = value["stringValue"]
        elif "booleanValue" in value:
            result[key] = value["booleanValue"]
        elif "integerValue" in value:
            result[key] = int(value["integerValue"])
        elif "arrayValue" in value:
            values = value["arrayValue"].get("values", [])
            result[key] = [_from_firestore_value(v) for v in values]
        elif "mapValue" in value:
            result[key] = _from_firestore(value["mapValue"].get("fields", {}))
        elif "nullValue" in value:
            result[key] = None
    return result

def _from_firestore_value(value):
    """Convert a single Firestore value."""
    if "stringValue" in value:
        return value["stringValue"]
    elif "booleanValue" in value:
        return value["booleanValue"]
    elif "integerValue" in value:
        return int(value["integerValue"])
    elif "arrayValue" in value:
        return [_from_firestore_value(v) for v in value["arrayValue"].get("values", [])]
    return None

def generate_game_code():
    return ''.join(random.choices(string.digits, k=4))

def create_game(language="en"):
    code = generate_game_code()
    data = {
        "fields": {
            k: _to_firestore(v) for k, v in {
                "code": code,
                "language": language,
                "status": "waiting",
                "word_p1": "",
                "word_p2": "",
                "guesses_p1": [],
                "feedback_p1": [],
                "guesses_p2": [],
                "feedback_p2": [],
                "turn": "p1",
                "winner": "",
            }.items()
        }
    }
    url = f"{BASE_URL}/games/{code}"
    result = _request("PATCH", url, data)
    if result:
        return code
    return None

def join_game(code):
    url = f"{BASE_URL}/games/{code}"
    result = _request("GET", url)
    if result and "fields" in result:
        return _from_firestore(result["fields"])
    return None

def set_word(code, player, word):
    field = f"word_{player}"
    game = join_game(code)
    if not game:
        return
    game[field] = word
    other_field = "word_p2" if player == "p1" else "word_p1"
    if game.get(other_field):
        game["status"] = "playing"
    url = f"{BASE_URL}/games/{code}"
    data = {"fields": {k: _to_firestore(v) for k, v in game.items()}}
    _request("PATCH", url, data)

def submit_guess(code, player, guess, feedback):
    game = join_game(code)
    if not game:
        return
    guesses_field = f"guesses_{player}"
    feedback_field = f"feedback_{player}"
    game[guesses_field] = game.get(guesses_field, []) + [guess]
    # Store feedback as comma-separated string to avoid nested list issues
    feedback_str = ",".join(feedback)
    existing = game.get(feedback_field, [])
    if isinstance(existing, list):
        game[feedback_field] = existing + [feedback_str]
    else:
        game[feedback_field] = [feedback_str]
    game["turn"] = "p2" if player == "p1" else "p1"
    url = f"{BASE_URL}/games/{code}"
    data = {"fields": {k: _to_firestore(v) for k, v in game.items()}}
    _request("PATCH", url, data)

def set_winner(code, winner):
    game = join_game(code)
    if not game:
        return
    game["status"] = "finished"
    game["winner"] = winner
    url = f"{BASE_URL}/games/{code}"
    data = {"fields": {k: _to_firestore(v) for k, v in game.items()}}
    _request("PATCH", url, data)

def listen_to_game(code, callback):
    """Poll Firebase every 2 seconds for updates."""
    stop_event = threading.Event()

    def poll():
        last_data = None
        while not stop_event.is_set():
            game = join_game(code)
            if game and game != last_data:
                last_data = game
                callback(game)
            stop_event.wait(2)

    thread = threading.Thread(target=poll, daemon=True)
    thread.start()

    class Listener:
        def unsubscribe(self):
            stop_event.set()

    return Listener()

def delete_game(code):
    url = f"{BASE_URL}/games/{code}"
    _request("DELETE", url)