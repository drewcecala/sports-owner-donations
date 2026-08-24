"""Reddit / mobile cut of the sports-owner donation concentration story.

Same verified numbers as `build_concentration.py`, rebuilt for a
phone screen: 4:5 portrait, plain-language labels, no Lorenz curve (it is the
main comprehension barrier for a general audience), and one idea per section.

Lead finding: between the 2020 and 2024 elections, one owner gave about 2.3x more to
federal politics than every other U.S. pro-sports team owner combined.

Outputs output/sports_owners_donations_reddit.png (1200x1600).
"""

import os

import matplotlib

from data_sources import (
    GUARDIAN_ADELSON,
    GUARDIAN_DEMOCRATIC,
    GUARDIAN_REPUBLICAN,
    GUARDIAN_TOTAL_APPROX,
    load_fivethirtyeight_dataframe,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ----------------------------------------------------------------- style ---
SURFACE = "#fbfaf7"
INK = "#14150f"
INK2 = "#4a4b42"
MUTED = "#83817a"
GRID = "#e3ded2"
R_COL = "#c1352f"
D_COL = "#2a78d6"
N_COL = "#9c9a90"
HERO = "#7b1f1a"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "text.color": INK,
    "figure.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})

# ------------------------------------------------------------------ data ---
df = load_fivethirtyeight_dataframe()
BUCKET = {"Republican": "R", "Bipartisan, but mostly Republican": "R",
          "Democrat": "D", "Bipartisan, but mostly Democratic": "D",
          "Bipartisan": "N", "Independent": "N"}
df["b"] = df["Party"].map(BUCKET).fillna("N")

TOTAL = df.amt.sum()
owner_tot = df.groupby("Owner").amt.sum().sort_values(ascending=False)
TOP_NAME, TOP_AMT = owner_tot.index[0], owner_tot.iloc[0]


def split(frame):
    t = frame.amt.sum()
    g = frame.groupby("b").amt.sum()
    return t, 100 * g.get("R", 0) / t, 100 * g.get("D", 0) / t, 100 * g.get("N", 0) / t


A_ALL, A_EX = split(df), split(df[df.Owner != TOP_NAME])

G_R, G_D, G_ADELSON = GUARDIAN_REPUBLICAN, GUARDIAN_DEMOCRATIC, GUARDIAN_ADELSON
G_TOTAL = GUARDIAN_TOTAL_APPROX
G_OTHERS = G_TOTAL - G_ADELSON
RATIO = G_ADELSON / G_OTHERS
B_ALL = (G_TOTAL, 100 * G_R / G_TOTAL, 100 * G_D / G_TOTAL,
         100 * (G_TOTAL - G_R - G_D) / G_TOTAL)
B_EX = (G_OTHERS, 100 * (G_R - G_ADELSON) / G_OTHERS, 100 * G_D / G_OTHERS,
        100 * (G_TOTAL - G_R - G_D) / G_OTHERS)

print("Adelson  $%s   |  all other owners  $%s   |  ratio %.2fx"
      % (f"{G_ADELSON:,.0f}", f"{G_OTHERS:,.0f}", RATIO))
print("2021-24  R %.1f%% -> %.1f%% without Adelson  (%+.1f pts)"
      % (B_ALL[1], B_EX[1], B_EX[1] - B_ALL[1]))
print("2016-20  R %.1f%% -> %.1f%% without %s  (%+.1f pts)"
      % (A_ALL[1], A_EX[1], TOP_NAME, A_EX[1] - A_ALL[1]))

# ---------------------------------------------------------- league splits ---
# Owners holding teams in more than one league (e.g. "NBA, WNBA") count toward
# EACH listed league, so league dollar totals double-count those owners across
# leagues. Within-league shares are unaffected. Disclosed on the chart.
LEAGUES = ["NASCAR", "NHL", "NFL", "MLB", "NBA", "WNBA"]
lg_rows = []
for lg in LEAGUES:
    sub = df[df["League"].str.contains(lg)]
    t = sub.amt.sum()
    g = sub.groupby("b").amt.sum()
    lg_rows.append(dict(lg=lg, total=t, n=sub.Owner.nunique(),
                        R=100 * g.get("R", 0) / t,
                        N=100 * g.get("N", 0) / t,
                        D=100 * g.get("D", 0) / t))
lg_rows.sort(key=lambda r: -r["R"])
print("\nLEAGUES (2016-20):")
for r in lg_rows:
    print("  %-7s $%5.1fM  %2d owners  R %5.1f%%  D %5.1f%%"
          % (r["lg"], r["total"] / 1e6, r["n"], r["R"], r["D"]))

# ------------------------------------------------------------------ plot ---
FW, FH = 7.5, 10.0                        # 1200x1600 at 160 dpi
fig = plt.figure(figsize=(FW, FH))
L = 0.55 / FW
RGT = 1 - 0.55 / FW


def fy(i):
    return i / FH


def ax_at(x, y, w, h):
    return fig.add_axes([x / FW, y / FH, w / FW, h / FH])


def rule(yi):
    fig.add_artist(Line2D([L, RGT], [fy(yi), fy(yi)], color=GRID, lw=1.3))


# ------------------------------------------------------------------ title --
fig.text(L, fy(9.80), "One sports owner out-gave",
         fontsize=26, fontweight="bold", ha="left", va="top", color=INK)
fig.text(L, fy(9.38), "all the others combined",
         fontsize=26, fontweight="bold", ha="left", va="top", color=INK)
fig.text(L, fy(8.90),
         "Federal political donations by U.S. pro-sports team owners",
         fontsize=12.5, ha="left", va="top", color=INK2)

# ================================= HERO: Adelson vs everyone (2021-24) =====
fig.text(L, fy(8.56), "2020 ELECTION THROUGH 2024 ELECTION", fontsize=10.5,
         fontweight="bold", ha="left", va="top", color=MUTED)

hero = ax_at(0.55, 6.90, 6.40, 1.45)
hero.set_axis_off()
hero.set_xlim(0, 100)
hero.set_ylim(-1.05, 1.05)
for yy, val, money, who, col in [
    (0.45, 100.0, f"${G_ADELSON/1e6:.0f} million",
     "Miriam Adelson  ·  Dallas Mavericks", HERO),
    (-0.55, 100 * G_OTHERS / G_ADELSON, f"≈${G_OTHERS/1e6:.0f} million",
     "Every other team owner, combined", N_COL),
]:
    hero.text(0, yy + 0.30, who, fontsize=12.5, ha="left", va="bottom", color=INK2)
    hero.barh(yy, val, height=0.46, color=col, zorder=3)
    hero.text(1.8, yy, money, fontsize=18, fontweight="bold",
              ha="left", va="center", color="white", zorder=4)
hero.text(46, -0.55, f"≈{RATIO:.1f}× more than\neveryone else\nput together",
          fontsize=13, fontweight="bold", ha="left", va="center",
          color=INK, linespacing=1.5)

# --- what that one donor does to the topline (same period) ---
fig.text(L, fy(6.80), "That one donor is most of the reason the total looks lopsided",
         fontsize=12.5, fontweight="bold", ha="left", va="top", color=INK)

mini = ax_at(0.55, 5.45, 6.40, 0.98)
mini.set_axis_off()
mini.set_xlim(0, 126)
mini.set_ylim(-1.30, 0.72)
for yy, (tot, r, d, n), lab, ex in [(0.30, B_ALL, "All owners", False),
                                    (-0.85, B_EX, "Without Adelson", True)]:
    left = 0.0
    for val, col in ((r, R_COL), (n, N_COL), (d, D_COL)):
        mini.barh(yy, val, left=left, height=0.42, color=col,
                  alpha=0.45 if ex else 1.0, edgecolor=SURFACE, lw=1.4, zorder=3)
        left += val
    mini.text(0, yy + 0.28, lab, fontsize=11.5, ha="left", va="bottom",
              color=INK2 if ex else INK, fontweight="normal" if ex else "bold")
    mini.text(r / 2, yy, f"≈{r:.0f}% Republican", fontsize=12.5, ha="center",
              va="center", color="white", fontweight="bold", zorder=4)
mini.plot([102, 104.4, 104.4, 102], [0.30, 0.30, -0.85, -0.85],
          lw=1.4, color=INK2, zorder=5)
mini.text(107, -0.28, f"≈−{B_ALL[1]-B_EX[1]:.0f}\npoints", fontsize=12.5,
          fontweight="bold", va="center", ha="left", color=INK, linespacing=1.4)

rule(5.30)

# ================================== BY LEAGUE (2016-20, row-level data) ====
fig.text(L, fy(5.12), "Which leagues lean hardest?",
         fontsize=16.5, fontweight="bold", ha="left", va="top", color=INK)
fig.text(L, fy(4.80),
         "2016, 2018 and 2020 election cycles  ·  $47M from 158 owners and commissioners",
         fontsize=11.5, ha="left", va="top", color=MUTED)

lgax = ax_at(1.30, 2.48, 5.10, 2.10)
lgax.set_axis_off()
lgax.set_xlim(0, 100)

BH, BG = 0.60, 0.28
y, tops = 0.0, []
for r in lg_rows:
    left = 0.0
    for val, col in ((r["R"], R_COL), (r["N"], N_COL), (r["D"], D_COL)):
        lgax.barh(y, val, left=left, height=BH, color=col,
                  edgecolor=SURFACE, lw=1.4, zorder=3)
        left += val
    lgax.text(-2.5, y, r["lg"], fontsize=13.5, fontweight="bold",
              ha="right", va="center", color=INK)
    lgax.text(r["R"] / 2, y, f"{r['R']:.0f}%", fontsize=12.5, ha="center",
              va="center", color="white", fontweight="bold", zorder=4)
    if r["D"] >= 17:
        lgax.text(100 - r["D"] / 2, y, f"{r['D']:.0f}%", fontsize=12,
                  ha="center", va="center", color="white", fontweight="bold", zorder=4)
    lgax.text(103, y, f"${r['total']/1e6:.1f}M", fontsize=11,
              ha="left", va="center", color=MUTED)
    tops.append(y)
    y -= BH + BG

lgax.set_ylim(y + BG - 0.16, BH + 0.22)
# 50% reference line
lgax.plot([50, 50], [tops[-1] - BH / 2 - 0.08, BH + 0.02], ls=(0, (3, 3)),
          lw=1.5, color=INK, zorder=6)

handles = [
    Line2D([], [], marker="s", ls="", ms=12, mfc=R_COL, mec=R_COL, label="to Republicans"),
    Line2D([], [], marker="s", ls="", ms=12, mfc=N_COL, mec=N_COL, label="bipartisan / other"),
    Line2D([], [], marker="s", ls="", ms=12, mfc=D_COL, mec=D_COL, label="to Democrats"),
]
fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(L, fy(2.24)),
           frameon=False, fontsize=12, ncol=3, handletextpad=0.5, columnspacing=1.6)

