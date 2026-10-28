"""Builds app/index.html (the installable phone app) from the website's index.html so both are identical.
Run from the repo root after any change to index.html: python3 tools/build_app.py"""
s = open('index.html').read()
s = s.replace("get('data/", "get('../data/")
s = s.replace('href="icon-192.png"', 'href="../icon-192.png"').replace('href="icon-180.png"', 'href="../icon-180.png"')
s = s.replace('<link rel="icon"', '<link rel="manifest" href="manifest.webmanifest">\n<meta name="theme-color" content="#1846a3">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-title" content="Market Desk">\n<link rel="icon"', 1)
s = s.replace('</body>', "<script>if('serviceWorker' in navigator)navigator.serviceWorker.register('sw.js').catch(()=>{});</script>\n</body>", 1)
assert "get('data/" not in s
open('app/index.html', 'w').write(s)
print('app/index.html rebuilt from index.html')
