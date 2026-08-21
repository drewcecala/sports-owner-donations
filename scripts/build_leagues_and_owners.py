"""The owner's box leans red — sports-owner political donations graphic.

Source: Kaggle dataset "Political donations by American sports owners"
(rahul253801, v1) — FiveThirtyEight's tracker of federal contributions by
U.S. pro-sports owners and commissioners, 2016 / 2018 / 2020 cycles, with
each recipient committee's party lean.

Buckets: R = Republican + "mostly Republican"; D = Democrat + "mostly
Democratic"; N = bipartisan + independent + no party listed ($0.85M).

Outputs: sports_owners_political_donations.png / .svg at the repo root.
"""

import os

import kagglehub
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, PathPatch
from matplotlib.path import Path

# ---------------------------------------------------------------- data ----

path = kagglehub.dataset_download("rahul253801/political-donations-by-american-sports-owners")
df = pd.read_csv(f"{path}/sports-political-donations.csv")
df["amt"] = df["Amount"].str.replace(r"[$,]", "", regex=True).astype(float)
BUCKET = {"Republican": "R", "Bipartisan, but mostly Republican": "R",
          "Democrat": "D", "Bipartisan, but mostly Democratic": "D",
          "Bipartisan": "N", "Independent": "N"}
df["b"] = df["Party"].map(BUCKET).fillna("N")   # NaN party -> neutral bucket

TOTAL = df.amt.sum()
tot = df.groupby("b").amt.sum()

LEAGUES = ["NASCAR", "NHL", "NFL", "MLB", "NBA", "WNBA"]
league_rows = []
for lg in LEAGUES:
    sub = df[df["League"].str.contains(lg)]
    g = sub.groupby("b").amt.sum()
    t = sub.amt.sum()
    league_rows.append(dict(lg=lg, total=t, R=g.get("R", 0) / t * 100,
                            N=g.get("N", 0) / t * 100, D=g.get("D", 0) / t * 100))
league_rows.sort(key=lambda r: -r["R"])

own = (df.pivot_table(index="Owner", columns="b", values="amt",
                      aggfunc="sum", fill_value=0)
         .assign(total=lambda x: x.sum(axis=1))
         .sort_values("total", ascending=False).head(12))
TEAMS = {
    "Charles Johnson": "Giants (MLB)", "Dan DeVos": "Magic (NBA)",
    "Peter Angelos": "Orioles (MLB)", "Jerry Reinsdorf": "Bulls + White Sox",
    "Philip F. Anschutz": "Kings (NHL)", "Jimmy and Susan Haslam": "Browns (NFL)",
    "Laura Ricketts": "Cubs (MLB)", "James L. Dolan": "Knicks + Rangers",
    "Dan Gilbert": "Cavaliers (NBA)", "Ken Kendrick": "D-backs (MLB)",
    "Janice S. McNair": "Texans (NFL)", "Ron Burkle": "Penguins (NHL)",
}

print("=== AUDIT ===")
print(f"total ${TOTAL:,.0f} | R ${tot['R']:,.0f} ({tot['R']/TOTAL*100:.1f}%) | "
      f"D ${tot['D']:,.0f} ({tot['D']/TOTAL*100:.1f}%) | N ${tot['N']:,.0f} ({tot['N']/TOTAL*100:.1f}%)")
print(f"{df.Owner.nunique()} owners, {len(df)} donations, years {sorted(df['Election Year'].unique())}")
for r in league_rows:
    print(f"{r['lg']:<7} ${r['total']/1e6:5.1f}M  R {r['R']:4.1f}%  N {r['N']:4.1f}%  D {r['D']:4.1f}%")
print(own[["R", "N", "D", "total"]].round(0).to_string())

# ------------------------------------------------------------- drawing ----

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
HAIR = "#e1e0d9"
BORDER = (0.043, 0.043, 0.043, 0.10)
RED = "#e34948"     # Republican
BLUE = "#2a78d6"    # Democratic
GRAY = "#d9d8d2"    # bipartisan / no party listed

plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
                     "svg.fonttype": "none", "text.color": INK,
                     "text.parse_math": False})

W, H = 12.6, 15.6
ML, MR = 0.9, 0.9
fig = plt.figure(figsize=(W, H), dpi=200, facecolor=SURFACE)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis("off")
ax.set_facecolor(SURFACE)

KAPPA = 0.5523


