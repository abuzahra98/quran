"""يدمج القالب + الخط + بيانات المصحف في ملف واحد index.html يعمل بدون إنترنت.
التشغيل من جذر المشروع:  python src/build.py
"""
import base64, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
tpl = (root / "src" / "app.template.html").read_text(encoding="utf-8")
font = base64.b64encode((root / "fonts" / "UthmanicHafs-v-3.0.ttf").read_bytes()).decode()
data = (root / "data" / "qdata.json").read_text(encoding="utf-8").replace("</", "<\\/")
page = tpl.replace("__FONT__", font).replace("__DATA__", data)
html = ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '</head><body>' + page + '</body></html>')
(root / "index.html").write_text(html, encoding="utf-8")
print("built index.html:", round(len(html.encode()) / 1e6, 2), "MB")
