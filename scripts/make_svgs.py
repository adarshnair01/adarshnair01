"""Generate the animated SVGs for the GitHub profile README (light + dark).

All animation is SMIL (<animate>, <animateMotion>), which GitHub keeps when it
serves an SVG as an image, and which works in Chrome, Firefox and Safari.
No scripts, no external fonts.
"""
import math
import sys
from xml.sax.saxutils import escape
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

THEMES = {
    "dark": dict(bg="#0d1117", panel="#161b22", border="#30363d", grid="#21262d",
                 text="#e6edf3", muted="#8b949e", a1="#58a6ff", a2="#bc8cff",
                 glow1="#1f6feb", glow2="#8957e5", glow_op="0.35"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", border="#d1d9e0", grid="#eaeef2",
                  text="#1f2328", muted="#59636e", a1="#0969da", a2="#8250df",
                  glow1="#b6e3ff", glow2="#e8d5ff", glow_op="0.7"),
}

ROLES = [
    "Data Science Manager",
    "Machine Learning Engineer",
    "Recommendation Systems & Forecasting",
]


def text_width(s, size):
    # Rough width for system UI fonts (about 0.53 em per character)
    return len(s) * size * 0.53


def response_curve(x0, y0, x1, y1, n=60):
    """A saturating response curve (Hill, shape 1.6) from bottom-left to top-right."""
    pts = []
    for i in range(n + 1):
        t = i / n
        s = t * 3.2
        h = s ** 1.6 / (s ** 1.6 + 1.0)
        h /= 3.2 ** 1.6 / (3.2 ** 1.6 + 1.0)
        pts.append((x0 + (x1 - x0) * t, y0 - (y0 - y1) * h))
    return pts


def header(t):
    W, H = 1200, 340
    roles = []
    cycle = 4 * len(ROLES)
    for i, role in enumerate(ROLES):
        w = text_width(role, 30) + 6
        begin = f"{4 * i}s"
        roles.append(f"""
    <g opacity="0">
      <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.31;0.33;1" dur="{cycle}s" begin="{begin}" repeatCount="indefinite"/>
      <clipPath id="clip{i}"><rect x="64" y="190" height="44" width="0">
        <animate attributeName="width" values="0;{w:.0f};{w:.0f};0;0" keyTimes="0;0.12;0.31;0.33;1" dur="{cycle}s" begin="{begin}" repeatCount="indefinite"/>
      </rect></clipPath>
      <text x="64" y="222" font-size="30" font-weight="500" fill="{t['text']}" clip-path="url(#clip{i})">{escape(role)}</text>
      <rect y="196" width="3" height="32" fill="{t['a1']}" x="66">
        <animate attributeName="x" values="66;{66 + w:.0f};{66 + w:.0f};66;66" keyTimes="0;0.12;0.31;0.33;1" dur="{cycle}s" begin="{begin}" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.5;0.51;0.99;1" dur="0.9s" repeatCount="indefinite"/>
      </rect>
    </g>""")

    pts = response_curve(760, 280, 1130, 96)
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))

    # Observed weeks scattered around the curve (deterministic)
    dots = []
    for k, frac in enumerate([0.06, 0.13, 0.21, 0.3, 0.38, 0.47, 0.55, 0.64, 0.73, 0.82, 0.9, 0.97]):
        x, y = pts[int(frac * (len(pts) - 1))]
        jitter = ((k * 37) % 23 - 11)
        dots.append(
            f'<circle cx="{x:.1f}" cy="{y + jitter:.1f}" r="4" fill="{t["muted"]}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.8;0.8;0" keyTimes="0;0.08;0.9;1" dur="8s" begin="{0.15 * k:.2f}s" repeatCount="indefinite"/></circle>')

    grid = "".join(
        f'<line x1="760" x2="1140" y1="{y}" y2="{y}" stroke="{t["grid"]}" stroke-width="1"/>' for y in (100, 160, 220))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Adarsh Nair: Data Science Manager and Machine Learning Engineer">
  <title>Adarsh Nair: Data Science Manager and Machine Learning Engineer</title>
  <defs>
    <linearGradient id="name" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/>
    </linearGradient>
    <linearGradient id="curve" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/>
    </linearGradient>
    <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="4"/></filter>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  </defs>
  <g clip-path="url(#frame)" font-family="{FONT}">
    <rect width="{W}" height="{H}" fill="{t['bg']}"/>
    <circle cx="180" cy="60" r="220" fill="{t['glow1']}" opacity="{t['glow_op']}" filter="url(#blur)">
      <animate attributeName="cx" values="180;300;180" dur="14s" repeatCount="indefinite"/>
    </circle>
    <circle cx="1000" cy="300" r="240" fill="{t['glow2']}" opacity="{t['glow_op']}" filter="url(#blur)">
      <animate attributeName="cx" values="1000;880;1000" dur="16s" repeatCount="indefinite"/>
    </circle>
    <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{t['border']}"/>

    <text x="64" y="96" font-size="18" letter-spacing="4" fill="{t['muted']}">HI, I'M</text>
    <text x="64" y="162" font-size="64" font-weight="700" fill="url(#name)">Adarsh Nair</text>
    {''.join(roles)}
    <text x="64" y="282" font-size="18" fill="{t['muted']}">Bengaluru, India  ·  Senior Data Science Manager at Yum! Brands</text>

    {grid}
    <line x1="760" x2="1140" y1="280" y2="280" stroke="{t['border']}" stroke-width="1.5"/>
    <line x1="760" x2="760" y1="80" y2="280" stroke="{t['border']}" stroke-width="1.5"/>
    <text x="1140" y="306" font-size="14" text-anchor="end" fill="{t['muted']}">spend →</text>
    <text x="748" y="88" font-size="14" text-anchor="end" fill="{t['muted']}">revenue</text>
    {''.join(dots)}
    <path id="rc" d="{d}" fill="none" stroke="url(#curve)" stroke-width="4" stroke-linecap="round"
          stroke-dasharray="{length:.0f}" stroke-dashoffset="{length:.0f}">
      <animate attributeName="stroke-dashoffset" values="{length:.0f};0;0;{length:.0f}" keyTimes="0;0.3;0.9;1" dur="8s" repeatCount="indefinite"/>
    </path>
    <g opacity="0">
      <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.3;0.32;0.88;0.9;1" dur="8s" repeatCount="indefinite"/>
      <circle r="12" fill="{t['a2']}" opacity="0.5" filter="url(#glow)">
        <animateMotion dur="8s" repeatCount="indefinite" keyPoints="0;0;1;1" keyTimes="0;0.3;0.85;1" calcMode="linear"><mpath xlink:href="#rc"/></animateMotion>
      </circle>
      <circle r="6" fill="{t['a2']}">
        <animateMotion dur="8s" repeatCount="indefinite" keyPoints="0;0;1;1" keyTimes="0;0.3;0.85;1" calcMode="linear"><mpath xlink:href="#rc"/></animateMotion>
      </circle>
    </g>
    <text x="1130" y="70" font-size="14" text-anchor="end" fill="{t['muted']}" opacity="0">diminishing returns
      <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.35;0.45;0.88;0.9;1" dur="8s" repeatCount="indefinite"/>
    </text>
  </g>
