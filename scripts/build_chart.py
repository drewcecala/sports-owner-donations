"""Sports-owner political donations — plotted as a chart, not an infographic.

Two panels sharing one row axis (leagues, plus period totals):

  Left   composition — share of each league's dollars by recipient party lean,
         stacked to 100% on a real percentage axis.
  Right  megadonor effect — % going to Republican-leaning recipients with all
         owners (filled dot) vs excluding that league's single largest donor
         (open dot), connected. Shows how much of each league's lean rests on
         one person.

Sources: FiveThirtyEight `sports-political-donations` (FEC, 2016/2018/2020),
pinned to its official source commit and recomputed at build time; The Guardian's analysis of FEC
filings for 4 Nov 2020 - 16 Oct 2024, published aggregates (2021-24 row only).

Outputs output/sports_owners_donations_chart.png / .svg
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
SURFACE = "#ffffff"
PAGE = "#fbfaf7"
INK = "#14150f"
INK2 = "#4a4b42"
MUTED = "#83817a"
GRID = "#e0dcd2"
AXIS = "#b9b5aa"
R_COL = "#c1352f"
D_COL = "#2a78d6"
N_COL = "#a8a69c"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "text.color": INK,
    "figure.facecolor": PAGE,
    "savefig.facecolor": PAGE,
    "axes.facecolor": SURFACE,
})

# ------------------------------------------------------------------ data ---
df = load_fivethirtyeight_dataframe()
BUCKET = {"Republican": "R", "Bipartisan, but mostly Republican": "R",
          "Democrat": "D", "Bipartisan, but mostly Democratic": "D",
          "Bipartisan": "N", "Independent": "N"}
df["b"] = df["BUCKET"] = df["Party"].map(BUCKET).fillna("N")


def comp(frame):
    t = frame.amt.sum()
    g = frame.groupby("b").amt.sum()
    return t, 100 * g.get("R", 0) / t, 100 * g.get("N", 0) / t, 100 * g.get("D", 0) / t


rows = []
for lg in ["NASCAR", "NHL", "NFL", "MLB", "NBA", "WNBA"]:
    sub = df[df["League"].str.contains(lg)]
    t, r, n, d = comp(sub)
    by_owner = sub.groupby("Owner").amt.sum()
    top, top_amt = by_owner.idxmax(), by_owner.max()
    _, r2, _, _ = comp(sub[sub.Owner != top])
    rows.append(dict(label=lg, total=t, R=r, N=n, D=d, R_ex=r2,
                     top=top, top_share=100 * top_amt / t, kind="league"))
rows.sort(key=lambda x: -x["R"])

# period totals
t, r, n, d = comp(df)
by_owner = df.groupby("Owner").amt.sum()
TOP_ALL, TOP_AMT = by_owner.idxmax(), by_owner.max()
_, r2, _, _ = comp(df[df.Owner != TOP_ALL])
rows.append(dict(label="All owners, 2016–20", total=t, R=r, N=n, D=d, R_ex=r2,
                 top=TOP_ALL, top_share=100 * TOP_AMT / t, kind="total"))

G_R, G_D, G_ADELSON = GUARDIAN_REPUBLICAN, GUARDIAN_DEMOCRATIC, GUARDIAN_ADELSON
G_TOT = GUARDIAN_TOTAL_APPROX
G_N = G_TOT - G_R - G_D
rows.append(dict(label="2021–24 (approx.)", total=G_TOT,
                 R=100 * G_R / G_TOT, N=100 * G_N / G_TOT, D=100 * G_D / G_TOT,
                 R_ex=100 * (G_R - G_ADELSON) / (G_TOT - G_ADELSON),
                 top="Miriam Adelson", top_share=100 * G_ADELSON / G_TOT,
                 kind="total"))

print(f"{'row':22s} {'$M':>7s} {'%R':>6s} {'%N':>6s} {'%D':>6s} {'%R excl':>8s} {'shift':>7s}  top donor")
for r_ in rows:
    print("%-22s %7.1f %6.1f %6.1f %6.1f %8.1f %+7.1f  %s (%.0f%% of row)"
          % (r_["label"], r_["total"] / 1e6, r_["R"], r_["N"], r_["D"],
             r_["R_ex"], r_["R_ex"] - r_["R"], r_["top"], r_["top_share"]))

# ------------------------------------------------------------------ plot ---
FW, FH = 13.0, 8.4
fig = plt.figure(figsize=(FW, FH))

# y positions: leagues stacked, gap, then the two totals
ypos, y = [], 0.0
for i, r_ in enumerate(rows):
    if i > 0 and rows[i]["kind"] != rows[i - 1]["kind"]:
        y -= 0.85                                  # visual gap before totals
    ypos.append(y)
    y -= 1.0
Y_LO, Y_HI = y + 0.45, 0.75

axA = fig.add_axes([1.85 / FW, 2.10 / FH, 4.85 / FW, 4.55 / FH])
axB = fig.add_axes([8.05 / FW, 2.10 / FH, 4.05 / FW, 4.55 / FH])

# ------------------------------------------------- panel A: composition ----
for r_, yy in zip(rows, ypos):
    left = 0.0
    for val, col in ((r_["R"], R_COL), (r_["N"], N_COL), (r_["D"], D_COL)):
        axA.barh(yy, val, left=left, height=0.62, color=col,
                 edgecolor=SURFACE, linewidth=1.2, zorder=3)
        left += val
    axA.text(101.5, yy, f"${r_['total']/1e6:,.1f}M", fontsize=9.5,
             ha="left", va="center", color=MUTED)

axA.axvline(50, color=INK, lw=1.2, ls=(0, (3, 3)), zorder=5)
axA.set_xlim(0, 100)
axA.set_ylim(Y_LO, Y_HI)
axA.set_yticks(ypos)
axA.set_yticklabels([r_["label"] for r_ in rows], fontsize=11.5)
for lbl, r_ in zip(axA.get_yticklabels(), rows):
    lbl.set_fontweight("bold" if r_["kind"] == "league" else "normal")
    lbl.set_color(INK if r_["kind"] == "league" else INK2)
axA.set_xticks(range(0, 101, 20))
axA.set_xticklabels([f"{v}%" for v in range(0, 101, 20)], fontsize=10)
axA.tick_params(axis="both", length=0, colors=MUTED)
axA.set_xlabel("share of donations, by recipient party lean", fontsize=11, color=INK2, labelpad=9)
axA.xaxis.grid(True, color=GRID, lw=0.9, zorder=0)
axA.set_axisbelow(True)
for s in axA.spines.values():
    s.set_visible(False)
axA.spines["bottom"].set_visible(True)
axA.spines["bottom"].set_color(AXIS)
axA.set_title("Where the money went", fontsize=13.5, fontweight="bold",
              color=INK, loc="left", pad=12)

# --------------------------------------------- panel B: megadonor effect ---
for r_, yy in zip(rows, ypos):
    axB.plot([r_["R_ex"], r_["R"]], [yy, yy], lw=2.0, color="#e0b8b5",
             solid_capstyle="round", zorder=3)
    axB.plot([r_["R_ex"]], [yy], "o", ms=9, mfc=SURFACE, mec=R_COL, mew=2.0, zorder=5)
    axB.plot([r_["R"]], [yy], "o", ms=9.5, mfc=R_COL, mec=R_COL, zorder=5)
    shift = r_["R"] - r_["R_ex"]
    axB.text(101.5, yy, f"−{shift:.0f}", fontsize=9.5, ha="left", va="center",
             color=INK if shift >= 15 else MUTED,
             fontweight="bold" if shift >= 15 else "normal")

axB.axvline(50, color=INK, lw=1.2, ls=(0, (3, 3)), zorder=2)
axB.set_xlim(18, 100)
axB.set_ylim(Y_LO, Y_HI)
axB.set_yticks(ypos)
axB.set_yticklabels([])
axB.set_xticks(range(20, 101, 20))
axB.set_xticklabels([f"{v}%" for v in range(20, 101, 20)], fontsize=10)
axB.tick_params(axis="both", length=0, colors=MUTED)
axB.set_xlabel("share going to Republican-leaning recipients", fontsize=11,
               color=INK2, labelpad=9)
axB.xaxis.grid(True, color=GRID, lw=0.9, zorder=0)
axB.set_axisbelow(True)
for s in axB.spines.values():
    s.set_visible(False)
axB.spines["bottom"].set_visible(True)
axB.spines["bottom"].set_color(AXIS)
axB.set_title("How much of that rests on one donor", fontsize=13.5,
              fontweight="bold", color=INK, loc="left", pad=12)
fig.text((8.05 + 4.05 + 0.12) / FW, (2.10 + 4.55 + 0.30) / FH, "shift",
         fontsize=9.5, color=MUTED, ha="left", va="bottom")

# ------------------------------------------------------ titles & legend ----
fig.text(1.85 / FW, 0.958, "Political giving by U.S. pro-sports team owners",
         fontsize=19, fontweight="bold", ha="left", va="top", color=INK)
fig.text(1.85 / FW, 0.917,
         "Federal contributions by league. Right panel removes each row's single largest donor to show how "
         "concentrated the giving is.",
         fontsize=11.5, ha="left", va="top", color=INK2)

comp_handles = [
    Line2D([], [], marker="s", ls="", ms=11, mfc=R_COL, mec=R_COL, label="Republican-leaning"),
    Line2D([], [], marker="s", ls="", ms=11, mfc=N_COL, mec=N_COL, label="bipartisan / other"),
    Line2D([], [], marker="s", ls="", ms=11, mfc=D_COL, mec=D_COL, label="Democratic-leaning"),
]
dot_handles = [
    Line2D([], [], marker="o", ls="", ms=9.5, mfc=R_COL, mec=R_COL, label="all owners"),
    Line2D([], [], marker="o", ls="", ms=9, mfc=SURFACE, mec=R_COL, mew=2.0,
           label="excluding that row's largest donor"),
]
fig.legend(handles=comp_handles, loc="lower left", bbox_to_anchor=(1.85 / FW, 1.28 / FH),
           frameon=False, fontsize=10.5, ncol=3, handletextpad=0.5, columnspacing=2.0)
fig.legend(handles=dot_handles, loc="lower left", bbox_to_anchor=(8.05 / FW, 1.28 / FH),
           frameon=False, fontsize=10.5, ncol=2, handletextpad=0.5, columnspacing=2.0)

fig.text(1.85 / FW, 1.02 / FH,
         "Leagues and the 2016–20 row: FiveThirtyEight “sports-political-donations” (FEC records), pinned to source commit e0c8091 — 2,798 contributions by 158 owners and commissioners.\n"
         "2021–24 row: The Guardian’s FEC analysis, published 5 Nov 2024, covering 4 Nov 2020 – 16 Oct 2024. The reported total is at least $132.1M, so derived values are approximate.\n"
         "“Without” assumes Miriam Adelson’s giving is ~entirely Republican-leaning. Party lean is the recipient committee’s, not the donor’s. Federal contributions only.\n"
         "Multi-league owners count toward each league, so league totals overlap.\n"
         "The periods are separate snapshots, not a continuous series.   Python (pandas, matplotlib) · Drew Cecala, 2026",
         fontsize=8.3, color=MUTED, ha="left", va="top", linespacing=1.7)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "sports_owners_donations_chart")
fig.savefig(f"{OUT}.png", dpi=170)
fig.savefig(f"{OUT}.svg")
print(f"\nwrote {OUT}.png / .svg")
