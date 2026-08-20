#!/usr/bin/env python3
"""
Generates dark_mode.svg and light_mode.svg in the classic "neofetch" style:
ASCII-art portrait (converted from assets/profile.jpg) on the left,
dotted key/value system info + live GitHub stats on the right.
"""
import json
import urllib.request
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

USER = "kiranr12r"  # your GitHub username
ROOT = Path(__file__).resolve().parent
PHOTO = ROOT / "assets" / "profile.jpg"

RAMP = " .:-=+*#%@"


# ---------- ASCII ART ----------
def image_to_ascii(path, cols=54, rows=34, crop_box=None):
    im = Image.open(path).convert("RGB")
    if crop_box:
        im = im.crop(crop_box)
    gray = ImageOps.grayscale(im)
    gray = ImageEnhance.Contrast(gray).enhance(1.35)
    gray = ImageEnhance.Brightness(gray).enhance(1.05)
    gray = gray.resize((cols, rows))
    pixels = list(gray.getdata())
    lines = []
    for r in range(rows):
        row = []
        for c in range(cols):
            p = pixels[r * cols + c]
            idx = int(((255 - p) / 255) * (len(RAMP) - 1))
            row.append(RAMP[idx])
        lines.append("".join(row))
    return lines


# ---------- GITHUB STATS ----------
def api(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": USER},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def get_stats():
    u = api(f"/users/{USER}")
    repos = []
    page = 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&page={page}&type=owner")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    return {
        "repos": u.get("public_repos", len(repos)),
        "followers": u.get("followers", 0),
        "following": u.get("following", 0),
        "stars": stars,
    }


# ---------- ESCAPING ----------
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ---------- SVG BUILD ----------
def build_svg(ascii_lines, stats, dark=False):
    bg = "#0d1117" if dark else "#f6f8fa"
    fg = "#e6edf3" if dark else "#24292f"
    key_c = "#79c0ff" if dark else "#953800"
    val_c = "#a5d6ff" if dark else "#0a3069"
    cc = "#30363d" if dark else "#c2cfde"
    add_c = "#3fb950" if dark else "#1a7f37"

    width, height = 1080, 560
    ascii_x = 15
    ascii_y_start = 26
    line_h = 13.2
    ascii_font = 12

    info_x = 460
    row_h = 20

    svg_parts = [f'<svg xmlns="http://www.w3.org/2000/svg" font-family="Consolas,monospace" '
                 f'width="{width}px" height="{height}px" font-size="16px">']
    svg_parts.append('<style>text,tspan{white-space:pre;}</style>')
    svg_parts.append(f'<rect width="{width}px" height="{height}px" fill="{bg}" rx="15"/>')

    # ASCII art block (its own <text>, since it uses a different font-size)
    ascii_tspans = []
    y = ascii_y_start
    for line in ascii_lines:
        ascii_tspans.append(f'<tspan x="{ascii_x}" y="{y:.1f}">{esc(line)}</tspan>')
        y += line_h
    svg_parts.append(f'<text x="{ascii_x}" y="{ascii_y_start}" fill="{fg}" font-size="{ascii_font}px" '
                      f'font-family="Consolas,monospace">{"".join(ascii_tspans)}</text>')

    # Info block (neofetch key/value style)
    rows = [
        ("header", "kiran@github"),
        ("kv", "Role", "Full-Stack Developer | AI/ML Enthusiast"),
        ("kv", "Location", "India (UTC+05:30)"),
        ("kv", "IDE", "VS Code"),
        ("blank", None),
        ("kv", "Frontend", "React, Next.js, Tailwind CSS"),
        ("kv", "Backend", "Node.js, Express, Flask"),
        ("kv", "Languages", "JavaScript, TypeScript, Python, Java"),
        ("kv", "Databases", "MongoDB, PostgreSQL, MySQL"),
        ("blank", None),
        ("kv", "Email", "rkiru04@gmail.com"),
        ("kv", "Portfolio", "portfolios-chi-seven.vercel.app"),
        ("kv", "GitHub", "github.com/kiranr12r"),
        ("blank", None),
        ("header2", "GitHub Stats"),
        ("stat", None),
    ]

    info_tspans = []
    y = ascii_y_start + 4
    for row in rows:
        kind = row[0]
        if kind == "header":
            info_tspans.append(f'<tspan x="{info_x}" y="{y:.1f}" fill="{fg}" font-weight="700">{esc(row[1])}</tspan>'
                                f'<tspan fill="{cc}"> -——————————————————————————————-—-</tspan>')
            y += row_h
        elif kind == "header2":
            info_tspans.append(f'<tspan x="{info_x}" y="{y:.1f}" fill="{fg}" font-weight="700">- {esc(row[1])}</tspan>'
                                f'<tspan fill="{cc}"> -——————————————————————-—-</tspan>')
            y += row_h
        elif kind == "kv":
            label, value = row[1], row[2]
            dots = "." * max(3, 22 - len(label))
            info_tspans.append(f'<tspan x="{info_x}" y="{y:.1f}" fill="{cc}">. </tspan>'
                                f'<tspan fill="{key_c}">{esc(label)}</tspan>'
                                f'<tspan fill="{cc}">: {dots} </tspan>'
                                f'<tspan fill="{val_c}">{esc(value)}</tspan>')
            y += row_h
        elif kind == "stat":
            info_tspans.append(f'<tspan x="{info_x}" y="{y:.1f}" fill="{cc}">. </tspan>'
                                f'<tspan fill="{key_c}">Repos</tspan><tspan fill="{cc}">: .... </tspan>'
                                f'<tspan fill="{add_c}">{stats["repos"]}</tspan>'
                                f'<tspan fill="{cc}"> | </tspan>'
                                f'<tspan fill="{key_c}">Followers</tspan><tspan fill="{cc}">: .. </tspan>'
                                f'<tspan fill="{add_c}">{stats["followers"]}</tspan>')
            y += row_h
            info_tspans.append(f'<tspan x="{info_x}" y="{y:.1f}" fill="{cc}">. </tspan>'
                                f'<tspan fill="{key_c}">Following</tspan><tspan fill="{cc}">: . </tspan>'
                                f'<tspan fill="{add_c}">{stats["following"]}</tspan>'
                                f'<tspan fill="{cc}"> | </tspan>'
                                f'<tspan fill="{key_c}">Stars</tspan><tspan fill="{cc}">: .... </tspan>'
                                f'<tspan fill="{add_c}">{stats["stars"]}</tspan>')
            y += row_h
        else:  # blank
            y += row_h * 0.5

    svg_parts.append(f'<text font-size="14px">{"".join(info_tspans)}</text>')
    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def main():
    crop = (150, 60, 1400, 1500)  # head/shoulders/upper-torso bust crop
    ascii_lines = image_to_ascii(str(PHOTO), cols=54, rows=34, crop_box=crop)

    try:
        stats = get_stats()
    except Exception:
        # Falls back to placeholders if the API is unreachable (e.g. offline preview)
        stats = {"repos": "53", "followers": "4", "following": "10", "stars": "1"}

    (ROOT / "dark_mode.svg").write_text(build_svg(ascii_lines, stats, dark=True), encoding="utf-8")
    (ROOT / "light_mode.svg").write_text(build_svg(ascii_lines, stats, dark=False), encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