</svg>
"""


IMPACT = [
    ("5M+", "daily users served by", "a two-tower recommender"),
    ("+10%", "conversion lift from", "a propensity model"),
    ("2,000+", "stores forecast up to", "4 weeks ahead"),
    ("+25%", "sales-forecast accuracy", "improvement"),
]


def impact(t):
    W, H = 1200, 210
    tw, gap, x0 = 270, 20, 30
    tiles = []
    for i, (value, l1, l2) in enumerate(IMPACT):
        x = x0 + i * (tw + gap)
        b = 0.25 * i
        tiles.append(f"""
    <g opacity="0" transform="translate(0 12)">
      <animate attributeName="opacity" from="0" to="1" begin="{b}s" dur="0.6s" fill="freeze"/>
      <animateTransform attributeName="transform" type="translate" from="0 12" to="0 0" begin="{b}s" dur="0.6s" fill="freeze"/>
      <rect x="{x}" y="20" width="{tw}" height="170" rx="14" fill="{t['panel']}" stroke="{t['border']}"/>
      <text x="{x + 24}" y="86" font-size="46" font-weight="700" fill="url(#val)">{value}</text>
      <rect x="{x + 24}" y="104" width="0" height="3" rx="1.5" fill="url(#val)">
        <animate attributeName="width" values="0;64;64" keyTimes="0;0.15;1" begin="{b + 0.3}s" dur="6s" repeatCount="indefinite"/>
      </rect>
      <text x="{x + 24}" y="140" font-size="16" fill="{t['text']}">{l1}</text>
      <text x="{x + 24}" y="164" font-size="16" fill="{t['muted']}">{l2}</text>
    </g>""")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Impact: 5M+ daily users, +10% conversion, 2,000+ stores forecast, +25% forecast accuracy">
  <title>Impact: 5M+ daily users, +10% conversion, 2,000+ stores forecast, +25% forecast accuracy</title>
  <defs>
    <linearGradient id="val" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/>
    </linearGradient>
  </defs>
  <g font-family="{FONT}">{''.join(tiles)}
  </g>
</svg>
"""


