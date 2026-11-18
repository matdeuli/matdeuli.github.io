"""Builds privacy/index.html from the app repository's docs/legal/privacy-policy.md.

Usage: python3 scripts/build_privacy.py path/to/privacy-policy.md
Only the small Markdown subset used by the policy is supported:
headings, paragraphs, numbered and bulleted lists, tables, HTML comments (dropped).
"""
import html
import re
import sys

src = open(sys.argv[1], encoding='utf-8').read()
src = re.sub(r'<!--.*?-->', '', src, flags=re.S).strip()


def inline(t: str) -> str:
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\(((?:www\.|privacy\.|ecrm\.)[^)\s]+)\)', r'(<a href="https://\1">\1</a>)', t)
    t = re.sub(r'([\w.+-]+@[\w-]+\.[\w.]+)', r'<a href="mailto:\1">\1</a>', t)
    return t


out, title, lines, i = [], '', src.split('\n'), 0
while i < len(lines):
    line = lines[i].rstrip()
    if not line:
        i += 1
        continue
    if line.startswith('# '):
        title = line[2:].strip()
        i += 1
        continue
    if line.startswith('## '):
        out.append(f'<h2>{inline(line[3:])}</h2>')
        i += 1
        continue
    if line.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?', c) for c in cells):
                rows.append(cells)
            i += 1
        head, body = rows[0], rows[1:]
        out.append('<table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>'
                   + ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body) + '</tbody></table>')
        continue
    m = re.match(r'(\d+)\. (.*)', line)
    if m:
        items = []
        while i < len(lines) and re.match(r'\d+\. ', lines[i]):
            items.append(re.sub(r'^\d+\. ', '', lines[i]))
            i += 1
        out.append('<ol>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ol>')
        continue
    if line.startswith('- '):
        items = []
        while i < len(lines) and lines[i].startswith('- '):
            items.append(lines[i][2:])
            i += 1
        out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ul>')
        continue
    out.append(f'<p>{inline(line)}</p>')
    i += 1

page = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>맛들이 {html.escape(title)}</title>
<style>
  :root {{ --bg: #ffffff; --text: #191f28; --muted: #4e5968; --line: #e5e8eb; --accent: #0f8a5f; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg: #17171c; --text: #e9ebee; --muted: #a6adb7; --line: #2c2f36; --accent: #3fc28d; }} }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--text); font: 16px/1.7 -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif; word-break: keep-all; }}
  main {{ max-width: 760px; margin: 0 auto; padding: 32px 16px 64px; }}
  h1 {{ font-size: 26px; margin: 0 0 24px; }}
  h2 {{ font-size: 18px; margin: 32px 0 8px; }}
  p, li {{ color: var(--text); }}
  ol, ul {{ padding-left: 22px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 15px; }}
  th, td {{ border: 1px solid var(--line); padding: 8px 10px; text-align: left; vertical-align: top; }}
  th {{ color: var(--muted); font-weight: 600; }}
  a {{ color: var(--accent); }}
  .app {{ color: var(--muted); font-size: 14px; margin: 0 0 4px; }}
</style>
</head>
<body>
<main>
<p class="app">맛들이</p>
<h1>{html.escape(title)}</h1>
{chr(10).join(out)}
</main>
</body>
</html>
'''
open('privacy/index.html', 'w', encoding='utf-8').write(page)
print('wrote privacy/index.html', len(page), 'bytes')
