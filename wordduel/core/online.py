"""Online duels over the Firestore REST API (protocol v2).

What changed from v1, and why:

* TLS is verified (v1 turned verification off). Android's Python has no
  system CA store, so we use certifi's bundle when available.
* Secret words never leave the device during play. Each player publishes a
  commitment sha256(salt:word). When you guess, *your opponent's* app scores
  the guess against its own word and writes the feedback back. At the end
  both apps reveal salt+word, and each side checks the reveal against the
  commitment and every piece of feedback it received.
* Writes touch only the fields they change (updateMask) and carry an
  updateTime precondition, so two phones writing at once can't silently
  overwrite each other; a conflicting write is re-read and retried.
* 6-digit codes, created with an exists=false precondition so a new game can
  never clobber someone else's.

Game document  games/{code}:
  v, code, language, length, status (waiting|playing|finished)
  joined_p2, commit_p1, commit_p2, turn (p1|p2)
  guesses_p1 / feedback_p1   p1's guesses at p2's word, and p2's scoring
  guesses_p2 / feedback_p2   vice versa
  winner (p1|p2|draw|""), ended_by (solved|draw|forfeit|"")
  reveal_p1, reveal_p2       "salt:word", written once the game is finished
  created_at, expires_at     timestamps (expires_at is meant for a TTL policy)

A guess is "pending" while len(guesses_X) > len(feedback_X).
"""
import datetime
import hashlib
import json
import random
import secrets
import ssl
import threading
import urllib.error
import urllib.parse
import urllib.request

from .rules import MAX_ATTEMPTS, encode_feedback, decode_feedback, is_win, score_guess

PROJECT_ID = "thewordgame-2c3ec"
BASE_URL = (f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}"
            "/databases/(default)/documents/games")
PROTOCOL = 2
CODE_DIGITS = 6
POLL_SECONDS = 1.5


class NetworkError(Exception):
    pass


class Conflict(Exception):
    """Precondition failed: the document changed (or exists) under us."""


class GameError(Exception):
    """A user-facing problem; .key is an i18n key."""

    def __init__(self, key):
        super().__init__(key)
        self.key = key


def other(role):
    return "p2" if role == "p1" else "p1"


def make_commitment(word):
    salt = secrets.token_hex(8)
    return salt, commitment_for(salt, word)


def commitment_for(salt, word):
    return hashlib.sha256(f"{salt}:{word}".encode("utf-8")).hexdigest()


# --------------------------------------------------------------- transport ---

def _ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