fig.text(L, fy(2.08),
         "The WNBA is the only league whose owners gave more to Democrats than Republicans.",
         fontsize=11.5, color=INK, ha="left", va="top")

fig.text(L, fy(1.84),
         f"The one-donor effect shows up here too: the 2016\u201320 split was {A_ALL[1]:.0f}% Republican overall,\n"
         f"but {A_EX[1]:.0f}% with the biggest single giver ({TOP_NAME}) taken out.",
         fontsize=11, color=INK2, ha="left", va="top", linespacing=1.6)

# ----------------------------------------------------------------- footer --
fig.text(L, fy(1.30),
         "SOURCES  2021\u201324: The Guardian\u2019s analysis of FEC filings (pub. 5 Nov 2024), covering 4 Nov 2020 \u2013 16 Oct\n"
         "2024; at least $132.1M total, so derived figures are approximate.  2016\u201320 league panel:\n"
         "FiveThirtyEight \u201csports-political-donations\u201d (FEC), pinned to source commit e0c8091 \u2014 2,798 contributions by 158 owners.\n"
         "NOTES  Party lean is the recipient\u2019s, not the donor\u2019s. Federal donations only. Owners holding teams in\n"
         "more than one league count toward each, so league totals overlap. The two periods use different compilers\n"
         "and are not a continuous series.   TOOL  Python (pandas, matplotlib)   \u00b7   OC: Drew Cecala, 2026",
         fontsize=8.7, color=MUTED, ha="left", va="top", linespacing=1.55)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "sports_owners_donations_reddit")
fig.savefig(f"{OUT}.png", dpi=160)
print(f"\nwrote {OUT}.png  (1200x1600)")
