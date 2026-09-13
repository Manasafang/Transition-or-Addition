"""Render notebook tables with bundled Garuda fonts using local Chrome/Edge."""
import base64
import subprocess
import sys
from pathlib import Path


def export_table(html, name, width=1050):
    root = Path(__file__).resolve().parent
    faces = []
    for filename, weight in [('Garuda.otf', 400), ('Garuda-Bold.otf', 700)]:
        encoded = base64.b64encode((root / 'fonts' / filename).read_bytes()).decode()
        faces.append("@font-face {font-family: Garuda; src: url(data:font/otf;base64," +
                     encoded + ") format('opentype'); font-weight: " + str(weight) + ";}")
    css = ''.join(faces) + 'table, table * {font-family: Garuda !important;} body {margin:16px;background:white;} #export {display:inline-block;padding:12px;background:white;}'
    page = '<!doctype html><html><head><meta charset="utf-8"><style>' + css + '</style></head><body><div id="export">' + html + '</div></body></html>'
    html_path = root / (name + '_export.html')
    png_path = root / (name + '.png')
    html_path.write_text(page, encoding='utf-8')
    subprocess.run([sys.executable, str(Path(__file__).resolve()), str(html_path),
                    str(png_path), str(width)], check=True,
                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    return png_path


def render(html_path, png_path, width):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    browsers = [Path('C:/Program Files/Google/Chrome/Application/chrome.exe'),
                Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')]
    executable = next((str(p) for p in browsers if p.is_file()), None)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=executable)
        try:
            page = browser.new_page(viewport={'width': int(width), 'height': 900},
                                    device_scale_factor=300 / 96)
            page.goto(Path(html_path).resolve().as_uri())
            page.evaluate('document.fonts.ready')
            assert page.evaluate('document.fonts.check("16px Garuda")')
            page.locator('#export').screenshot(path=png_path)
        finally:
            browser.close()
    with Image.open(png_path) as im:
        im.save(png_path, dpi=(300, 300))


if __name__ == '__main__':
    render(*sys.argv[1:])
