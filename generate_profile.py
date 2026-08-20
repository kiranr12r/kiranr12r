#!/usr/bin/env python3
"""
A one-of-a-kind GitHub profile card: a sci-fi "operative ID scan".
Dark mode  -> holographic HUD scanner with animated sweep + glowing bars.
Light mode -> technical blueprint / schematic spec-sheet aesthetic.

Both derive the portrait from assets/profile.jpg, converted to ASCII and
clipped into a circular scan frame.
"""
import json
import urllib.request
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

USER = "kiranr12r"  # your GitHub username
ROOT = Path(__file__).resolve().parent
PHOTO = ROOT / "assets" / "profile.jpg"

RAMP = " .:-=+*#%@"

SKILLS = ["React", "Next.js", "Tailwind", "Node.js", "Express", "Flask",
          "JavaScript", "TypeScript", "Python", "Java", "MongoDB", "PostgreSQL"]

CONTACT = [
    ("MAIL", "rkiru04@gmail.com"),
    ("WEB", "portfolios-chi-seven.vercel.app"),
    ("HUB", "github.com/kiranr12r"),
]


# ---------- ASCII ART ----------
def image_to_ascii(path, cols, rows, crop_box=None):
    im = Image.open(path).convert("RGB")
    if crop_box:
        im = im.crop(crop_box)
    gray = ImageOps.grayscale(im)
    gray = ImageEnhance.Contrast(gray).enhance(1.4)
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


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ---------- SVG BUILD ----------
def build_svg(ascii_lines, stats, dark=True):
    W, H = 1080, 600
    cx, cy, r = 210, 290, 165

    if dark:
        bg0, bg1 = "#050810", "#0b1220"
        panel_line = "#1b2a3d"
        cyan = "#4df3ff"
        cyan_dim = "#1c5866"
        magenta = "#ff3fb0"
        text_main = "#d9f6ff"
        text_dim = "#5c7a8a"
        bar_bg = "#0f1c28"
        green = "#39ff88"
        frame_stroke = cyan
    else:
        bg0, bg1 = "#f4f7fb", "#e7edf5"
        panel_line = "#b9c8d9"
        cyan = "#0a5c8a"
        cyan_dim = "#7ea3bd"
        magenta = "#b5185f"
        text_main = "#132635"
        text_dim = "#5b7284"
        bar_bg = "#dbe4ee"
        green = "#127a3e"
        frame_stroke = "#0a5c8a"

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}px" height="{H}px" '
                f'viewBox="0 0 {W} {H}" font-family="Consolas,Menlo,monospace">')

    # ---- defs ----
    svg.append('<defs>')
    svg.append(f'<linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">'
                f'<stop offset="0" stop-color="{bg0}"/><stop offset="1" stop-color="{bg1}"/></linearGradient>')
    svg.append(f'<clipPath id="circleClip"><circle cx="{cx}" cy="{cy}" r="{r-6}"/></clipPath>')
    svg.append(f'<radialGradient id="sweepGrad" cx="50%" cy="50%" r="50%">'
                f'<stop offset="0%" stop-color="{cyan}" stop-opacity="0"/>'
                f'<stop offset="85%" stop-color="{cyan}" stop-opacity="0"/>'
                f'<stop offset="100%" stop-color="{cyan}" stop-opacity="0.55"/></radialGradient>')
    svg.append(f'<linearGradient id="scanLine" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="{cyan}" stop-opacity="0"/>'
                f'<stop offset="0.5" stop-color="{cyan}" stop-opacity="0.85"/>'
                f'<stop offset="1" stop-color="{cyan}" stop-opacity="0"/></linearGradient>')
    svg.append('<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
                '<feGaussianBlur stdDeviation="3" result="b"/>'
                '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    # hex grid pattern
    svg.append(f'<pattern id="hex" width="42" height="24" patternUnits="userSpaceOnUse" '
                f'patternTransform="translate(0,0)">'
                f'<path d="M10 0 L31 0 L42 12 L31 24 L10 24 L0 12 Z" fill="none" '
                f'stroke="{panel_line}" stroke-width="0.6" opacity="0.35"/></pattern>')
    svg.append('</defs>')

    svg.append(f'<rect width="{W}" height="{H}" fill="url(#bgGrad)" rx="18"/>')
    svg.append(f'<rect width="{W}" height="{H}" fill="url(#hex)" rx="18"/>')

    # ---- corner brackets (outer frame) ----
    bl = 26
    for (bx, by, dx, dy) in [(18, 18, 1, 1), (W - 18, 18, -1, 1), (18, H - 18, 1, -1), (W - 18, H - 18, -1, -1)]:
        svg.append(f'<path d="M{bx} {by + dy*bl} L{bx} {by} L{bx + dx*bl} {by}" '
                    f'fill="none" stroke="{cyan}" stroke-width="2.5"/>')

    label = "SCANNER ACTIVE" if dark else "SPEC SHEET"
    svg.append(f'<text x="42" y="46" fill="{cyan}" font-size="13" letter-spacing="3">{label}</text>')
    svg.append(f'<text x="{W-42}" y="46" fill="{text_dim}" font-size="12" text-anchor="end">FILE #0001</text>')

    # ---- circular scan frame ----
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{frame_stroke}" stroke-width="2" opacity="0.9"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r+10}" fill="none" stroke="{frame_stroke}" stroke-width="1" '
                f'stroke-dasharray="3 6" opacity="0.5">'
                f'<animateTransform attributeName="transform" type="rotate" '
                f'from="0 {cx} {cy}" to="360 {cx} {cy}" dur="18s" repeatCount="indefinite"/></circle>')
    # tick marks around ring
    import math
    ticks = []
    for i in range(36):
        ang = math.radians(i * 10)
        r1, r2 = r + 14, r + 20 if i % 3 == 0 else r + 17
        x1, y1 = cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)
        x2, y2 = cx + r2 * math.cos(ang), cy + r2 * math.sin(ang)
        ticks.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                      f'stroke="{cyan_dim}" stroke-width="1"/>')
    svg.append("".join(ticks))

    # ascii portrait clipped to circle
    svg.append(f'<g clip-path="url(#circleClip)">')
    svg.append(f'<rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" fill="{bar_bg}"/>')
    fx, fy_start, fline = cx - r + 6, cy - r + 14, 9.4
    tspans = []
    yy = fy_start
    for line in ascii_lines:
        tspans.append(f'<tspan x="{fx}" y="{yy:.1f}">{esc(line)}</tspan>')
        yy += fline
    svg.append(f'<text fill="{text_main}" font-size="8.6px" font-family="Consolas,monospace">{"".join(tspans)}</text>')
    # animated sweep line moving down through the circle, looping
    svg.append(f'<rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="14" fill="url(#scanLine)">'
                f'<animate attributeName="y" from="{cy-r}" to="{cy+r}" dur="3.2s" repeatCount="indefinite"/>'
                f'</rect>')
    svg.append('</g>')

    # status dot
    dot_c = green
    svg.append(f'<circle cx="{cx - r + 16}" cy="{cy + r + 26}" r="5" fill="{dot_c}">'
                f'<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></circle>')
    status = "IDENTITY VERIFIED" if dark else "PROFILE ON FILE"
    svg.append(f'<text x="{cx - r + 28}" y="{cy + r + 30}" fill="{dot_c}" font-size="12" letter-spacing="1.5">{status}</text>')

    # ---- name / glitch title ----
    name_y = cy + r + 62
    if dark:
        svg.append(f'<text x="{cx-r}" y="{name_y}" fill="{magenta}" font-size="30" font-weight="700" opacity="0.55" transform="translate(-2,1)">KIRAN R</text>')
        svg.append(f'<text x="{cx-r}" y="{name_y}" fill="{cyan}" font-size="30" font-weight="700" opacity="0.55" transform="translate(2,-1)">KIRAN R</text>')
    svg.append(f'<text x="{cx-r}" y="{name_y}" fill="{text_main}" font-size="30" font-weight="700">KIRAN R</text>')
    svg.append(f'<text x="{cx-r}" y="{name_y+24}" fill="{text_dim}" font-size="14">Full-Stack Developer // AI-ML Enthusiast</text>')
    svg.append(f'<text x="{cx-r}" y="{name_y+44}" fill="{text_dim}" font-size="12">India · UTC+05:30 · VS Code</text>')

    # ---- right column: stat bars ----
    rx = 480
    ry = 96
    row_gap = 46
    max_val = max(stats["repos"], stats["followers"] * 4, stats["following"] * 4, stats["stars"] * 2, 60)
    bar_w = 420

    svg.append(f'<text x="{rx}" y="{ry-24}" fill="{text_main}" font-size="15" font-weight="700" letter-spacing="2">TELEMETRY</text>')
    svg.append(f'<line x1="{rx}" y1="{ry-14}" x2="{rx+bar_w}" y2="{ry-14}" stroke="{panel_line}" stroke-width="1"/>')

    bar_defs = [
        ("REPOS", stats["repos"], stats["repos"]),
        ("FOLLOWERS", stats["followers"], stats["followers"] * 4),
        ("FOLLOWING", stats["following"], stats["following"] * 4),
        ("STARS", stats["stars"], stats["stars"] * 2),
    ]
    yy = ry
    for i, (label, real_val, scaled) in enumerate(bar_defs):
        w = max(6, min(bar_w, (scaled / max_val) * bar_w))
        svg.append(f'<text x="{rx}" y="{yy}" fill="{text_dim}" font-size="12" letter-spacing="1">{label}</text>')
        svg.append(f'<text x="{rx+bar_w}" y="{yy}" fill="{cyan}" font-size="13" text-anchor="end" font-weight="700">{real_val}</text>')
        svg.append(f'<rect x="{rx}" y="{yy+8}" width="{bar_w}" height="8" rx="4" fill="{bar_bg}"/>')
        svg.append(f'<rect x="{rx}" y="{yy+8}" height="8" rx="4" fill="{cyan}" filter="url(#glow)">'
                    f'<animate attributeName="width" from="0" to="{w:.1f}" dur="1.1s" begin="{0.15*i:.2f}s" fill="freeze"/></rect>')
        yy += row_gap

    # ---- skill chips ----
    chip_y0 = yy + 12
    svg.append(f'<text x="{rx}" y="{chip_y0}" fill="{text_main}" font-size="15" font-weight="700" letter-spacing="2">STACK</text>')
    chip_y0 += 16
    cx_pos = rx
    cy_pos = chip_y0 + 10
    max_x = rx + bar_w
    chips = []
    for s in SKILLS:
        w = 15 + len(s) * 7.4
        if cx_pos + w > max_x:
            cx_pos = rx
            cy_pos += 30
        chips.append(f'<rect x="{cx_pos:.1f}" y="{cy_pos-16:.1f}" width="{w:.1f}" height="24" rx="12" '
                      f'fill="none" stroke="{cyan_dim}" stroke-width="1.2"/>')
        chips.append(f'<text x="{cx_pos+w/2:.1f}" y="{cy_pos:.1f}" fill="{text_main}" font-size="11.5" text-anchor="middle">{esc(s)}</text>')
        cx_pos += w + 10
    svg.append("".join(chips))

    # ---- contact rows ----
    contact_y = cy_pos + 40
    svg.append(f'<text x="{rx}" y="{contact_y}" fill="{text_main}" font-size="15" font-weight="700" letter-spacing="2">CONTACT</text>')
    contact_y += 6
    svg.append(f'<line x1="{rx}" y1="{contact_y}" x2="{rx+bar_w}" y2="{contact_y}" stroke="{panel_line}" stroke-width="1"/>')
    contact_y += 24
    for tag, val in CONTACT:
        svg.append(f'<rect x="{rx}" y="{contact_y-14}" width="52" height="20" rx="4" fill="none" stroke="{cyan_dim}"/>')
        svg.append(f'<text x="{rx+26}" y="{contact_y}" fill="{cyan}" font-size="10.5" text-anchor="middle">{tag}</text>')
        svg.append(f'<text x="{rx+66}" y="{contact_y}" fill="{text_main}" font-size="13">{esc(val)}</text>')
        contact_y += 28

    # ---- bottom terminal line ----
    term_y = H - 24
    svg.append(f'<text x="42" y="{term_y}" fill="{green}" font-size="13">'
                f'&gt; profile_scan --status'
                f'<tspan fill="{text_dim}"> ... complete</tspan></text>')
    svg.append(f'<rect x="330" y="{term_y-11}" width="8" height="14" fill="{green}">'
                f'<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>')

    svg.append('</svg>')
    return "\n".join(svg)


def main():
    crop = (150, 60, 1400, 1500)
    ascii_lines = image_to_ascii(str(PHOTO), cols=34, rows=34, crop_box=crop)

    try:
        stats = get_stats()
    except Exception:
        stats = {"repos": 53, "followers": 4, "following": 10, "stars": 1}

    (ROOT / "dark_mode.svg").write_text(build_svg(ascii_lines, stats, dark=True), encoding="utf-8")
    (ROOT / "light_mode.svg").write_text(build_svg(ascii_lines, stats, dark=False), encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
