"""splice_teams.py — patches the team catalogue in app.py"""
import sys, ast

with open('_team_block.py', 'r', encoding='utf-8') as f:
    new_block = f.read()

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

START_MARKER = '# All 48 FIFA World Cup 2026'
END_MARKER   = 'FD_WC_COMP = "WC"'

start = content.find(START_MARKER)
end   = content.find(END_MARKER)
end   = content.index('\n', end) + 1

if start == -1 or end <= start:
    print('ERROR: markers not found', start, end)
    sys.exit(1)

print(f'Replacing bytes {start}..{end} ({end-start} bytes old)')
new_content = content[:start] + new_block + '\n' + content[end:]

# Syntax check first
try:
    ast.parse(new_content)
    print('Syntax OK')
except SyntaxError as e:
    print(f'SYNTAX ERROR at line {e.lineno}: {e.msg}')
    # Show context
    lines = new_content.split('\n')
    for i in range(max(0, e.lineno-3), min(len(lines), e.lineno+3)):
        print(f'{i+1:4d}: {lines[i]}')
    sys.exit(1)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'Done! {len(content)} -> {len(new_content)} bytes')

# Quick count
import re
teams = re.findall(r'"name":\s*"([^"]+)".*?"group":', new_content)
print(f'Team entries found: {len(teams)}')
for t in teams:
    print(f'  - {t}')
