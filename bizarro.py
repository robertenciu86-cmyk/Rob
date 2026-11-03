#!/usr/bin/env python3
"""Build brendancomedygroup.com: the bizarro twin of londoncomedygroup.com.

Usage: python3 bizarro.py <london-checkout> <output-dir>

Copies the London site, then flips it: Ridwan and Brendan swap places
(names, photos, credits, the catch game), London Comedy Group and Brendan
Comedy Group swap names, a pride theme goes on top, and Brendan gets a
gallery. Show times, venues and ticket links are left exactly as they are.
"""
import hashlib
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OVERLAY = HERE / "overlay"
LONDON_URL = "https://londoncomedygroup.com"
BRENDAN_URL = "https://brendancomedygroup.com"

# Not part of the public site, or London-only config.
SKIP = {".git", ".github", ".agents", ".claude", "scripts", "CNAME", "_config.yml",
        "README.md", "diff_script.txt", "skills-lock.json", "__pycache__"}

# Whole-word swaps. One regex pass, so A->B and B->A never collide.
SWAPS = {
    "Ridwan": "Brendan", "Brendan": "Ridwan",
    "ridwan": "brendan", "brendan": "ridwan",
    "RIDWAN": "BRENDAN", "BRENDAN": "RIDWAN",
    "Hussain": "Morris", "Morris": "Hussain",
    "hussain": "morris", "morris": "hussain",
    "richardhudsoncomedy": "vagabondbrendan", "vagabondbrendan": "richardhudsoncomedy",
    "London Comedy Group": "Brendan Comedy Group", "Brendan Comedy Group": "London Comedy Group",
    "londoncomedygroup.com": "brendancomedygroup.com", "brendancomedygroup.com": "londoncomedygroup.com",
}
# Longest first so "Brendan Comedy Group" wins over "Brendan".
SWAP_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in sorted(SWAPS, key=len, reverse=True)) + r")\b")

# Copy jokes, applied after the swaps. Missing ones are reported, not fatal,
# so a London copy edit never breaks the build.
COPY = [
    ("<title>Free Comedy Shows in London | Dates, Venues &amp; Tickets</title>",
     "<title>Brendan Comedy Group | Free Comedy in London, Brendan's Way</title>"),
    ('<p class="eyebrow">Live stand-up across London</p>',
     '<p class="eyebrow">Live stand-up across London · Brendan edition</p>'),
    ("<h1>Free comedy in London, almost every night</h1>",
     "<h1>Same shows. More Brendan. Fully fabulous.</h1>"),
    ("<h2>Meet the show runners</h2>",
     "<h2>Meet the show runners (they swapped bodies)</h2>"),
    ("<h2>Booked in three steps</h2>",
     "<h2>Booked in three steps (Brendan needed four)</h2>"),
    ("<p>Live stand-up comedy across London.</p>",
     "<p>Live stand-up comedy across London. Everyone welcome, especially you. 🏳️‍🌈</p>"),
    ('<meta name="theme-color" content="#090811">',
     '<meta name="theme-color" content="#1a0b2e">'),
]

BACK_BANNER = ('<div class="sister-banner"><a href="' + LONDON_URL + '/">'
               'Visit our sister site, <strong>London Comedy Group</strong> '
               '<span aria-hidden="true">→</span></a></div>')

GALLERY = [
    ("brendan-1", 600, 450, "Brendan on a stool on stage, head resting on his hands", "Thinking about the bit"),
    ("brendan-2", 600, 450, "Brendan on a stool on stage, eyes closed, head on his hands", "Still thinking about the bit"),
    ("brendan-3", 450, 600, "Brendan lying on the stage floor holding the mic", "The floor bit"),
    ("brendan-4", 450, 600, "Brendan lying across the stage, trainers in the air", "The floor bit, extended cut"),
    ("brendan-5", 450, 600, "Brendan lying on the stage, talking into the mic", "He's fine. We checked."),
    ("brendan-6", 450, 600, "Close-up of Brendan lying on stage, looking up", "Hello from down here"),
    ("brendan-7", 450, 600, "Brendan standing in front of a projector screen", "Brendan, after the floor bit"),
]


RIBBON = ["Everyone welcome", "Free comedy", "Love is love", "Laughs are laughs",
          "Trans joy", "Brendan approved", "Ridwan tolerated"]


def ribbon() -> str:
    # Two copies back to back so the marquee loops without a gap.
    spans = "".join(f"<span>{item}</span>" for item in RIBBON * 2)
    return f'\n    <div class="bz-ribbon-wrap" aria-hidden="true"><div class="bz-ribbon"><div>{spans}</div></div></div>'


def gallery_section() -> str:
    items = "".join(
        f'<a class="bz-shot" href="/gallery/{name}.webp" data-caption="{caption}">'
        f'<img src="/gallery/{name}-sm.webp" width="{w}" height="{h}" loading="lazy" alt="{alt}">'
        f"<span>{caption}</span></a>"
        for name, w, h, alt, caption in GALLERY
    )
    return f"""
    <section id="brendan" class="section wrap bz-gallery">
        <div class="section-heading"><p class="eyebrow">The main character</p><h2>The Brendan gallery</h2>
            <p>Our founder, our host, our floor enthusiast. Tap a photo to make it bigger.</p></div>
        <div class="bz-grid">{items}</div>
    </section>"""


