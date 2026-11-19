"""All UI strings, in normal reading order for both languages.

Use {name} placeholders for values. Hebrew is converted to visual order at
draw time by core.bidi, so never pre-reverse anything here.
"""

STRINGS = {
    "en": {
        "app_title": "Word Duel",
        "tagline": "Guess the word. Beat your friends.",
        "daily": "Daily Word",
        "daily_sub": "Puzzle #{n}",
        "daily_done": "Done! Next in {time}",
        "solo": "Free Play",
        "solo_sub": "{n} letters, endless words",
        "pass_play": "Pass & Play",
        "pass_play_sub": "Two players, one phone",
        "online": "Online Duel",
        "online_sub": "Race a friend anywhere",
        "stats": "Stats",
        "settings": "Settings",
        "rules": "How to play",
        "back": "Back",
        "menu": "Menu",

        "not_enough": "Not enough letters",
        "not_valid": "Not in word list",
        "repeat_letters": "Secret words can't repeat letters",
        "hard_position": "Letter {n} must be {letter}",
        "hard_contains": "Guess must contain {letter}",
        "already_guessed": "Already tried that one",
        "hint": "Hint",
        "hint_left": "Hint ({n})",
        "hint_given": "Letter {n} is {letter}",
        "no_hints": "No hints left",
        "hint_none_needed": "You already know every letter!",
        "hard_badge": "HARD",

        "win_1": "Genius!", "win_2": "Magnificent!", "win_3": "Impressive!",
        "win_4": "Splendid!", "win_5": "Great!", "win_6": "Phew!",
        "lose": "So close!",
        "the_word_was": "The word was {word}",
        "play_again": "Play again",
        "share": "Share",
        "copied": "Copied to clipboard!",
        "next_daily": "Next word in",

        "player_1": "Player 1",
        "player_2": "Player 2",
        "type_secret": "Pick a secret word",
        "secret_hint": "{n} letters, no repeats. Keep it hidden!",
        "lock_in": "Lock it in",
        "pass_phone": "Pass the phone!",
        "pass_instruction": "Hand the phone to {name}.\nNo peeking!",
        "im_ready": "I'm {name}, let's go!",
        "guesser": "{name} guesses",
        "rematch": "Swap & rematch",
        "score": "Score",

        "online_title": "Online Duel",
        "online_intro": "Take turns guessing each other's word. First to crack it wins!",
        "create_game": "Create a game",
        "join_game": "Join a game",
        "connecting": "Connecting...",
        "your_code": "Your game code",
        "share_code": "Send this code to your friend",
        "enter_code": "Enter your friend's 6-digit code",
        "join": "Join!",
        "game_not_found": "Game not found. Check the code!",
        "game_taken": "That game already has two players",
        "game_finished": "That game has already finished",
        "game_old": "That game was made with an older version",
        "net_error": "Can't reach the server. Check your connection.",
        "net_retry": "Connection trouble, retrying...",
        "friend_joined": "Your friend joined!",
        "waiting_friend": "Waiting for your friend to join...",
        "waiting_word": "Waiting for your friend's secret word...",
        "your_turn": "Your turn!",
        "their_turn": "Friend is guessing...",
        "scoring": "Checking with your friend...",
        "you_won": "You cracked it!",
        "you_lost": "Your friend got there first",
        "draw": "Nobody got it. It's a draw!",
        "forfeit_win": "Your friend left. You win!",
        "their_word": "Their word was {word}",
        "cheat_warning": "Heads up: your friend's answers didn't match their word.",
        "no_reveal": "Waiting for your friend to reveal their word...",
        "leave_game": "Leave game",
        "your_board": "You",
        "their_board": "Friend",

        "played": "Played",
        "win_pct": "Win %",
        "streak": "Streak",
        "best": "Best",
        "distribution": "Guess distribution",
        "no_games": "No games yet. Go play!",

        "language": "Language",
        "word_length": "Word length",
        "word_length_note": "For Free Play and Pass & Play",
        "hard_mode": "Hard mode",
        "hard_mode_note": "Revealed hints must be used in later guesses",
        "colorblind": "High-contrast colors",
        "colorblind_note": "Orange and blue instead of green and yellow",
        "sound": "Sound effects",
        "vibration": "Vibration",

        "rules_text": (
            "Guess the secret word in 6 tries.\n\n"
            "Each guess must be a real word. After each guess the tiles change "
            "color to show how close you were:"
        ),
        "rule_correct": "In the word, in the right spot",
        "rule_present": "In the word, wrong spot",
        "rule_absent": "Not in the word",
        "rules_more": (
            "Secret words never repeat a letter, but your guesses may.\n\n"
            "Stuck? Tap the bulb for a hint: it reveals one letter.\n\n"
            "Daily Word: everyone gets the same word each day. Keep your streak "
            "going!\n\n"
            "Pass & Play: Player 1 picks a word, Player 2 guesses. Then swap.\n\n"
            "Online Duel: you and a friend each pick a word and take turns "
            "guessing. First to crack it wins."
        ),
        "got_it": "Got it!",
        "share_title": "Word Duel",
    },
    "he": {
        "app_title": "דו־קרב מילים",
        "tagline": "נחשו את המילה. נצחו את החברים.",
        "daily": "המילה היומית",
        "daily_sub": "חידה #{n}",
        "daily_done": "סיימת! הבאה בעוד {time}",
        "solo": "משחק חופשי",
        "solo_sub": "{n} אותיות, מילים בלי סוף",
        "pass_play": "העבר ושחק",
        "pass_play_sub": "שני שחקנים, טלפון אחד",
        "online": "דו־קרב אונליין",
        "online_sub": "התחרו בחבר מכל מקום",
        "stats": "סטטיסטיקה",
        "settings": "הגדרות",
        "rules": "איך משחקים",
        "back": "חזור",
        "menu": "תפריט",

        "not_enough": "אין מספיק אותיות",
        "not_valid": "המילה לא ברשימה",
        "repeat_letters": "במילה סודית אסור לחזור על אותיות",
        "hard_position": "אות {n} חייבת להיות {letter}",
        "hard_contains": "הניחוש חייב לכלול {letter}",
        "already_guessed": "כבר ניסית את המילה הזו",
        "hint": "רמז",
        "hint_left": "רמז ({n})",
        "hint_given": "אות {n} היא {letter}",
        "no_hints": "נגמרו הרמזים",
        "hint_none_needed": "את כל האותיות כבר גילית!",
        "hard_badge": "קשה",

        "win_1": "גאוני!", "win_2": "מדהים!", "win_3": "מרשים!",
        "win_4": "נהדר!", "win_5": "יפה מאוד!", "win_6": "בנס!",
        "lose": "כמעט!",
        "the_word_was": "המילה הייתה {word}",
        "play_again": "שחק שוב",
        "share": "שתף",
        "copied": "הועתק!",
        "next_daily": "המילה הבאה בעוד",

        "player_1": "שחקן 1",
        "player_2": "שחקן 2",
        "type_secret": "בחרו מילה סודית",
        "secret_hint": "{n} אותיות, בלי חזרות. אל תגלו!",
        "lock_in": "נעל מילה",
        "pass_phone": "העבירו את הטלפון!",
        "pass_instruction": "תנו את הטלפון ל{name}.\nבלי להציץ!",
        "im_ready": "אני {name}, יאללה!",
        "guesser": "{name} מנחש",
        "rematch": "החלפה ומשחק חוזר",
        "score": "ניקוד",

        "online_title": "דו־קרב אונליין",
        "online_intro": "מנחשים בתורות את המילה של היריב. מי שמפצח ראשון מנצח!",
        "create_game": "צור משחק",
        "join_game": "הצטרף למשחק",
        "connecting": "מתחבר...",
        "your_code": "קוד המשחק שלך",
        "share_code": "שלחו את הקוד לחבר",
        "enter_code": "הקלידו את הקוד בן 6 הספרות",
        "join": "הצטרף!",
        "game_not_found": "המשחק לא נמצא. בדקו את הקוד!",
        "game_taken": "במשחק הזה כבר יש שני שחקנים",
        "game_finished": "המשחק כבר הסתיים",
        "game_old": "המשחק נוצר בגרסה ישנה",
        "net_error": "אין חיבור לשרת. בדקו את האינטרנט.",
        "net_retry": "בעיית חיבור, מנסה שוב...",
        "friend_joined": "החבר הצטרף!",
        "waiting_friend": "ממתין שהחבר יצטרף...",
        "waiting_word": "ממתין למילה הסודית של החבר...",
        "your_turn": "התור שלך!",
        "their_turn": "החבר מנחש...",
        "scoring": "בודק מול החבר...",
        "you_won": "פיצחת!",
        "you_lost": "החבר הקדים אותך",
        "draw": "אף אחד לא הצליח. תיקו!",
        "forfeit_win": "החבר עזב. ניצחת!",
        "their_word": "המילה שלו הייתה {word}",
        "cheat_warning": "שימו לב: התשובות של החבר לא התאימו למילה שלו.",
        "no_reveal": "ממתין שהחבר יחשוף את המילה...",
        "leave_game": "עזוב משחק",
        "your_board": "אתה",
        "their_board": "חבר",

        "played": "משחקים",
        "win_pct": "% ניצחון",
        "streak": "רצף",
        "best": "שיא",
        "distribution": "התפלגות ניחושים",
        "no_games": "עוד לא שיחקת. קדימה!",

        "language": "שפה",
        "word_length": "אורך מילה",
        "word_length_note": "למשחק חופשי ולהעבר ושחק",
        "hard_mode": "מצב קשה",
        "hard_mode_note": "חובה להשתמש ברמזים שנחשפו",
        "colorblind": "צבעים בניגודיות גבוהה",
        "colorblind_note": "כתום וכחול במקום ירוק וצהוב",
        "sound": "צלילים",
        "vibration": "רטט",

        "rules_text": (
            "נחשו את המילה הסודית ב־6 ניסיונות.\n\n"
            "כל ניחוש חייב להיות מילה אמיתית. אחרי כל ניחוש המשבצות "
            "משנות צבע ומראות כמה התקרבתם:"
        ),
        "rule_correct": "האות במילה ובמקום הנכון",
        "rule_present": "האות במילה אבל לא במקום",
        "rule_absent": "האות לא במילה",
        "rules_more": (
            "במילים הסודיות אין אותיות חוזרות, אבל בניחושים מותר.\n\n"
            "תקועים? לחצו על הנורה לרמז שחושף אות אחת.\n\n"
            "המילה היומית: כולם מקבלים את אותה מילה בכל יום. שמרו על הרצף!\n\n"
            "העבר ושחק: שחקן 1 בוחר מילה ושחקן 2 מנחש. ואז מתחלפים.\n\n"
            "דו־קרב אונליין: כל אחד בוחר מילה ומנחשים בתורות. "
            "מי שמפצח ראשון מנצח."
        ),
        "got_it": "הבנתי!",
        "share_title": "דו־קרב מילים",
    },
}


def tr(language, key, **params):
    table = STRINGS.get(language, STRINGS["en"])
    text = table.get(key) or STRINGS["en"].get(key) or key
    return text.format(**params) if params else text
