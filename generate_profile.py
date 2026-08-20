#!/usr/bin/env python3
import json, re, urllib.request
from pathlib import Path

USER = "kiranr12r"
ROOT = Path(__file__).resolve().parent

def api(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": USER},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

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
forks = sum(r.get("forks_count", 0) for r in repos)
commits = 0

for r in repos[:100]:
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{USER}/{r['name']}/commits?author={USER}&per_page=1",
            headers={"Accept":"application/vnd.github+json","User-Agent":USER},
        )
        with urllib.request.urlopen(req, timeout=10) as res:
            link = res.headers.get("Link","")
            m = re.search(r'[?&]page=(\d+)>; rel="last"', link)
            commits += int(m.group(1)) if m else len(json.load(res))
    except Exception:
        pass

stats = {
    "repos": u.get("public_repos", len(repos)),
    "followers": u.get("followers", 0),
    "following": u.get("following", 0),
    "stars": stars,
    "forks": forks,
    "commits": commits,
}

def svg(dark):
    bg, panel = ("#0d1117","#111827") if dark else ("#f6f8fa","#ffffff")
    fg, muted = ("#e6edf3","#8b949e") if dark else ("#24292f","#57606a")
    cyan, green, border = ("#79c0ff","#7ee787","#30363d") if dark else ("#0969da","#1a7f37","#d0d7de")
    rows = [
        ("$ whoami",cyan,1),("Kiran R",fg,1),("Full-Stack Developer  |  AI/ML Enthusiast",muted,0),("","",0),
        ("$ cat system.txt",cyan,1),("OS          : India • UTC+05:30",fg,0),("Focus       : Full-Stack + AI/ML",fg,0),
        ("Learning    : TypeScript • AI/ML • Modern Backend",fg,0),("IDE         : VS Code",fg,0),("","",0),
        ("$ cat stack.txt",cyan,1),("Frontend    : React • Next.js • Tailwind CSS",fg,0),
        ("Backend     : Node.js • Express • Flask",fg,0),("Languages   : JavaScript • TypeScript • Python • Java",fg,0),
        ("Data        : MongoDB • PostgreSQL • MySQL",fg,0),("Tools       : Git • GitHub • Docker",fg,0),("","",0),
        ("$ github --stats",cyan,1),(f"Repos       : {stats['repos']}",green,0),(f"Followers   : {stats['followers']}",green,0),
        (f"Following   : {stats['following']}",green,0),(f"Stars       : {stats['stars']}",green,0),
        (f"Forks       : {stats['forks']}",green,0),(f"Commits*    : {stats['commits']}",green,0),("","",0),
        ("$ projects --pinned",cyan,1),("AI Smart Port Navigation",fg,0),("Open Source Finder",fg,0),
        ("AI Proctoring System",fg,0),("Vendor Management System",fg,0),("","",0),
        ("$ contact",cyan,1),("Email       : rkiru04@gmail.com",fg,0),
        ("Portfolio   : portfolios-chi-seven.vercel.app",fg,0),("GitHub      : github.com/kiranr12r",fg,0),("","",0),
        ('$ echo "Always learning. Always building."',cyan,1)
    ]
    y=88
    out=[]
    for s,c,b in rows:
        if not s:
            y += 9
            continue
        out.append(f'<text x="350" y="{y}" fill="{c}" font-family="monospace" font-size="{16 if b else 14}" font-weight="{"700" if b else "400"}">{esc(s)}</text>')
        y += 20
    h=max(720,y+30)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{h}" viewBox="0 0 1200 {h}">
<rect width="1200" height="{h}" rx="18" fill="{bg}"/>
<rect x="18" y="18" width="1164" height="{h-36}" rx="14" fill="{panel}" stroke="{border}" stroke-width="2"/>
<circle cx="58" cy="52" r="7" fill="{green}"/><circle cx="82" cy="52" r="7" fill="{muted}"/><circle cx="106" cy="52" r="7" fill="{muted}"/>
<text x="145" y="58" fill="{muted}" font-family="monospace" font-size="14">kiranr12r@github:~</text>
<rect x="48" y="88" width="250" height="{h-136}" rx="12" fill="{bg}" stroke="{border}"/>
<image href="https://raw.githubusercontent.com/kiranr12r/kiranr12r/main/assets/profile.jpg" x="68" y="112" width="210" height="270" preserveAspectRatio="xMidYMid slice"/>
<rect x="68" y="112" width="210" height="270" rx="8" fill="none" stroke="{border}" stroke-width="2"/>
<text x="68" y="420" fill="{fg}" font-family="monospace" font-size="22" font-weight="700">KIRAN R</text>
<text x="68" y="448" fill="{muted}" font-family="monospace" font-size="14">Full-Stack Developer</text>
<text x="68" y="470" fill="{muted}" font-family="monospace" font-size="14">AI/ML Enthusiast</text>
{''.join(out)}
</svg>'''

Path(ROOT/"dark_mode.svg").write_text(svg(True), encoding="utf-8")
Path(ROOT/"light_mode.svg").write_text(svg(False), encoding="utf-8")