def rounded_rect(x, y, w, h, r, corners="all", **kw):
    """Rect with selected corners rounded ('all' | 'left' | 'right' | 'none')."""
    rx = min(r, h / 2, w / 2)
    k = KAPPA
    y0, y1 = y, y + h
    tr = br = rx if corners in ("all", "right") else 0
    tl = bl = rx if corners in ("all", "left") else 0
    verts, codes = [(x + tl, y0)], [Path.MOVETO]

    def seg(px, py):
        verts.append((px, py)); codes.append(Path.LINETO)

    def arc(cx, cy, sx, sy, ex, ey):
        verts.extend([(sx + k * (cx - sx), sy + k * (cy - sy)),
                      (ex + k * (cx - ex), ey + k * (cy - ey)), (ex, ey)])
        codes.extend([Path.CURVE4] * 3)

    seg(x + w - tr, y0)
    if tr:
        arc(x + w, y0, x + w - tr, y0, x + w, y0 + tr)
    seg(x + w, y1 - br)
    if br:
        arc(x + w, y1, x + w, y1 - br, x + w - br, y1)
    seg(x + bl, y1)
    if bl:
        arc(x, y1, x + bl, y1, x, y1 - bl)
    seg(x, y0 + tl)
    if tl:
        arc(x, y0, x, y0 + tl, x + tl, y0)
    verts.append(verts[0])
    codes.append(Path.CLOSEPOLY)
    ax.add_patch(PathPatch(Path(verts, codes), **kw))


def text(x, y, s, size, color=INK, weight="normal", ha="left", va="baseline", **kw):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
            ha=ha, va=va, **kw)


def hline(x0, x1, y, color=HAIR, lw=0.9):
    ax.add_line(Line2D([x0, x1], [y, y], color=color, lw=lw, solid_capstyle="butt"))


def dot(x, y, color, r=0.05):
    ax.add_patch(Circle((x, y), r, facecolor=color, edgecolor="none"))


def track(s):
    return " ".join(s)


def money(v):
    return f"${v/1e6:.1f}M"


# -------------------------------------------------------------- header ----
text(ML, 1.02, track("AMERICAN SPORTS OWNERS · FEDERAL POLITICAL GIVING · 2016–2020"),
     10.5, MUTED, "bold")
text(ML, 1.56, "The owner's box leans red", 27, INK, "bold")
sub = (f"Owners and commissioners across six U.S. sports leagues made ${TOTAL/1e6:.1f} million in federal political contributions over the 2016,\n"
       f"2018 and 2020 election cycles, per FiveThirtyEight's donation tracker — {tot['R']/TOTAL*100:.0f}% of the money went to Republican candidates and\n"
       "PACs, and only one league's ownership tilted blue: the WNBA's.")
text(ML, 1.82, sub, 11.5, INK2, va="top", linespacing=1.55)

# ------------------------------------------------------------ KPI band ----
y = 3.30
tile_h, gap = 1.28, 0.24
tile_w = (W - ML - MR - 2 * gap) / 3
tiles = [
    ("Total contributions", money(TOTAL), f"{len(df):,} donations · {df.Owner.nunique()} owners & commissioners"),
    ("To Republican candidates & PACs", money(tot["R"]), f"{tot['R']/TOTAL*100:.0f}% of all dollars"),
    ("To Democratic candidates & PACs", money(tot["D"]), f"{tot['D']/TOTAL*100:.0f}% — rest bipartisan or unlisted ({tot['N']/TOTAL*100:.0f}%)"),
]
for i, (label, value, foot) in enumerate(tiles):
    tx = ML + i * (tile_w + gap)
    rounded_rect(tx, y, tile_w, tile_h, 0.09, facecolor="#ffffff",
                 edgecolor=BORDER, linewidth=1)
    text(tx + 0.22, y + 0.40, label, 9.5, INK2)
    text(tx + 0.22, y + 0.87, value, 17, INK, "bold")
    text(tx + 0.22, y + 1.12, foot, 8.5, MUTED)

# ------------------------------------------------- panel A: by league ----
y = 5.24
text(ML, y, "Where each league's money went", 15.5, INK, "bold")
y += 0.34
text(ML, y, "Share of each ownership group's dollars by the recipient's party lean. "
            "Owners with teams in several leagues count toward each of them.", 9.5, INK2)
y += 0.40
lx = ML
for c, lab in [(RED, "Republican"), (GRAY, "bipartisan / no party listed"), (BLUE, "Democratic")]:
    dot(lx + 0.05, y - 0.04, c, r=0.05)
    text(lx + 0.18, y, lab, 8.5, INK2)
    lx += 0.18 + len(lab) * 0.055 + 0.32

