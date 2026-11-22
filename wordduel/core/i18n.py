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
        "challenge": "Challenge a Friend",
        "challenge_sub": "Send a word, they solve it anytime",
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

        "challenge_title": "Challenges",
        "challenge_intro": "Pick a secret word and send the code to a friend. They solve it whenever they like, no internet needed.",
        "challenge_create": "Create a challenge",
        "challenge_solve": "Solve a challenge",
        "challenge_play": "Friend's challenge",
        "challenge_code_title": "Your challenge code",
        "challenge_code_note": "Send this code to a friend. Anyone with the code can play your word.",
        "share_code": "Send to a friend",
        "copy_code": "Copy code",
        "done": "Done",
        "enter_code": "Enter your friend's 10-digit code",
        "paste": "Paste",
        "play": "Play!",
        "code_invalid": "That code doesn't work. Check the digits!",
        "no_code_in_clipboard": "No challenge code found to paste",
        "challenge_message": "Can you guess my secret word? Open Word Duel, tap Challenge a Friend, then Solve a challenge, and enter this code: {code}",
        "challenge_result_intro": "I played your Word Duel challenge {code}!",
        "send_one_back": "Send one back",

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
            "Guess the secret word in 6 tries (Free Play: as many as you need).\n\n"
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
            "Challenge a Friend: pick a word and send the code. Your friend "
            "solves it whenever they like and can send one back."
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
        "challenge": "אתגר חבר",
        "challenge_sub": "שלחו מילה, והחבר יפתור מתי שירצה",
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

        "challenge_title": "אתגרים",
        "challenge_intro": "בחרו מילה סודית ושלחו את הקוד לחבר. הוא יפתור מתי שנוח לו, בלי אינטרנט.",
        "challenge_create": "צור אתגר",
        "challenge_solve": "פתור אתגר",
        "challenge_play": "אתגר מחבר",
        "challenge_code_title": "קוד האתגר שלך",
        "challenge_code_note": "שלחו את הקוד לחבר. כל מי שיש לו את הקוד יכול לשחק במילה שלכם.",
        "share_code": "שלח לחבר",
        "copy_code": "העתק קוד",
        "done": "סיום",
        "enter_code": "הקלידו את הקוד בן 10 הספרות",
        "paste": "הדבק",
        "play": "שחק!",
        "code_invalid": "הקוד לא תקין. בדקו את הספרות!",
        "no_code_in_clipboard": "לא נמצא קוד אתגר להדבקה",
        "challenge_message": "תצליחו לנחש את המילה הסודית שלי? פתחו את דו־קרב מילים, לחצו על אתגר חבר ואז פתור אתגר, והקלידו את הקוד: {code}",
        "challenge_result_intro": "שיחקתי באתגר שלך בדו־קרב מילים {code}!",
        "send_one_back": "שלח אתגר בחזרה",

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
            "נחשו את המילה הסודית ב־6 ניסיונות (במשחק חופשי: כמה שצריך).\n\n"
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
            "אתגר חבר: בחרו מילה ושלחו את הקוד. החבר פותר מתי שנוח לו "
            "ויכול לשלוח אתגר בחזרה."
        ),
        "got_it": "הבנתי!",
        "share_title": "דו־קרב מילים",
    },
}


def tr(language, key, **params):
    table = STRINGS.get(language, STRINGS["en"])
    text = table.get(key) or STRINGS["en"].get(key) or key
    return text.format(**params) if params else text
