"""The megadonor effect — concentration in sports-owner political giving.

A companion to `build_leagues_and_owners.py`. Where that chart asks *which
way* sports-owner money leans, this one asks *how few people* decide the answer.

Two sources, deliberately kept visually distinct because they are not the same
kind of evidence:

  A. 2016 / 2018 / 2020 cycles — FiveThirtyEight's `sports-political-donations`
     dataset (FEC records), via the Kaggle mirror. Row-level: 2,798 individual
     contributions by 158 owners and commissioners. Every figure drawn from this
     source is recomputed from the rows at build time and printed in the audit
     block below.

  B. 4 Nov 2020 - 16 Oct 2024 — The Guardian's analysis of FEC filings
     (published 5 Nov 2024). Published aggregates only; no row-level file is
     available, so these figures are transcribed constants, not recomputed.
     They are labeled as such on the chart.

Outputs PNG + SVG to output/ and prints a full audit table.
"""

import os

import kagglehub
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ----------------------------------------------------------------- style ---
SURFACE = "#fbfaf7"
INK = "#14150f"
INK2 = "#55564c"
MUTED = "#8b897f"
GRID = "#e3ded2"
R_COL = "#c1352f"   # Republican-leaning recipients
D_COL = "#2a78d6"   # Democratic-leaning recipients
N_COL = "#9c9a90"   # bipartisan / independent / unlisted

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "text.color": INK,
    "figure.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})

# ------------------------------------------------------------------ data ---
path = kagglehub.dataset_download("rahul253801/political-donations-by-american-sports-owners")
df = pd.read_csv(f"{path}/sports-political-donations.csv")
df["amt"] = df["Amount"].astype(str).str.replace(r"[$,\s]", "", regex=True).astype(float)

BUCKET = {"Republican": "R", "Bipartisan, but mostly Republican": "R",
          "Democrat": "D", "Bipartisan, but mostly Democratic": "D",
          "Bipartisan": "N", "Independent": "N"}
df["b"] = df["Party"].map(BUCKET).fillna("N")   # blank party -> neutral bucket

TOTAL = df.amt.sum()
N_OWNERS = df.Owner.nunique()
owner_tot = df.groupby("Owner").amt.sum().sort_values(ascending=False)
TOP_NAME = owner_tot.index[0]
TOP_AMT = owner_tot.iloc[0]


def split(frame):
    """Return (total, %R, %D, %N) for a slice of contributions."""
    t = frame.amt.sum()
    g = frame.groupby("b").amt.sum()
    return t, 100 * g.get("R", 0) / t, 100 * g.get("D", 0) / t, 100 * g.get("N", 0) / t


A_ALL = split(df)
A_EX = split(df[df.Owner != TOP_NAME])

# Lorenz-style concentration curve, richest donor first
cum_share = np.concatenate([[0], owner_tot.cumsum().values / TOTAL * 100])
donor_share = np.linspace(0, 100, len(cum_share))


def cum_at(n):
    """Share of all dollars given by the top-n donors."""
    return owner_tot.head(n).sum() / TOTAL * 100


# --- Source B: Guardian published aggregates (transcribed, not recomputed) ---
G_R, G_D, G_ADELSON = 124_806_435, 5_215_693, 92_275_100
G_TOTAL = G_R / 0.945                       # Guardian states R = 94.5% of total
G_N = G_TOTAL - G_R - G_D
B_ALL = (G_TOTAL, 100 * G_R / G_TOTAL, 100 * G_D / G_TOTAL, 100 * G_N / G_TOTAL)
_t = G_TOTAL - G_ADELSON                     # assumes Adelson's giving is ~all R
B_EX = (_t, 100 * (G_R - G_ADELSON) / _t, 100 * G_D / _t, 100 * G_N / _t)