y += 0.28
BAR_H, PITCH = 0.20, 0.47
max_l = max(r["R"] + r["N"] / 2 for r in league_rows)   # widest left arm (%)
max_r = max(r["D"] + r["N"] / 2 for r in league_rows)   # widest right arm (%)
FIELD_L = ML + 2.0            # room for league labels + left % labels
FIELD_R = W - MR - 0.55       # room for right % labels
UNIT = (FIELD_R - FIELD_L) / (max_l + max_r)
CX = FIELD_L + max_l * UNIT   # the 50/50 midline
top_a = y
ax.add_line(Line2D([CX, CX], [top_a - 0.06, top_a + 6 * PITCH - (PITCH - BAR_H) + 0.06],
                   color=HAIR, lw=0.9))
SGAP = 0.022
for i, r in enumerate(league_rows):
    by = top_a + i * PITCH
    text(ML, by + BAR_H - 0.035, r["lg"], 10, INK, "bold")
    text(ML, by + BAR_H + 0.135, money(r["total"]), 8, MUTED)
    x_left = CX - (r["R"] + r["N"] / 2) * UNIT
    segs = [(r["R"], RED), (r["N"], GRAY), (r["D"], BLUE)]
    sx = x_left
    for j, (pct, color) in enumerate(segs):
        w_in = pct * UNIT
        if w_in < 0.01:
            continue
        corner = "left" if j == 0 else ("right" if j == 2 else "none")
        rounded_rect(sx + (SGAP if j > 0 else 0), by,
                     w_in - (SGAP if j > 0 else 0), BAR_H, 0.03,
                     corners=corner, facecolor=color, edgecolor="none")
        sx += w_in
    text(x_left - 0.12, by + BAR_H - 0.04, f"{r['R']:.0f}%", 9, INK, "bold", ha="right")
    text(sx + 0.12, by + BAR_H - 0.04, f"{r['D']:.0f}%", 9, INK, "bold")

# --------------------------------------------- panel B: biggest donors ----
y = top_a + 6 * PITCH + 0.30
text(ML, y, "The twelve biggest checkbooks", 15.5, INK, "bold")
y += 0.34
text(ML, y, "Total federal giving by owner, 2016–2020 combined — same party coloring. "
            "One donor, Giants owner Charles Johnson, accounts for almost a quarter of all the money.", 9.5, INK2)
y += 0.34
BAR_X0 = ML + 2.95
B_H, B_PITCH = 0.17, 0.335
B_UNIT = (W - MR - BAR_X0 - 0.75) / own["total"].max()
for i, (owner, r) in enumerate(own.iterrows()):
    by = y + i * B_PITCH
    text(BAR_X0 - 0.16, by + B_H - 0.025, owner, 9, INK, "bold", ha="right")
    text(BAR_X0 - 0.16, by + B_H + 0.125, TEAMS.get(owner, ""), 7.5, MUTED, ha="right")
    sx = BAR_X0
    parts = [(r.get("R", 0), RED), (r.get("N", 0), GRAY), (r.get("D", 0), BLUE)]
    last_j = max(j for j, (v, _) in enumerate(parts) if v * B_UNIT >= 0.012)
    for j, (v, color) in enumerate(parts):
        w_in = v * B_UNIT
        if w_in < 0.012:
            continue
        g = SGAP if sx > BAR_X0 else 0
        rounded_rect(sx + g, by, w_in - g, B_H, 0.028,
                     corners="right" if j == last_j else "none",
                     facecolor=color, edgecolor="none")
        sx += w_in
    text(sx + 0.10, by + B_H - 0.03, money(r["total"]), 8.5, INK2)

# -------------------------------------------------------------- footer ----
y = y + 12 * B_PITCH + 0.28
hline(ML, W - MR, y)
foot = (
    "Source: “Political donations by American sports owners” (Kaggle · rahul253801, v1) — FiveThirtyEight's compilation of FEC records: 2,798 contributions to federal candidates,\n"
    "parties and PACs by 158 owners and commissioners in MLB, NBA, NFL, NHL, WNBA and NASCAR, 2016 / 2018 / 2020 cycles, with each recipient's party lean as classified by\n"
    "FiveThirtyEight. “Mostly Republican / mostly Democratic” bipartisan committees are folded into the respective party; $0.85M to committees with no party listed (largely Jerry\n"
    "Reinsdorf's $0.8M to three PACs) is counted as gray alongside bipartisan giving. League shares double-count owners who hold teams in more than one league."
)
text(ML, y + 0.16, foot, 7.3, MUTED, va="top", linespacing=1.65)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "sports_owners_political_donations")
fig.savefig(f"{OUT}.png", dpi=200, facecolor=SURFACE)
fig.savefig(f"{OUT}.svg", facecolor=SURFACE)
print(f"saved {OUT}.png / .svg")
