import sys
sys.stdout.reconfigure(encoding='utf-8')

# Read main.py and find Hebrew translations
content = open('main.py', encoding='utf-8').read()
start = content.find('"he": {')
print(content[start:start+500])