# ----------------------------------------------------------------- audit ---
print("=" * 78)
print("AUDIT — every number drawn on the chart")
print("=" * 78)
print(f"\n[A] FiveThirtyEight / FEC, 2016+2018+2020 cycles  (recomputed from rows)")
print(f"    contributions {len(df):,} | owners {N_OWNERS} | total ${TOTAL:,.0f}")
print(f"    all owners            R {A_ALL[1]:5.1f}%  D {A_ALL[2]:5.1f}%  N {A_ALL[3]:4.1f}%   ${A_ALL[0]:,.0f}")
print(f"    excl. {TOP_NAME:<16} R {A_EX[1]:5.1f}%  D {A_EX[2]:5.1f}%  N {A_EX[3]:4.1f}%   ${A_EX[0]:,.0f}")
print(f"    -> removing 1 of {N_OWNERS} donors moves R share {A_ALL[1]-A_EX[1]:+.1f} pts")
print(f"\n    concentration:")
for n in (1, 3, 5, 10, 20, 50):
    print(f"      top {n:>2} donors ({100*n/N_OWNERS:4.1f}% of givers) = {cum_at(n):5.1f}% of dollars")
print(f"      median donor ${owner_tot.median():,.0f} | mean ${owner_tot.mean():,.0f}")
print(f"\n    top donor: {TOP_NAME} ${TOP_AMT:,.0f} = {100*TOP_AMT/TOTAL:.1f}% of all dollars")
print(f"\n[B] Guardian / FEC, 4 Nov 2020 - 16 Oct 2024  (transcribed aggregates)")
print(f"    all owners            R {B_ALL[1]:5.1f}%  D {B_ALL[2]:5.1f}%  N {B_ALL[3]:4.1f}%   ${B_ALL[0]:,.0f}")
print(f"    excl. Miriam Adelson  R {B_EX[1]:5.1f}%  D {B_EX[2]:5.1f}%  N {B_EX[3]:4.1f}%   ${B_EX[0]:,.0f}")
print(f"    -> removing 1 donor moves R share {B_ALL[1]-B_EX[1]:+.1f} pts")
print(f"    Adelson ${G_ADELSON:,.0f} = {100*G_ADELSON/G_TOTAL:.1f}% of all dollars in window")
print("=" * 78)

# ------------------------------------------------------------------ plot ---
FW, FH = 16.5, 11.6
fig = plt.figure(figsize=(FW, FH))
L = 1.15 / FW          # common left margin (figure fraction)


def ax_at(x, y, w, h):
    return fig.add_axes([x / FW, y / FH, w / FW, h / FH])


# ------------------------------------------------------------- title block --
fig.text(L, 0.953, "A handful of people decide which way the owner's box leans",
         fontsize=26, fontweight="bold", ha="left", va="top", color=INK)
fig.text(L, 0.909,
         "Federal political contributions by U.S. pro-sports team owners and commissioners. In both periods below, removing a single donor moves\n"
         "the league-wide partisan split by 8 to 13 percentage points — the topline describes the few who give most, not owners as a group.",
         fontsize=13, ha="left", va="top", color=INK2, linespacing=1.55)

PANEL_Y, PANEL_H = 3.45, 5.40
AX, AW = 1.15, 6.05
BX, BW = 9.10, 5.95

# ====================================================== PANEL A: Lorenz  ====
fig.text(AX / FW, (PANEL_Y + PANEL_H + 0.50) / FH, "How concentrated is the money?",
         fontsize=16, fontweight="bold", color=INK, ha="left", va="bottom")
fig.text(AX / FW, (PANEL_Y + PANEL_H + 0.22) / FH,
         f"{N_OWNERS} owners and commissioners · {len(df):,} contributions · 2016, 2018 and 2020 cycles",
         fontsize=11, color=MUTED, ha="left", va="bottom")

