with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix the broken pass_instruction line
import re
content = re.sub(
    r'"pass_instruction":\s*"[^"]*\n[^"]*"',
    '"pass_instruction": "!ךסמה תא ול הארת לא - 2 ןקחשל ןופלטה תא ןת."',
    content
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed!")
