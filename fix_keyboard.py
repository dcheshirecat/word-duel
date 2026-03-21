with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_rows = '''HE_ROW1 = ["\u05e7", "\u05e8", "\u05d0", "\u05d8", "\u05d5", "\u05df", "\u05de", "\u05e4"]
HE_ROW2 = ["\u05e9", "\u05d3", "\u05d2", "\u05db", "\u05e2", "\u05d9", "\u05d7", "\u05dc"]
HE_ROW3 = ["\u05d6", "\u05e1", "\u05d1", "\u05d4", "\u05e0", "\u05ea", "\u05e6", "\u05e3", "\u05da", "\u05dd", "\u05e5"]'''

# Find and replace the corrupted rows
import re
content = re.sub(
    r'HE_ROW1 = \[.*?\]\nHE_ROW2 = \[.*?\]\nHE_ROW3 = \[.*?\]',
    old_rows,
    content,
    flags=re.DOTALL
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Hebrew keyboard rows restored!")