axA = ax_at(AX, PANEL_Y, AW, PANEL_H)
axA.plot([0, 100], [0, 100], ls=(0, (4, 4)), lw=1.4, color=MUTED, zorder=2)
axA.text(70, 62, "if every owner\ngave equally", fontsize=10, color=MUTED,
         ha="center", va="center", rotation=33, linespacing=1.45)

axA.fill_between(donor_share, cum_share, donor_share, color=R_COL, alpha=0.10, zorder=1)
axA.plot(donor_share, cum_share, lw=3.0, color=INK, zorder=5, solid_capstyle="round")

# annotations placed into empty space to the right of the curve
for n, tx, ty in ((1, 12, 20), (10, 20, 45), (20, 30, 68)):
    x, y = 100 * n / N_OWNERS, cum_at(n)
    axA.plot([x], [y], "o", ms=8.5, mfc=R_COL, mec=SURFACE, mew=2.0, zorder=6)
    lbl = f"top {n} donor" + ("" if n == 1 else "s") + f" = {y:.0f}%\nof all dollars"
    axA.annotate(lbl, xy=(x, y), xytext=(tx, ty), fontsize=10.8,
                 color=INK, va="center", ha="left", linespacing=1.5, zorder=7,
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.1,
                                 shrinkA=0, shrinkB=5))

axA.set_xlim(0, 100)
axA.set_ylim(0, 100)
axA.set_xlabel("share of donors  (largest first)", fontsize=11.5, color=INK2, labelpad=9)
axA.set_ylabel("cumulative share of dollars", fontsize=11.5, color=INK2, labelpad=9)
axA.set_xticks(range(0, 101, 25))
axA.set_yticks(range(0, 101, 25))
axA.set_xticklabels([f"{v}%" for v in range(0, 101, 25)], fontsize=10.5, color=MUTED)
axA.set_yticklabels([f"{v}%" for v in range(0, 101, 25)], fontsize=10.5, color=MUTED)
axA.grid(color=GRID, lw=0.9, zorder=0)
axA.set_axisbelow(True)
for s in ("top", "right"):
    axA.spines[s].set_visible(False)
for s in ("left", "bottom"):
    axA.spines[s].set_color(GRID)

axA.text(52, 11,
         f"The median owner gave ${owner_tot.median():,.0f}.\n"
         f"The average is ${owner_tot.mean():,.0f} — pulled\nup by the top of the curve.",
         fontsize=10.8, color=INK2, ha="left", va="center", linespacing=1.6, zorder=8,
         bbox=dict(boxstyle="round,pad=0.62", fc=SURFACE, ec=GRID, lw=1.1))

# ============================================== PANEL B: megadonor effect ===
fig.text(BX / FW, (PANEL_Y + PANEL_H + 0.68) / FH,
         "What happens if you remove the single largest donor?",
         fontsize=16, fontweight="bold", color=INK, ha="left", va="bottom")
fig.text(BX / FW, (PANEL_Y + PANEL_H + 0.30) / FH,
         "Share of each period's dollars by recipient party lean",
         fontsize=11, color=MUTED, ha="left", va="bottom")

axB = ax_at(BX, PANEL_Y, BW, PANEL_H)
axB.set_axis_off()

rows = [
    ("2021–24 · every owner",   B_ALL, False),
    ("2021–24 · minus Adelson", B_EX,  True),
    ("2016–20 · every owner",   A_ALL, False),
    ("2016–20 · minus Johnson", A_EX,  True),
]

