# -*- coding: utf-8 -*-
"""
Build the self-hosted GitHub stats card in the profile's design language.

Writes assets/stats-dark.svg and assets/stats-light.svg.
Runs locally or in GitHub Actions (needs a token with repo read access).

    GITHUB_TOKEN=xxx python scripts/build_stats.py
"""
import json
import os
import sys
import urllib.request
from datetime import date, timedelta

LOGIN = os.environ.get("GH_LOGIN", "Cikian")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
OUTDIR = os.environ.get("OUTDIR", "assets")

API = "https://api.github.com/graphql"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""

MONO = "'JetBrains Mono','SFMono-Regular',ui-monospace,Consolas,'Liberation Mono',monospace"
SANS = "Inter,'Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"

NOISE_LANGS = ("HTML", "CSS", "FreeMarker", "Dockerfile")

DARK = dict(bg1="#0C1324", bg2="#0E1730", glow_c_op="0.16", glow_v_op="0.18",
            title="#F1F5F9", sub="#64748B", updated="#5A6889", line="#1E2A44",
            tile_bg="#111B30", tile_bg_op="0.75", tile_stroke="#22304F",
            tile_label="#7E8BA8", tile_value="#F1F5F9", track="#1B2540",
            legend="#A3AFC8", pct="#7E8BA8", foot="#5A6889", outer="#232F4E")

LIGHT = dict(bg1="#FFFFFF", bg2="#F6F9FF", glow_c_op="0.10", glow_v_op="0.10",
             title="#0F172A", sub="#64748B", updated="#94A3B8", line="#E1E8F5",
             tile_bg="#F5F8FF", tile_bg_op="1", tile_stroke="#E1E8F5",
             tile_label="#7C89A8", tile_value="#0F172A", track="#EDF2FB",
             legend="#475569", pct="#64748B", foot="#94A3B8", outer="#E1E8F5")


def gql():
    if not TOKEN:
        sys.exit("missing GITHUB_TOKEN")
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    req = urllib.request.Request(
        API, data=body,
        headers={"Authorization": "Bearer " + TOKEN,
                 "Content-Type": "application/json",
                 "User-Agent": "cikian-profile-stats"})
    with urllib.request.urlopen(req, timeout=45) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit("graphql errors: %s" % payload["errors"])
    return payload["data"]["user"]


def streaks(days):
    seq = sorted(days, key=lambda d: d["date"])
    best = cur = 0
    for d in seq:
        if d["contributionCount"] > 0:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    have = {d["date"]: d["contributionCount"] for d in seq}
    today = date.today()
    start = today if have.get(today.isoformat(), 0) > 0 else today - timedelta(days=1)
    run = 0
    while have.get(start.isoformat(), 0) > 0:
        run += 1
        start -= timedelta(days=1)
    return run, best