class FirestoreTransport:
    """Thin JSON-over-HTTPS layer. Swappable for tests."""

    def __init__(self, base_url=BASE_URL, timeout=10):
        self.base_url = base_url
        self.timeout = timeout
        self.ctx = _ssl_context()

    def request(self, method, code, body=None, params=None):
        url = f"{self.base_url}/{code}"
        if params:
            url += "?" + urllib.parse.urlencode(params, doseq=True)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self.ctx) as resp:
                return json.loads(resp.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            detail = e.read().decode(errors="replace")
            if e.code in (409, 412) or "FAILED_PRECONDITION" in detail or "ALREADY_EXISTS" in detail:
                raise Conflict(detail) from e
            raise NetworkError(f"HTTP {e.code}: {detail[:200]}") from e
        except (urllib.error.URLError, OSError, ValueError) as e:
            raise NetworkError(str(e)) from e


# ------------------------------------------------------- value conversion ---

def to_value(v):
    if isinstance(v, bool):
        return {"booleanValue": v}
    if isinstance(v, int):
        return {"integerValue": str(v)}
    if isinstance(v, str):
        return {"stringValue": v}
    if isinstance(v, datetime.datetime):
        return {"timestampValue": v.strftime("%Y-%m-%dT%H:%M:%SZ")}
    if isinstance(v, (list, tuple)):
        return {"arrayValue": {"values": [to_value(x) for x in v]}}
    if v is None:
        return {"nullValue": None}
    raise TypeError(f"can't store {type(v)}")


def from_value(v):
    if "stringValue" in v:
        return v["stringValue"]
    if "booleanValue" in v:
        return v["booleanValue"]
    if "integerValue" in v:
        return int(v["integerValue"])
    if "timestampValue" in v:
        return v["timestampValue"]
    if "arrayValue" in v:
        return [from_value(x) for x in v["arrayValue"].get("values", [])]
    if "mapValue" in v:
        return {k: from_value(x) for k, x in v["mapValue"].get("fields", {}).items()}
    return None


class Snapshot:
    def __init__(self, raw):
        self.fields = {k: from_value(v) for k, v in raw.get("fields", {}).items()}
        self.update_time = raw.get("updateTime")

    def __getitem__(self, key):
        return self.fields.get(key)

    def get(self, key, default=None):
        value = self.fields.get(key)
        return default if value is None else value


# ------------------------------------------------------------------ client ---

class OnlineClient:
    def __init__(self, transport=None, rng=None):
        self.t = transport or FirestoreTransport()
        self.rng = rng or random.SystemRandom()

    # -- raw document ops
    def fetch(self, code):
        raw = self.t.request("GET", code)
        return Snapshot(raw) if raw else None

    def _write(self, code, changes, snapshot=None, must_not_exist=False):
        params = [("updateMask.fieldPaths", k) for k in changes]
        if must_not_exist:
            params.append(("currentDocument.exists", "false"))
        elif snapshot is not None:
            params.append(("currentDocument.updateTime", snapshot.update_time))
        body = {"fields": {k: to_value(v) for k, v in changes.items()}}
        return Snapshot(self.t.request("PATCH", code, body, params))

    def _update(self, code, mutate, retries=4):
        """Read-modify-write with optimistic concurrency.

        `mutate(snapshot)` returns a dict of changed fields, or None to skip.
        """
        for _ in range(retries):
            snap = self.fetch(code)
            if snap is None:
                raise GameError("game_not_found")
            changes = mutate(snap)
            if not changes:
                return snap
            try:
                return self._write(code, changes, snapshot=snap)
            except Conflict:
                continue
        raise NetworkError("too many conflicting updates")

    # -- game lifecycle
    def create_game(self, language, length):
        now = datetime.datetime.now(datetime.timezone.utc)
        for _ in range(8):
            code = "".join(self.rng.choice("0123456789") for _ in range(CODE_DIGITS))
            fields = {
                "v": PROTOCOL, "code": code, "language": language, "length": length,
                "status": "waiting", "joined_p2": False,
                "commit_p1": "", "commit_p2": "", "turn": "p1",
                "guesses_p1": [], "feedback_p1": [], "guesses_p2": [], "feedback_p2": [],
                "winner": "", "ended_by": "", "reveal_p1": "", "reveal_p2": "",
                "created_at": now, "expires_at": now + datetime.timedelta(days=1),
            }
            try:
                self._write(code, fields, must_not_exist=True)
                return code
            except Conflict:
                continue
        raise NetworkError("could not find a free game code")

    def join_game(self, code):
        def mutate(snap):
            if snap.get("v") != PROTOCOL:
                raise GameError("game_old")
            if snap.get("status") == "finished":
                raise GameError("game_finished")
            if snap.get("joined_p2"):
                raise GameError("game_taken")
            return {"joined_p2": True}
        return self._update(code, mutate)

    def commit_word(self, code, role, commit):
        def mutate(snap):
            changes = {f"commit_{role}": commit}
            if snap.get(f"commit_{other(role)}"):
                changes["status"] = "playing"
            return changes
        return self._update(code, mutate)

    def submit_guess(self, code, role, guess):
        def mutate(snap):
            guesses = snap.get(f"guesses_{role}", [])
            pending = len(guesses) > len(snap.get(f"feedback_{role}", []))
            if snap.get("status") != "playing" or snap.get("turn") != role or pending:
                return None
            return {f"guesses_{role}": guesses + [guess]}
        return self._update(code, mutate)

    def score_pending(self, code, role, my_word):
        """If the opponent has a pending guess at my word, score it.

        Scoring also hands the turn to me (the scorer guesses next), or ends
        the game on a win / when both players are out of guesses.
        """
        opp = other(role)

        def mutate(snap):
            guesses = snap.get(f"guesses_{opp}", [])
            feedback = snap.get(f"feedback_{opp}", [])
            if snap.get("status") != "playing" or len(guesses) <= len(feedback):
                return None
            guess = guesses[len(feedback)]
            fb = score_guess(my_word, guess) if len(guess) == len(my_word) else None
            code_str = encode_feedback(fb) if fb else "X" * len(my_word)
            changes = {f"feedback_{opp}": feedback + [code_str], "turn": role}
            mine_done = len(snap.get(f"guesses_{role}", [])) >= MAX_ATTEMPTS
            theirs_done = len(guesses) >= MAX_ATTEMPTS
            if fb and is_win(fb):
                changes.update(status="finished", winner=opp, ended_by="solved")
            elif mine_done and theirs_done:
                changes.update(status="finished", winner="draw", ended_by="draw")
            elif mine_done:
                changes["turn"] = opp
            return changes
        return self._update(code, mutate)

    def reveal(self, code, role, salt, word):
        def mutate(snap):
            if snap.get("status") != "finished" or snap.get(f"reveal_{role}"):
                return None
            return {f"reveal_{role}": f"{salt}:{word}"}
        return self._update(code, mutate)

    def forfeit(self, code, role):
        def mutate(snap):
            if snap.get("status") == "finished":
                return None
            return {"status": "finished", "winner": other(role), "ended_by": "forfeit"}
        return self._update(code, mutate)

    def listen(self, code, callback, on_error=None, interval=POLL_SECONDS):
        """Poll for changes on a background thread. Returns a stop() function."""
        stop = threading.Event()

        def run():
            last = None
            while not stop.is_set():
                try:
                    snap = self.fetch(code)
                    if snap is not None and snap.update_time != last:
                        last = snap.update_time
                        callback(snap)
                except NetworkError as e:
                    if on_error:
                        on_error(e)
                except Exception as e:  # never let the poller die silently
                    if on_error:
                        on_error(e)
                stop.wait(interval)

        threading.Thread(target=run, daemon=True).start()
        return stop.set


def verify_opponent(snapshot, role):
    """After the game: check the opponent's reveal against their commitment
    and every piece of feedback they gave us.

    Returns (word or None, honest: bool or None). None means not revealed yet.
    """
    opp = other(role)
    reveal = snapshot.get(f"reveal_{opp}", "")
    if not reveal or ":" not in reveal:
        return None, None
    salt, word = reveal.split(":", 1)
    if commitment_for(salt, word) != snapshot.get(f"commit_{opp}"):
        return word, False
    for guess, fb in zip(snapshot.get(f"guesses_{role}", []), snapshot.get(f"feedback_{role}", [])):
        if len(guess) != len(word) or decode_feedback(fb) != score_guess(word, guess):
            return word, False
    return word, True
