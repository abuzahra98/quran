import json, re, unicodedata, sys, base64

src = sys.argv[1]
out = sys.argv[2]
d = json.load(open(src, encoding="utf-8"))
words = d["words"]
rasm = d["rasm_imlai"]
N = len(words)

# marks per word position
marks = {}
for pos, t in d["marks"]:
    marks.setdefault(pos, []).append(d["mark_types"][t])

def render_word(i):
    w = words[i]
    before = "".join(m["sign"] + " " for m in marks.get(i, []) if m["side"] == "before")
    after = "".join(m["sign"] for m in marks.get(i, []) if m["side"] == "after" and m["kind"] != "sajdah_line")
    return before + w + after

def idx_of(starts, pos):
    # 1-based number of the unit that contains pos
    lo, hi = 0, len(starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if starts[mid] <= pos: lo = mid
        else: hi = mid - 1
    return lo + 1

STRIP = set("ۖۗۘۙۚۛۜ۝۞ۣ۟۠ۡۢۤۥۦۧۨ۩ٰ۪ۭ۫۬ـۥۦ")
def plain(t):
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch) and ch not in STRIP)
    for a, b in (("ٱ","ا"),("أ","ا"),("إ","ا"),("آ","ا"),("ى","ي"),("ة","ه"),("ۥ",""),("ۦ","")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()

ayah_starts = d["ayah_starts"]
page_starts = d["page_starts"]
juz_starts = d["juz_starts"]
surah_starts = d["surah_starts"]
surahs_meta = d["surahs"]

ayahs = []
for ai, start in enumerate(ayah_starts):
    end = ayah_starts[ai + 1] if ai + 1 < len(ayah_starts) else N
    s = idx_of(surah_starts, start)
    sm = surahs_meta[s - 1]
    num = ai - sm["first_ayah"] + 1
    text = " ".join(render_word(i) for i in range(start, end))
    ray = " ".join(r for r in rasm[start:end] if r)
    ayahs.append([s, num, idx_of(page_starts, start), idx_of(juz_starts, start), text, plain(text) if not ray else plain(ray)])

surahs = [{"n": sm["number"], "ar": sm["name_ar"], "en": sm["name_en"], "rev": sm["revelation"],
           "c": sm["ayah_count"], "p": ayahs[sm["first_ayah"]][2], "b": sm["has_basmalah"]} for sm in surahs_meta]

# rub' (quarter-hizb) boundaries: ayah index where ۞ appears + juz starts
rub = sorted(set([idx_of(ayah_starts, pos) - 1 for pos, t in d["marks"] if d["mark_types"][t]["kind"] == "division"] +
                 [idx_of(ayah_starts, p) - 1 for p in juz_starts]))

json.dump({"surahs": surahs, "ayahs": ayahs, "rub": rub}, open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("ayahs", len(ayahs), "pages", ayahs[-1][2], "rub", len(rub))
print(ayahs[0]); print(ayahs[261][4][:90]); print(ayahs[7][4][:60])
# sanity: page 1 and 2 content
print([a[:2] for a in ayahs if a[2] == 1][:3], [a[:2] for a in ayahs if a[2] == 2][:2], [a[:2] for a in ayahs if a[2] == 604][-1])
