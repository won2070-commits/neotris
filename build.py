#!/usr/bin/env python3
"""NEOTRIS 배포 빌드: 단일 HTML(아이콘·manifest 내장) + 웹 호스팅용 zip."""
import base64, json, pathlib, zipfile

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / 'index.html'
OUT_HTML = ROOT / 'NEOTRIS.html'
OUT_ZIP = ROOT / 'NEOTRIS_배포.zip'

html = SRC.read_text(encoding='utf-8')
b64 = lambda n: 'data:image/png;base64,' + base64.b64encode((ROOT / n).read_bytes()).decode()
i192, i512, i180 = b64('icon-192.png'), b64('icon-512.png'), b64('icon-180.png')

manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
for ic in manifest['icons']:
    ic['src'] = i512 if ic['sizes'].startswith('512') else i192

# 아이콘 인라인 + manifest를 blob URL로 런타임 주입 (file:// 에서도 동작)
repl = [
    ('<link rel="manifest" href="manifest.json">',
     '<script>document.head.appendChild(Object.assign(document.createElement("link"),{rel:"manifest",'
     'href:URL.createObjectURL(new Blob([' + json.dumps(json.dumps(manifest, ensure_ascii=False)) +
     '],{type:"application/manifest+json"}))}));</script>'),
    ('<link rel="icon" type="image/png" href="icon-192.png">', f'<link rel="icon" type="image/png" href="{i192}">'),
    ('<link rel="apple-touch-icon" href="icon-180.png">', f'<link rel="apple-touch-icon" href="{i180}">'),
    ('<img src="icon-192.png"', f'<img src="{i192}"'),
]
for old, new in repl:
    assert old in html, f'소스에서 못 찾음: {old[:50]}'
    html = html.replace(old, new)

OUT_HTML.write_text(html, encoding='utf-8')

with zipfile.ZipFile(OUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(SRC, 'index.html')                      # 호스팅 루트 진입점
    for n in ('manifest.json', 'sw.js', 'icon-192.png', 'icon-512.png', 'icon-180.png'):
        z.write(ROOT / n, n)
    z.writestr('README.txt',   # 윈도우 압축 해제 시 한글 파일명 깨짐 방지
               'NEOTRIS 배포 패키지\n\n'
               '[웹 호스팅] 이 폴더의 모든 파일을 사이트 루트에 업로드하세요. index.html이 진입점입니다.\n'
               '            (넷리파이는 이 zip을 app.netlify.com/drop 에 그대로 끌어다 놓으면 즉시 배포됩니다.)\n'
               '[PC/맥 단독] NEOTRIS.html 파일 하나만 더블클릭하면 실행됩니다.\n'
               '[휴대폰]     배포된 주소를 열고 "홈 화면에 추가"하면 앱처럼 전체화면으로 실행됩니다.\n')

print(f'단일 HTML: {OUT_HTML.name} ({OUT_HTML.stat().st_size/1024:.0f} KB)')
print(f'배포 zip : {OUT_ZIP.name} ({OUT_ZIP.stat().st_size/1024:.0f} KB)')
