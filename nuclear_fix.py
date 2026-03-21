import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace entire "he" section
old_start = content.find('"he": {')
old_end = content.find('def t(language')

new_he = """    "he": {
        "choose_language": "\\u05d4\\u05e4\\u05e9 \\u05e8\\u05d7\\u05d1",
        "choose_mode": "\\u05e7\\u05d7\\u05e9\\u05de \\u05d1\\u05e6\\u05de \\u05e8\\u05d7\\u05d1",
        "single_player": "\\u05d3\\u05d9\\u05d7\\u05d9 \\u05df\\u05e7\\u05d7\\u05e9",
        "pass_play": "\\u05e7\\u05d7\\u05e9\\u05d5 \\u05e8\\u05d1\\u05e2\\u05d4",
        "play_online": "\\u05df\\u05d9\\u05d9\\u05dc\\u05e0\\u05d5\\u05d0 \\u05e7\\u05d7\\u05e9",
        "back": "\\u05e8\\u05d5\\u05d6\\u05d7",
        "rules": "\\u05dd\\u05d9\\u05dc\\u05dc\\u05db",
        "player1": "1 \\u05df\\u05e7\\u05d7\\u05e9",
        "type_secret": "\\u05ea\\u05d9\\u05d3\\u05d5\\u05e1\\u05d4 \\u05d4\\u05dc\\u05d9\\u05de\\u05d4 \\u05ea\\u05d0 \\u05d3\\u05dc\\u05e7\\u05d4",
        "not_enough": "!\\u05ea\\u05d5\\u05d9\\u05ea\\u05d5\\u05d0 \\u05d9\\u05e7\\u05e4\\u05e1\\u05de \\u05df\\u05d9\\u05d0",
        "not_valid": "!\\u05d4\\u05e0\\u05d9\\u05e7\\u05ea \\u05d4\\u05e0\\u05d9\\u05d0 \\u05d4\\u05dc\\u05d9\\u05de\\u05d4",
        "must_be_5": "!\\u05ea\\u05d5\\u05d9\\u05ea\\u05d5\\u05d0 5 \\u05ea\\u05d1 \\u05ea\\u05d5\\u05d9\\u05d4\\u05dc \\u05ea\\u05d1\\u05d9\\u05d9\\u05d7 \\u05d4\\u05dc\\u05d9\\u05de\\u05d4",
        "you_won": "\\U0001f389 !\\u05ea\\u05d7\\u05e6\\u05d9\\u05e0",
        "game_over": " :\\u05d4\\u05ea\\u05d9\\u05d9\\u05d4 \\u05d4\\u05dc\\u05d9\\u05de\\u05d4 !\\u05e8\\u05de\\u05d2\\u05e0 \\u05e7\\u05d7\\u05e9\\u05de\\u05d4",
        "tap_again": "!\\u05d1\\u05d5\\u05e9 \\u05e7\\u05d7\\u05e9\\u05dc \\u05d9\\u05d3\\u05db \\u05e5\\u05d7\\u05dc",
        "checking": "...\\u05e7\\u05d3\\u05d5\\u05d1",
        "pass_phone": "!\\u05df\\u05d5\\u05e4\\u05dc\\u05d8\\u05d4 \\u05ea\\u05d0 \\u05e8\\u05d1\\u05e2\\u05d4",
        "pass_instruction": "!2 \\u05df\\u05e7\\u05d7\\u05e9\\u05dc \\u05df\\u05d5\\u05e4\\u05dc\\u05d8\\u05d4 \\u05ea\\u05d0 \\u05df\\u05ea - !\\u05da\\u05e1\\u05de\\u05d4 \\u05ea\\u05d0 \\u05d5\\u05dc \\u05d4\\u05d0\\u05e8\\u05ea \\u05dc\\u05d0",
        "p2_ready": "!\\u05df\\u05db\\u05d5\\u05de 2 \\u05df\\u05e7\\u05d7\\u05e9",
        "online_play": "\\u05df\\u05d9\\u05d9\\u05dc\\u05e0\\u05d5\\u05d0 \\u05e7\\u05d7\\u05e9\\u05de",
        "play_with_friend": "!\\u05df\\u05d9\\u05d9\\u05dc\\u05e0\\u05d5\\u05d0 \\u05e8\\u05d1\\u05d7 \\u05dd\\u05e2 \\u05e7\\u05d7\\u05e9",
        "create_game": "\\u05e7\\u05d7\\u05e9\\u05de \\u05e8\\u05d5\\u05e6",
        "join_game": "\\u05e7\\u05d7\\u05e9\\u05de\\u05dc \\u05e3\\u05e8\\u05d8\\u05e6\\u05d4",
        "your_code": "\\u05da\\u05dc\\u05e9 \\u05e7\\u05d7\\u05e9\\u05de\\u05d4 \\u05d3\\u05d5\\u05e7",
        "share_code": "!\\u05da\\u05e8\\u05d1\\u05d7 \\u05dd\\u05e2 \\u05d3\\u05d5\\u05e7\\u05d4 \\u05ea\\u05d0 \\u05e3\\u05ea\\u05e9",
        "enter_code": ":\\u05ea\\u05d5\\u05e8\\u05e4\\u05e1 4 \\u05df\\u05d1 \\u05e7\\u05d7\\u05e9\\u05de \\u05d3\\u05d5\\u05e7 \\u05e1\\u05e0\\u05db\\u05d4",
        "join": "!\\u05e3\\u05e8\\u05d8\\u05e6\\u05d4",
        "game_not_found": "!\\u05d3\\u05d5\\u05e7\\u05d4 \\u05ea\\u05d0 \\u05e7\\u05d3\\u05d5\\u05d1 .\\u05d0\\u05e6\\u05de\\u05e0 \\u05d0\\u05dc \\u05e7\\u05d7\\u05e9\\u05de\\u05d4",
        "game_finished": "!\\u05dd\\u05d9\\u05d9\\u05ea\\u05e1\\u05d4 \\u05e8\\u05d1\\u05db \\u05e7\\u05d7\\u05e9\\u05de\\u05d4",
        "enter_4digits": "!\\u05ea\\u05d5\\u05e8\\u05e4\\u05e1 4 \\u05df\\u05d1 \\u05d3\\u05d5\\u05e7 \\u05e1\\u05e0\\u05db\\u05d4",
        "waiting_word": "...\\u05d1\\u05d9\\u05e8\\u05d9\\u05d4 \\u05dc\\u05e9 \\u05d4\\u05dc\\u05d9\\u05de\\u05dc \\u05df\\u05d9\\u05ea\\u05de\\u05de",
        "waiting_p2": "...2 \\u05df\\u05e7\\u05d7\\u05e9\\u05dc \\u05df\\u05d9\\u05ea\\u05de\\u05de",
        "both_set": "!\\u05dc\\u05d9\\u05d7\\u05ea\\u05de \\u05e3\\u05e1 1 \\u05df\\u05e7\\u05d7\\u05e9 !\\u05d5\\u05e2\\u05d1\\u05e7\\u05e0 \\u05ea\\u05d5\\u05dc\\u05d9\\u05de\\u05d4 \\u05d9\\u05ea\\u05e9",
        "your_turn": "!\\u05da\\u05dc\\u05e9 \\u05e8\\u05d5\\u05ea\\u05d4",
        "opponent_turn": "...\\u05d1\\u05d9\\u05e8\\u05d9\\u05d4 \\u05e8\\u05d5\\u05ea",
        "you_won_online": "\\U0001f389 !\\u05ea\\u05d7\\u05e6\\u05d9\\u05e0",
        "opponent_won": " :\\u05d4\\u05ea\\u05d9\\u05d9\\u05d4 \\u05d4\\u05dc\\u05d9\\u05de\\u05d4 !\\u05d7\\u05e6\\u05d9\\u05e0 \\u05d1\\u05d9\\u05e8\\u05d9\\u05d4",
        "menu": "\\u05d8\\u05d9\\u05e8\\u05e4\\u05ea",
        "word_game": "\\u05dd\\u05d9\\u05dc\\u05d9\\u05de\\u05d4 \\u05e7\\u05d7\\u05e9\\u05de",
        "set_your_word": "!\\u05dd\\u05d3\\u05d5\\u05e7 \\u05da\\u05dc\\u05e9 \\u05ea\\u05d9\\u05d3\\u05d5\\u05e1\\u05d4 \\u05d4\\u05dc\\u05d9\\u05de\\u05d4 \\u05ea\\u05d0 \\u05e8\\u05d3\\u05d2\\u05d4",
        "waiting_opponent_word": "...\\u05d5\\u05dc\\u05e9 \\u05d4\\u05dc\\u05d9\\u05de\\u05d4 \\u05ea\\u05d0 \\u05e8\\u05d9\\u05d3\\u05d2\\u05d9\\u05e9 \\u05d1\\u05d9\\u05e8\\u05d9\\u05dc \\u05df\\u05d9\\u05ea\\u05de\\u05de",
    }
}

"""

new_content = content[:old_start] + new_he + content[old_end:]

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done! Hebrew translations restored as ASCII-safe unicode escapes.")
