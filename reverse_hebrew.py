def reverse_hebrew(text):
    return text[::-1]

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find Hebrew section
start = content.find('"he": {')
end = content.find('def t(language')
he_section = content[start:end]

# Reverse each Hebrew string value
import re
def reverse_match(m):
    value = m.group(1)
    # Only reverse if contains Hebrew characters
    if any('\u0590' <= c <= '\u05ff' for c in value):
        return f'": "{value[::-1]}"'
    return m.group(0)

new_he_section = re.sub(r'": "([^"]+)"', reverse_match, he_section)

new_content = content[:start] + new_he_section + content[end:]

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Hebrew strings reversed!")