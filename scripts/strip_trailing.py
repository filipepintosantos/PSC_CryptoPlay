"""Strip trailing whitespace from all .py files under src/"""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
count = 0
for p in root.rglob('src/*.py'):
    s = p.read_text(encoding='utf-8')
    new = '\n'.join([line.rstrip() for line in s.splitlines()]) + ('\n' if s.endswith('\n') else '')
    if new != s:
        p.write_text(new, encoding='utf-8')
        count += 1
print('trimmed', count, 'files')
