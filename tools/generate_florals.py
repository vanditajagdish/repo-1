#!/usr/bin/env python3
"""Generates the botanical SVG artwork used across the site.

Everything is vector, so the illustrations stay crisp on any screen.
Re-run after tweaking:  python3 tools/generate_florals.py
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "img"

GOLD_STOPS = [("0", "#f3e3a3"), ("0.35", "#cdb064"), ("0.7", "#a88a3c"), ("1", "#e2c97e")]
LEAF_STOPS = [("0", "#c4ad5c"), ("0.45", "#8f8038"), ("0.75", "#a8954a"), ("1", "#c9b064")]
PETAL_STOPS = [("0", "#f4e4da"), ("0.6", "#dcbfb2"), ("1", "#b99384")]
STEM = "#26331f"
SPECK = "#2b3a22"
LINE = "#8f6d5e"

uid = 0


def nid(prefix):
    global uid
    uid += 1
    return f"{prefix}{uid}"


def defs():
    def grad(gid, stops, x2="1", y2="1"):
        s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
        return f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'

    return (
        "<defs>"
        + grad("gGold", GOLD_STOPS)
        + grad("gLeaf", LEAF_STOPS, "1", "0.3")
        + grad("gPetal", PETAL_STOPS, "0", "1")
        + grad("gPetalDark", [("0", "#d9c0b3"), ("1", "#a07e70")], "0", "1")
        + "</defs>"
    )


def f(v):
    return f"{v:.1f}"


# ---------------------------------------------------------------- leaf
def leaf(x, y, angle, length, width, wave=0.25, seed=0, flip=False):
    """A long wavy leaf, base at (x, y), pointing along `angle` degrees (0 = up)."""
    rnd = random.Random(seed)
    L, w = length, width
    s = -1 if flip else 1
    wv = wave * w
    # outline (local coords: base at 0,0, tip at 0,-L)
    d = (
        f"M0,0 C{f(s*w*0.9)},{f(-L*0.12)} {f(s*(w*1.15+wv))},{f(-L*0.42)} {f(s*w*0.55)},{f(-L*0.62)} "
        f"C{f(s*(w*0.2-wv))},{f(-L*0.78)} {f(s*w*0.35)},{f(-L*0.9)} {f(s*w*-0.15)},{f(-L)} "
        f"C{f(s*-w*0.35)},{f(-L*0.86)} {f(s*(-w*0.75+wv))},{f(-L*0.7)} {f(s*-w*0.6)},{f(-L*0.48)} "
        f"C{f(s*(-w*0.5-wv))},{f(-L*0.25)} {f(s*-w*0.45)},{f(-L*0.08)} 0,0 Z"
    )
    cid = nid("lc")
    speck = []
    n = int(L * w / 85)
    for _ in range(n):
        px = rnd.uniform(-w * 1.2, w * 1.4) * s
        py = rnd.uniform(-L, 0)
        a = rnd.uniform(-35, 35)
        ln = rnd.uniform(5, 9)
        # small doubled dashes like hand-inked speckles
        speck.append(
            f'<g transform="translate({f(px)},{f(py)}) rotate({f(a)})">'
            f'<path d="M{f(-ln/2)},0 H{f(ln/2)} M{f(-ln/2+1)},3 H{f(ln/2+1)}"/></g>'
        )
    vein = f"M0,-4 C{f(s*w*0.25)},{f(-L*0.35)} {f(s*w*0.3)},{f(-L*0.6)} {f(s*w*-0.1)},{f(-L*0.97)}"
    return (
        f'<g transform="translate({f(x)},{f(y)}) rotate({f(angle)})">'
        f'<clipPath id="{cid}"><path d="{d}"/></clipPath>'
        f'<path d="{d}" fill="url(#gLeaf)" stroke="url(#gGold)" stroke-width="2.6"/>'
        f'<g clip-path="url(#{cid})" stroke="{SPECK}" stroke-width="2" stroke-linecap="round" fill="none" opacity=".9">{"".join(speck)}</g>'
        f'<path d="{vein}" fill="none" stroke="#e8d792" stroke-width="1.4" opacity=".75"/>'
        "</g>"
    )


# ---------------------------------------------------------------- petals
def petal_path(L, w, curl=0.0):
    return (
        f"M0,0 C{f(w)},{f(L*0.25)} {f(w*0.85+curl)},{f(L*0.75)} {f(curl)},{f(L)} "
        f"C{f(-w*0.85+curl)},{f(L*0.75)} {f(-w)},{f(L*0.25)} 0,0 Z"
    )


def petal(L, w, rot, curl=0.0, dark=False, lines=5):
    d = petal_path(L, w, curl)
    inner = []
    for i in range(lines):
        t = (i + 1) / (lines + 1) * 2 - 1  # -1..1
        ex = curl + t * w * 0.25
        inner.append(
            f"M{f(t*w*0.15)},{f(L*0.08)} C{f(t*w*0.85)},{f(L*0.3)} {f(t*w*0.7+curl*0.6)},{f(L*0.7)} {f(ex)},{f(L*0.93)}"
        )
    fill = "url(#gPetalDark)" if dark else "url(#gPetal)"
    return (
        f'<g transform="rotate({f(rot)})">'
        f'<path d="{d}" fill="{fill}" stroke="#c9a493" stroke-width="1.6"/>'
        f'<path d="{" ".join(inner)}" fill="none" stroke="{LINE}" stroke-width="1" opacity=".75"/>'
        f'<path d="M0,{f(L*0.1)} C{f(curl*0.3)},{f(L*0.5)} {f(curl*0.7)},{f(L*0.75)} {f(curl)},{f(L*0.95)}" '
        f'fill="none" stroke="url(#gGold)" stroke-width="1.6"/>'
        "</g>"
    )


def stem(d, width=3.2):
    return f'<path d="{d}" fill="none" stroke="{STEM}" stroke-width="{width}" stroke-linecap="round"/>'


def calyx(r=10):
    return (
        f'<path d="M{-r},0 C{-r},{-r*1.4} {r},{-r*1.4} {r},0 C{r*0.4},{r*0.6} {-r*0.4},{r*0.6} {-r},0 Z" '
        f'fill="{STEM}" stroke="#4a5a3a" stroke-width="1"/>'
    )


def bell(x, y, angle, size=1.0):
    """Drooping bell flower (like a fritillary), hanging from (x, y)."""
    parts = [petal(150, 34, r, curl=c, dark=True, lines=4) for r, c in ((-28, -14), (28, 14))]
    parts += [petal(165, 40, r, curl=c, lines=6) for r, c in ((-12, -10), (12, 12), (0, 2))]
    # stamens peeking out
    st = "".join(
        f'<path d="M0,40 Q{f(dx*0.4)},{f(130)} {f(dx)},{f(190)}" fill="none" stroke="url(#gGold)" stroke-width="1.4"/>'
        f'<circle cx="{f(dx)}" cy="194" r="3.2" fill="url(#gGold)"/>'
        for dx in (-14, -4, 8)
    )
    return (
        f'<g transform="translate({f(x)},{f(y)}) rotate({f(angle)}) scale({size})">'
        + st
        + "".join(parts)
        + calyx(12)
        + "</g>"
    )


def star(x, y, angle, size=1.0):
    """Open star-like flower with wavy petals."""
    out = []
    for i, r in enumerate((-150, -95, -35, 30, 90, 150)):
        out.append(petal(120 + (i % 2) * 22, 26, r, curl=10 if i % 2 else -10, dark=i % 2 == 0, lines=4))
    centre = (
        '<circle r="16" fill="url(#gGold)"/>'
        '<circle r="9" fill="#b8954a"/>'
        + "".join(
            f'<line x1="0" y1="0" x2="{f(22*math.cos(a))}" y2="{f(22*math.sin(a))}" stroke="#7a5a3a" stroke-width="1.2"/>'
            for a in [k * math.pi / 5 for k in range(10)]
        )
    )
    return f'<g transform="translate({f(x)},{f(y)}) rotate({f(angle)}) scale({size})">' + "".join(out) + centre + "</g>"


def bud(x, y, angle, size=1.0):
    """Closed ribbed bud, attached at (x, y), hanging down."""
    L, w = 110, 34
    body = f"M0,0 C{w},{L*0.15} {w*1.05},{L*0.7} 0,{L} C{-w*1.05},{L*0.7} {-w},{L*0.15} 0,0 Z"
    ribs = " ".join(
        f"M0,6 C{f(t*w*1.0)},{f(L*0.3)} {f(t*w*0.9)},{f(L*0.75)} 0,{f(L*0.97)}"
        for t in (-0.75, -0.45, -0.15, 0.15, 0.45, 0.75)
    )
    return (
        f'<g transform="translate({f(x)},{f(y)}) rotate({f(angle)}) scale({size})">'
        f'<path d="{body}" fill="url(#gPetal)" stroke="#c9a493" stroke-width="1.6"/>'
        f'<path d="{ribs}" fill="none" stroke="{LINE}" stroke-width="1.1" opacity=".8"/>'
        f'<path d="M-12,4 C-24,30 -18,46 -6,52 M12,4 C24,30 18,46 6,52" fill="none" stroke="{STEM}" stroke-width="5" stroke-linecap="round"/>'
        + calyx(10)
        + "</g>"
    )


def svg(w, h, body, extra=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" {extra}>'
        + defs()
        + body
        + "</svg>\n"
    )


# ---------------------------------------------------------------- compositions
def frame():
    """Full portrait frame, like the invitation card (1000 x 1400)."""
    b = []
    # ---- top-left cluster
    b.append(stem("M40,820 C120,640 170,420 300,300"))
    b.append(leaf(40, 830, 18, 430, 70, seed=1))
    b.append(leaf(150, 640, 40, 220, 48, seed=2, flip=True))
    b.append(leaf(180, 150, 78, 420, 60, seed=3))
    b.append(stem("M210,250 C250,210 290,215 318,262"))
    b.append(bell(320, 262, -22, 1.05))
    # ---- top-right cluster
    b.append(stem("M965,980 C930,760 880,560 800,330", 3.6))
    b.append(stem("M800,330 C830,250 860,210 905,175"))
    b.append(leaf(840, 80, -60, 230, 46, seed=4))
    b.append(leaf(960, 1000, -14, 520, 72, seed=5, flip=True))
    b.append(leaf(800, 600, -50, 280, 56, seed=6))
    b.append(star(745, 340, 8, 1.15))
    # ---- mid-left
    b.append(stem("M60,1150 C40,1000 120,880 210,870"))
    b.append(bell(222, 880, -6, 1.05))
    # ---- mid-right
    b.append(stem("M930,1060 C910,960 880,890 830,860"))
    b.append(bell(820, 862, 34, 1.0))
    b.append(stem("M915,1000 C880,1040 870,1080 885,1120", 3))
    b.append(bud(885, 1112, -10, 0.9))
    # ---- bottom
    b.append(leaf(250, 1420, 22, 360, 62, seed=7))
    b.append(leaf(420, 1420, -12, 270, 52, seed=8, flip=True))
    b.append(stem("M380,1400 C380,1300 410,1220 460,1200", 3))
    b.append(bud(460, 1196, 8, 0.75))
    b.append(leaf(560, 1420, 58, 330, 58, seed=9))
    b.append(leaf(990, 1420, -30, 420, 64, seed=10, flip=True))
    b.append(leaf(720, 1430, -64, 300, 54, seed=11))
    return svg(1000, 1400, "".join(b), 'preserveAspectRatio="xMidYMid meet"')


def corner():
    """A top-left corner spray (600 x 600); mirror it with CSS for other corners."""
    b = [
        stem("M10,520 C60,380 130,240 260,170"),
        leaf(0, 540, 22, 400, 62, seed=21),
        leaf(80, 60, 82, 380, 56, seed=22),
        leaf(110, 380, 48, 200, 42, seed=23, flip=True),
        stem("M160,140 C210,110 250,120 268,168"),
        bell(270, 168, -26, 0.95),
    ]
    return svg(600, 600, "".join(b))


def sprig():
    """Horizontal divider sprig (600 x 140)."""
    b = [
        stem("M40,70 C200,64 400,64 560,70", 2.4),
        leaf(300, 72, -78, 230, 34, seed=31),
        leaf(300, 70, 78, 230, 34, seed=32, flip=True),
        leaf(300, 70, -100, 150, 26, seed=33, flip=True),
        leaf(300, 70, 100, 150, 26, seed=34),
        f'<circle cx="300" cy="70" r="9" fill="url(#gGold)"/>',
    ]
    return svg(600, 140, "".join(b))


def single_bell():
    b = [stem("M150,0 C150,40 160,70 150,96"), bell(150, 100, 0, 1.0)]
    return svg(300, 330, "".join(b))


def single_star():
    return svg(340, 340, star(170, 170, 0, 1.0))


def single_bud():
    return svg(160, 220, stem("M80,0 C80,30 85,50 80,62") + bud(80, 66, 0, 1.0))


def favicon():
    return svg(
        64, 64,
        '<rect width="64" height="64" rx="12" fill="#4a1220"/>'
        '<text x="32" y="43" text-anchor="middle" font-family="Georgia,serif" font-style="italic" '
        'font-size="30" fill="url(#gGold)">S&amp;K</text>'.replace("S&amp;K", "S&amp;K"),
    )


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "frame.svg": frame(),
        "corner.svg": corner(),
        "sprig.svg": sprig(),
        "bell.svg": single_bell(),
        "star.svg": single_star(),
        "bud.svg": single_bud(),
        "favicon.svg": favicon(),
    }
    for name, content in files.items():
        (OUT / name).write_text(content)
        print(f"wrote {name} ({len(content)//1024} KB)")
