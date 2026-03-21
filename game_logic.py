import random
import os

WORD_LENGTH = 5
MAX_ATTEMPTS = 6
LANGUAGES = ["en", "he"]

CORRECT = "green"
MISPLACED = "yellow"
WRONG = "gray"

def load_words(language="en"):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if language == "en":
        # Use the large dictionary file for English
        filepath = os.path.join(base_dir, "words_alpha.txt")
    elif language == "he":
        filepath = os.path.join(base_dir, "words_he_full.txt")
    else:
        filename = f"words_{language}.txt"
        filepath = os.path.join(base_dir, "word_lists", filename)

    with open(filepath, "r", encoding="utf-8") as f:
        words = [line.strip().lower() for line in f if line.strip()]

    words = [w for w in words if len(w) == WORD_LENGTH and w.isalpha()]
    words = [w for w in words if len(set(w)) == len(w)]
    return words

def get_random_word(language="en"):
    words = load_words(language)
    unique_words = [w for w in words if len(set(w)) == len(w)]
    return random.choice(unique_words if unique_words else words)

def is_valid_word_offline(word, language="en"):
    words = load_words(language)
    return word.lower() in words

def is_valid_word_online(word):
    """Check word against free dictionary API."""
    try:
        import urllib.request
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.status == 200
    except Exception:
        return None  # None means offline or error

def check_guess(secret, guess):
    secret = list(secret.lower())
    guess = list(guess.lower())
    length = len(secret)
    feedback = [WRONG] * length
    used = [False] * length

    for i in range(length):
        if i < len(guess) and guess[i] == secret[i]:
            feedback[i] = CORRECT
            used[i] = True

    for i in range(length):
        if feedback[i] == CORRECT:
            continue
        if i >= len(guess):
            continue
        for j in range(length):
            if not used[j] and guess[i] == secret[j]:
                feedback[i] = MISPLACED
                used[j] = True
                break

    return feedback

class WordDuelGame:
    def __init__(self, secret_word, language="en"):
        self.secret = secret_word.lower()
        self.language = language
        self.attempts = []
        self.won = False
        self.over = False

    def guess(self, word):
        word = word.lower()
        if self.over:
            return {"error": "Game is already over."}
        if len(word) != WORD_LENGTH:
            return {"error": f"Word must be {WORD_LENGTH} letters."}
        if not is_valid_word_offline(word, self.language):
            return {"error": "Not a valid word!"}
        feedback = check_guess(self.secret, word)
        self.attempts.append((word, feedback))
        if all(f == CORRECT for f in feedback):
            self.won = True
            self.over = True
        elif len(self.attempts) >= MAX_ATTEMPTS:
            self.over = True
        return {
            "guess": word,
            "feedback": feedback,
            "won": self.won,
            "over": self.over,
            "attempts_left": MAX_ATTEMPTS - len(self.attempts)
        }

    def status(self):
        return {
            "attempts": self.attempts,
            "won": self.won,
            "over": self.over,
            "attempts_left": MAX_ATTEMPTS - len(self.attempts)
        }

if __name__ == "__main__":
    lang = input("Choose language (en/he): ").strip().lower()
    word = input("Enter the secret word: ").strip()
    game = WordDuelGame(word, language=lang)
    print(f"\nGame started! {MAX_ATTEMPTS} attempts allowed.\n")
    while not game.over:
        guess_input = input("Enter your guess: ").strip()
        result = game.guess(guess_input)
        if "error" in result:
            print(f"Error: {result['error']}")
            continue
        display = ""
        for letter, color in zip(result["guess"], result["feedback"]):
            if color == CORRECT:
                display += f"[{letter.upper()}]"
            elif color == MISPLACED:
                display += f"({letter.upper()})"
            else:
                display += f" {letter.upper()} "
        print(display)
        if result["won"]:
            print(f"\nYou won in {len(game.attempts)} attempts!")
        elif result["over"]:
            print(f"\nGame over! The word was: {game.secret}")
        else:
            print(f"Attempts left: {result['attempts_left']}\n")