BAR_H, GAP = 0.60, 0.34
y, ypos = 0.0, []
for label, (tot, r, d, n), is_ex in rows:
    left = 0.0
    for val, col in ((r, R_COL), (n, N_COL), (d, D_COL)):
        axB.barh(y, val, left=left, height=BAR_H, color=col,
                 alpha=0.45 if is_ex else 1.0,
                 edgecolor=SURFACE, linewidth=1.6, zorder=3)
        left += val
    axB.text(-3, y, label, fontsize=11.8, ha="right", va="center",
             color=INK2 if is_ex else INK,
             fontweight="normal" if is_ex else "bold")
    axB.text(r / 2, y, f"{r:.1f}%", fontsize=12.4, ha="center", va="center",
             color="white", fontweight="bold", zorder=4)
    if d > 16:
        axB.text(100 - d / 2, y, f"{d:.1f}%", fontsize=11.2, ha="center",
                 va="center", color="white", fontweight="bold", zorder=4)
    axB.text(104, y, f"${tot/1e6:,.1f}M", fontsize=11.2, ha="left", va="center",
             color=MUTED)
    ypos.append(y)
    y -= BAR_H + GAP

# delta brackets, parked clear of the dollar-total column
XB = 126
for i in (0, 2):
    y0, y1 = ypos[i], ypos[i + 1]
    r0, r1 = rows[i][1][1], rows[i + 1][1][1]
    axB.plot([XB, XB + 2.2, XB + 2.2, XB], [y0, y0, y1, y1], lw=1.3, color=INK2, zorder=5)
    axB.text(XB + 5.5, (y0 + y1) / 2, f"−{r0-r1:.1f} pts\nwithout\none donor",
             fontsize=10.8, va="center", ha="left", color=INK, linespacing=1.5)

axB.set_xlim(-42, 168)
axB.set_ylim(y + 0.34, BAR_H)

fig.text(BX / FW, (PANEL_Y - 0.34) / FH,
         f"Miriam Adelson (Mavericks) alone accounts for {100*G_ADELSON/G_TOTAL:.0f}% of all owner money in 2021–24.\n"
         f"{TOP_NAME} (Giants) accounts for {100*TOP_AMT/TOTAL:.0f}% in 2016–20.",
         fontsize=10.8, color=INK2, ha="left", va="top", linespacing=1.6)

# ----------------------------------------------------------------- legend --
handles = [
    Line2D([], [], marker="s", ls="", ms=13, mfc=R_COL, mec=R_COL, label="Republican-leaning recipient"),
    Line2D([], [], marker="s", ls="", ms=13, mfc=N_COL, mec=N_COL, label="Bipartisan / independent / unlisted"),
    Line2D([], [], marker="s", ls="", ms=13, mfc=D_COL, mec=D_COL, label="Democratic-leaning recipient"),
]
fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(L, 0.181),
           frameon=False, fontsize=11.5, ncol=3, handletextpad=0.6, columnspacing=2.6)

# --------------------------------------------------- sources / tools / method
fig.text(L, 0.151, "SOURCES · TOOLS · METHOD", fontsize=9.5, fontweight="bold",
         color=INK2, ha="left", va="top")
fig.text(L, 0.129,
         "2016–20  FiveThirtyEight “sports-political-donations” (FEC records), via Kaggle mirror rahul253801 v1 — 2,798 contributions by 158 owners; every figure recomputed from the rows at build time.\n"
         "2021–24  The Guardian’s analysis of FEC filings, published 5 Nov 2024, covering 4 Nov 2020 – 16 Oct 2024 — published aggregates transcribed, not recomputed. The Guardian notes its totals are\n"
         "“presumed to be a fraction of the actual contributions.”  The two periods use different compilers and party-lean rules, so they are shown as separate snapshots, not a continuous series.\n"
         "METHOD  Party lean is each source’s classification of the recipient committee, not of the donor. “Minus Adelson” assumes her giving is ~entirely Republican-leaning. Federal contributions only —\n"
         "no state or local giving, and no undisclosed spending.   TOOLS  Python · pandas · matplotlib.   Chart: Drew Cecala, 2026.",
         fontsize=8.8, color=MUTED, ha="left", va="top", linespacing=1.85)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "sports_owners_donation_concentration")
fig.savefig(f"{OUT}.png", dpi=200)
fig.savefig(f"{OUT}.svg")
print(f"\nwrote {OUT}.png / .svg")