def divider(t):
    W, H = 1200, 70
    def wave(phase, amp, y):
        pts = [f"{x} {y + amp * math.sin((x / W) * 4 * math.pi + phase):.1f}" for x in range(0, W * 2 + 1, 20)]
        return "M" + " L".join(pts)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Thanks for visiting">
  <title>Thanks for visiting</title>
  <defs>
    <linearGradient id="w" x1="0" x2="1"><stop offset="0" stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/></linearGradient>
  </defs>
  <g fill="none" stroke="url(#w)" stroke-linecap="round">
    <path d="{wave(0, 12, 35)}" stroke-width="2.5" opacity="0.9">
      <animateTransform attributeName="transform" type="translate" from="0 0" to="-600 0" dur="8s" repeatCount="indefinite"/>
    </path>
    <path d="{wave(1.6, 8, 35)}" stroke-width="1.5" opacity="0.5">
      <animateTransform attributeName="transform" type="translate" from="-600 0" to="0 0" dur="11s" repeatCount="indefinite"/>
    </path>
  </g>
</svg>
"""



CAREER = [
    ("2016", ["Software", "Developer"], "MAQ Software"),
    ("2017", ["Data", "Scientist"], "Kvantum Inc."),
    ("2019", ["Senior Data", "Scientist"], "Kvantum Inc."),
    ("2020", ["Principal Data", "Scientist"], "Kvantum Inc."),
    ("2021", ["Data Science", "Manager"], "Yum! Brands"),
    ("2022", ["Senior Data Science", "Manager"], "Yum! Brands"),
]


def timeline(t):
    W, H = 1200, 216
    x0, step, y = 110, 196, 80
    nodes = []
    for i, (year, role, company) in enumerate(CAREER):
        x = x0 + i * step
        b = 0.3 + 0.35 * i
        last = i == len(CAREER) - 1
        pulse = (f'<circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{t["a2"]}" stroke-width="2">'
                 f'<animate attributeName="r" values="9;22" dur="1.8s" begin="{b + 0.4:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0.8;0" dur="1.8s" begin="{b + 0.4:.2f}s" repeatCount="indefinite"/></circle>') if last else ""
        lines = "".join(
            f'<text x="{x}" y="{146 + 20 * k}" font-size="15" font-weight="{600 if last else 500}" text-anchor="middle" fill="{t["text"]}">{r}</text>'
            for k, r in enumerate(role))
        nodes.append(f"""
    <g opacity="0">
      <animate attributeName="opacity" from="0" to="1" begin="{b:.2f}s" dur="0.5s" fill="freeze"/>
      <text x="{x}" y="{y - 26}" font-size="16" font-weight="600" text-anchor="middle" fill="{t['a1'] if not last else t['a2']}">{year}{' – now' if last else ''}</text>
      {pulse}
      <circle cx="{x}" cy="{y}" r="9" fill="{t['bg']}" stroke="url(#tl)" stroke-width="3"/>
      <circle cx="{x}" cy="{y}" r="{4 if not last else 5}" fill="{t['a2'] if last else t['a1']}"/>
      {lines}
      <text x="{x}" y="{146 + 20 * len(role) + 6}" font-size="14" text-anchor="middle" fill="{t['muted']}">{company}</text>
    </g>""")
    x_end = x0 + (len(CAREER) - 1) * step
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Career: Software Developer at MAQ Software (2016), Data Scientist, Senior and Principal Data Scientist at Kvantum (2017 to 2021), Data Science Manager and Senior Data Science Manager at Yum! Brands (2021 to now)">
  <title>Career timeline, 2016 to now</title>
  <defs>
    <linearGradient id="tl" gradientUnits="userSpaceOnUse" x1="{x0 - 50}" x2="{x_end + 50}" y1="0" y2="0">
      <stop offset="0" stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/>
    </linearGradient>
  </defs>
  <g font-family="{FONT}">
    <line x1="{x0 - 50}" x2="{x_end + 50}" y1="{y}" y2="{y}" stroke="{t['grid']}" stroke-width="4" stroke-linecap="round"/>
    <line x1="{x0 - 50}" x2="{x0 - 50}" y1="{y}" y2="{y}" stroke="url(#tl)" stroke-width="4" stroke-linecap="round">
      <animate attributeName="x2" from="{x0 - 50}" to="{x_end + 50}" begin="0.2s" dur="2.2s" fill="freeze"/>
    </line>{''.join(nodes)}
  </g>
</svg>
"""

for name, t in THEMES.items():
    (OUT / f"header-{name}.svg").write_text(header(t))
    (OUT / f"impact-{name}.svg").write_text(impact(t))
    (OUT / f"divider-{name}.svg").write_text(divider(t))
    (OUT / f"timeline-{name}.svg").write_text(timeline(t))
print("written:", sorted(p.name for p in OUT.iterdir()))