def collect():
    u = gql()
    repos = u["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)
    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            lang = langs.setdefault(e["node"]["name"],
                                    {"size": 0, "color": e["node"]["color"] or "#8B949E"})
            lang["size"] += e["size"]
    for noise in NOISE_LANGS:
        langs.pop(noise, None)
    total = sum(v["size"] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: kv[1]["size"], reverse=True)[:6]
    top = [(n, v["size"] * 100.0 / total, v["color"]) for n, v in top]

    c = u["contributionsCollection"]
    days = [d for w in c["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    cur, best = streaks(days)
    return dict(stars=stars,
                commits=c["totalCommitContributions"],
                prs=c["totalPullRequestContributions"],
                issues=c["totalIssueContributions"],
                repos=c["totalRepositoriesWithContributedCommits"],
                public_repos=u["repositories"]["totalCount"],
                contribs=c["contributionCalendar"]["totalContributions"],
                streak=cur, longest=best, top=top,
                updated=date.today().isoformat())


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


W, H = 880, 286
TILE_W, TILE_H = 190, 50


def render(d, p):
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" role="img" aria-label="GitHub statistics for {LOGIN}">')
    a(f'<defs>'
      f'<linearGradient id="sbg" x1="0" y1="0" x2="{W}" y2="{H}" gradientUnits="userSpaceOnUse">'
      f'<stop stop-color="{p["bg1"]}"/><stop offset="1" stop-color="{p["bg2"]}"/></linearGradient>'
      f'<radialGradient id="sg" cx="0.5" cy="0.5" r="0.5">'
      f'<stop stop-color="#22D3EE" stop-opacity="{p["glow_c_op"]}"/><stop offset="1" stop-color="#22D3EE" stop-opacity="0"/></radialGradient>'
      f'<radialGradient id="sgv" cx="0.5" cy="0.5" r="0.5">'
      f'<stop stop-color="#A78BFA" stop-opacity="{p["glow_v_op"]}"/><stop offset="1" stop-color="#A78BFA" stop-opacity="0"/></radialGradient>'
      f'<clipPath id="sc"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
      f'</defs>')
    a('<g clip-path="url(#sc)">')
    a(f'<rect width="{W}" height="{H}" fill="url(#sbg)"/>')
    a(f'<ellipse cx="{W - 30}" cy="-70" rx="300" ry="200" fill="url(#sg)"/>')
    a(f'<ellipse cx="40" cy="{H + 60}" rx="320" ry="200" fill="url(#sgv)"/>')

    a(f'<g font-family="{SANS}">'
      f'<text x="32" y="42" font-size="18" font-weight="700" fill="{p["title"]}">GitHub in numbers</text>'
      f'<text x="32" y="62" font-size="11.5" fill="{p["sub"]}">pulled straight from the GraphQL API — refreshed daily by a workflow</text>'
      f'</g>')
    a(f'<text x="{W - 32}" y="42" font-size="10.5" letter-spacing="1.2" fill="{p["updated"]}" text-anchor="end" font-family="{MONO}">UPDATED {esc(d["updated"])}</text>')
    a(f'<line x1="32" y1="82" x2="{W - 32}" y2="82" stroke="{p["line"]}"/>')

    tiles = [
        ("TOTAL STARS", d["stars"], "#F59E0B"),
        ("COMMITS / 12 MO", d["commits"], "#22D3EE"),
        ("PULL REQUESTS", d["prs"], "#A78BFA"),
        ("ISSUES", d["issues"], "#F472B6"),
        ("REPOS CONTRIBUTED", d["repos"], "#34D399"),
        ("CURRENT STREAK", d["streak"], "#38BDF8"),
    ]
    for i, (label, value, color) in enumerate(tiles):
        x = 32 + (i % 2) * (TILE_W + 16)
        y = 98 + (i // 2) * (TILE_H + 8)
        a(f'<rect x="{x}" y="{y}" width="{TILE_W}" height="{TILE_H}" rx="12" fill="{p["tile_bg"]}" fill-opacity="{p["tile_bg_op"]}" stroke="{p["tile_stroke"]}"/>')
        a(f'<rect x="{x}" y="{y + 10}" width="2.5" height="{TILE_H - 20}" rx="1.25" fill="{color}" fill-opacity="0.9"/>')
        a(f'<text x="{x + 16}" y="{y + 20}" font-size="9.5" letter-spacing="1.3" fill="{p["tile_label"]}" font-family="{MONO}">{esc(label)}</text>')
        a(f'<text x="{x + 16}" y="{y + 40}" font-size="19" font-weight="700" fill="{p["tile_value"]}" font-family="{SANS}">{esc(value)}</text>')

    cx, cy, r, sw = 566, 184, 52, 16
    circ = 2 * 3.141592653589793 * r
    a(f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{p["track"]}" stroke-width="{sw}" fill="none"/>')
    acc = 0.0
    for name, pct, color in d["top"]:
        seg = circ * pct / 100.0
        dash = f'{max(seg - 2.5, 0.6):.2f} {circ - max(seg - 2.5, 0.6):.2f}'
        a(f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{color}" stroke-width="{sw}" fill="none" '
          f'stroke-dasharray="{dash}" stroke-dashoffset="{-acc:.2f}" transform="rotate(-90 {cx} {cy})" '
          f'stroke-linecap="round"/>')
        acc += seg
    if d["top"]:
        name, pct, color = d["top"][0]
        a(f'<text x="{cx}" y="{cy - 2}" font-size="19" font-weight="700" fill="{p["title"]}" text-anchor="middle" font-family="{SANS}">{pct:.0f}%</text>')
        a(f'<text x="{cx}" y="{cy + 15}" font-size="10.5" letter-spacing="1.1" fill="{color}" text-anchor="middle" font-family="{MONO}">{esc(name).upper()}</text>')

    a(f'<text x="648" y="106" font-size="9.5" letter-spacing="1.4" fill="{p["tile_label"]}" font-family="{MONO}">MOST USED LANGUAGES</text>')
    ly = 130
    for name, pct, color in d["top"]:
        a(f'<circle cx="652" cy="{ly - 4}" r="4" fill="{color}"/>')
        a(f'<text x="666" y="{ly}" font-size="12" fill="{p["legend"]}" font-family="{SANS}">{esc(name)}</text>')
        a(f'<text x="{W - 32}" y="{ly}" font-size="11.5" fill="{p["pct"]}" text-anchor="end" font-family="{MONO}">{pct:5.1f}%</text>')
        ly += 22

    a(f'<text x="{W - 32}" y="268" font-size="10.5" fill="{p["foot"]}" text-anchor="end" font-family="{MONO}">'
      f'{esc(d["contribs"])} CONTRIBS · BEST STREAK {esc(d["longest"])}D</text>')
    a("</g>")
    a(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="17.5" stroke="{p["outer"]}"/>')
    a("</svg>")
    return "\n".join(o)


def main():
    d = collect()
    os.makedirs(OUTDIR, exist_ok=True)
    for name, pal in (("stats-dark.svg", DARK), ("stats-light.svg", LIGHT)):
        path = os.path.join(OUTDIR, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(render(d, pal))
        print("wrote", path)
    print("stars=%s commits=%s langs=%s" % (d["stars"], d["commits"], len(d["top"])))


if __name__ == "__main__":
    main()