def short_hash(*paths: Path) -> str:
    digest = hashlib.sha1()
    for path in paths:
        digest.update(path.read_bytes())
    return digest.hexdigest()[:8]


def transform(text: str, *, home: bool, version: str, missing: set[str]) -> str:
    # Hold back things that must not be swapped.
    held: list[str] = []

    def hold(match: re.Match) -> str:
        held.append(match.group(0))
        return f"\x00{len(held) - 1}\x00"

    # Canonical stays on London: it's the original, so search engines
    # don't treat the twin as competing duplicate content.
    text = re.sub(r'<link rel="canonical" href="[^"]*">', hold, text)
    # Email address and social accounts belong to the real London group.
    text = re.sub(r"londoncomedygroup@gmail\.com", hold, text)
    # The prize photo really is Brendan under a "Brendan Comedy Group" sign.
    text = re.sub(r"<img[^>]*brendan-comedy-group\.jpg[^>]*>", hold, text)

    text = SWAP_RE.sub(lambda m: SWAPS[m.group(0)], text)
    # Brendan's face replaces the London logo: small in the header, bigger for sharing.
    text = text.replace('src="/london-comedy-group-logo.jpg"', 'src="/brendan-logo.png"')
    text = text.replace("london-comedy-group-logo.jpg", "brendan-og.jpg")
    text = text.replace(f"{BRENDAN_URL}/comedy-audience.jpg", f"{BRENDAN_URL}/brendan-og.jpg")
    text = re.sub(
        r'<img class="hero-image" src="/comedy-audience\.jpg"[^>]*>',
        '<img class="hero-image bz-hero-logo" src="/brendan-hero.webp" width="800" height="800" fetchpriority="high"\n'
        '                 alt="Brendan Comedy Group: Brendan in a patchwork top and denim shorts, arms raised">',
        text,
    )
    text = re.sub(r'<div class="sister-banner">.*?</div>', BACK_BANNER, text, count=1, flags=re.S)

    for old, new in COPY:
        if old in text:
            text = text.replace(old, new)
        elif home:
            missing.add(old)

    text = text.replace(
        '<a href="/#comedians">Comedians</a>',
        '<a href="/#comedians">Comedians</a>\n                <a href="/#brendan">Brendan gallery</a>',
        1,
    )
    theme = f'<link rel="stylesheet" href="/assets/bizarro.css?v={version}">'
    text, linked = re.subn(
        r'(<link rel="stylesheet" href="/assets/site\.css\?v=[0-9a-f]+">)',
        rf"\1\n    {theme}",
        text,
        count=1,
    )
    if not linked:
        # Standalone pages (the catch game) carry inline styles instead of
        # site.css; load the theme last so its colour variables win.
        text = text.replace("</head>", f"    {theme}\n</head>", 1)
    if "<!doctype" in text[:40].lower() and "bizarro.js" not in text:
        text = text.replace("</body>", f'    <script src="/assets/bizarro.js?v={version}" defer></script>\n</body>', 1)

    if home:
        hero = text.find('<section class="hero">')
        hero_end = text.find("</section>", hero) if hero >= 0 else -1
        if hero_end >= 0:
            hero_end += len("</section>")
            text = text[:hero_end] + ribbon() + text[hero_end:]
        else:
            missing.add("hero section")
        anchor ='\n    <section class="section section-alt">\n        <div class="wrap"><div class="section-heading"><p class="eyebrow">From the rooms</p>'
        if anchor in text:
            text = text.replace(anchor, gallery_section() + anchor, 1)
        else:
            missing.add("gallery anchor")
            text = text.replace("</main>", gallery_section() + "</main>", 1)

    return re.sub(r"\x00(\d+)\x00", lambda m: held[int(m.group(1))], text)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src, out, ignore=lambda d, names: [n for n in names if n in SKIP])
    shutil.copytree(OVERLAY, out, dirs_exist_ok=True)

    version = short_hash(OVERLAY / "assets/bizarro.css", OVERLAY / "assets/bizarro.js")
    missing: set[str] = set()
    pages = 0
    for page in out.rglob("*.html"):
        rel = page.relative_to(out).as_posix()
        text = page.read_text(encoding="utf-8")
        page.write_text(transform(text, home=rel == "index.html", version=version, missing=missing), encoding="utf-8")
        pages += 1

    manifest = out / "site.webmanifest"
    if manifest.exists():
        manifest.write_text(
            manifest.read_text(encoding="utf-8")
            .replace('"London Comedy Group"', '"Brendan Comedy Group"')
            .replace('"LCG Shows"', '"BCG Shows"')
            .replace('"#090811"', '"#140825"'),
            encoding="utf-8",
        )
    robots = out / "robots.txt"
    robots.write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    (out / "sitemap.xml").unlink(missing_ok=True)

    for item in sorted(missing):
        print(f"warning: London copy changed, skipped: {item[:80]}")
    print(f"Bizarro'd {pages} pages into {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
