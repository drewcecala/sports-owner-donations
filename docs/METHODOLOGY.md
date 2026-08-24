# Sources, tools & methodology

Charts live in `output/`, each built by a script in `scripts/`:

| Chart | Script |
|---|---|
| `sports_owners_donations_chart.png` / `.svg` | `build_chart.py` |
| `sports_owners_donations_reddit.png` (1200×1600 portrait) | `build_reddit.py` |
| `sports_owners_donation_concentration.png` / `.svg` | `build_concentration.py` |
| `sports_owners_political_donations.png` / `.svg` | `build_leagues_and_owners.py` |

The first three ask **how few people decide** which way sports-owner political
money leans. The fourth — the original graphic, documented in the appendix —
asks **which way** it leans.

Prepared 2026-08-20.

## Simple citation

> **Sources:** FiveThirtyEight's sports-owner political donations data (FEC
> records, 2016/2018/2020 cycles), pinned to its official source commit; and The Guardian's
> analysis of FEC filings for 4 Nov 2020 – 16 Oct 2024.
> **Tool:** Python (pandas + matplotlib).

One-liner:

> Sources: FiveThirtyEight sports-owner donations (FEC, 2016–20), pinned source; The Guardian analysis of FEC filings (2020–24) · Tool: Python (pandas, matplotlib)

## Sources

Two sources are used, and they are **deliberately kept visually and
editorially separate** because they are not the same kind of evidence.

### A. 2016 / 2018 / 2020 cycles — row-level, recomputed

- **FiveThirtyEight's official `sports-political-donations` dataset**, compiled
  from Federal Election Commission records for its October 2020 reporting and
  pinned to [commit `e0c8091`](https://github.com/fivethirtyeight/data/commit/e0c8091a3ba3be547b15a704b1ceb25b211e676b).
- The build requires SHA-256 `d6602d20049b8d36a1b455135bc4fc5900a2327dbe0f46d7633e2aad3222aca0`
  and validates the schema, 2,798 rows, 158 owners, 2016/2018/2020 cycles, and
  $46,978,697 total before analysis.
- **2,798 contributions** by **158 owners and commissioners** across MLB, NBA,
  NFL, NHL, WNBA and NASCAR, each tagged with the recipient committee's party
  lean as classified by FiveThirtyEight.
- Every figure on the chart from this period is **recomputed from the rows at
  build time** and printed to an audit table by the build script.

### B. 4 Nov 2020 – 16 Oct 2024 — published aggregates, transcribed

- **The Guardian**, analysis of FEC filings, published **5 November 2024**,
  covering federal contributions by principal owners / managing partners of
  MLB, NFL, NBA, NHL, MLS, NWSL and WNBA teams from 4 Nov 2020 through the
  16 Oct 2024 filing deadline. Read via syndication:
  https://onefootball.com/en/news/us-sports-owners-make-huge-political-donations-which-party-does-your-teams-give-to-40268249
- Published figures used: **at least $132.1M total**, **$124,806,435 (94.5%)** to Republican-leaning
  recipients, **$5,215,693 (3.9%)** to Democratic-leaning, ~2% bipartisan or
  unaffiliated; **Miriam Adelson $92,275,100**.
- **No row-level file is published.** Dollar figures are transcribed, while
  totals and “without Adelson” values derived from the rounded $132.1M
  denominator are approximate and labeled that way.
- Corroborating context (not used for the plotted figures):
  [OpenSecrets, Oct 2025](https://www.opensecrets.org/news/2025/10/blitzing-washington-how-the-nfl-and-team-owners-spend-millions-to-influence-government/) ·
  [Front Office Sports, 2024](https://frontofficesports.com/nfl-mlb-nba-owners-2024-election-trump-harris/)

## Tools

- **Python 3.12** — Python's standard library (pinned download and integrity
  checks), `pandas` (cleaning, aggregation, Lorenz construction),
  `matplotlib` (Agg backend; figure hand-laid
  in inch coordinates).
- Output: PNG at 200 dpi and SVG from one script, which prints an **audit
  table** of every number drawn on the chart.
- Palette checked with an OKLab-based colorblind validator: the
  red↔blue pair that carries the meaning clears the CVD separation floor
  (worst-pair ΔE 10.9 deutan / 11.5 tritan) and all three colors clear 3:1
  contrast on the chart surface. The neutral bucket deliberately fails the
  chroma floor — it is *supposed* to read as gray rather than compete as a
  third hue.

## Methodology

**Cleaning (source A).** Dollar strings (`"$4,000 "`) stripped to numbers.
Party labels folded into three buckets:

- **Republican (red):** "Republican" + "Bipartisan, but mostly Republican"
- **Democratic (blue):** "Democrat" + "Bipartisan, but mostly Democratic"
- **Neutral (gray):** "Bipartisan" + "Independent" + rows with no party listed

**Left panel — concentration curve.** Owners are sorted by total giving,
largest first, and plotted as cumulative share of dollars against cumulative
share of donors. The dashed 45° line is the reference case where every owner
gave an identical amount; the gap between curve and line is the concentration.
Marked points are the top 1, top 10 and top 20 donors.

Verified values: top 1 = **23.5%** of all dollars, top 10 = **57.4%**,
top 20 = **77.4%**. Median owner **$49,800**, mean **$297,334** — the gap
between those two is the same skew the curve draws.

**Right panel — the megadonor effect.** For each period, the party split is
computed twice: once across all owners, once with the single largest donor
removed. Bars are shares of that period's dollars, not absolute amounts;
absolute totals are printed to the right of each bar.

| Period | All owners | Minus top donor | Shift |
|---|---|---|---|
| 2016–20 | 73.5% R / 21.6% D | 65.3% R / 28.2% D | **−8.1 pts** |
| 2021–24 | 94.5% R / 3.9% D | ≈81.7% R / ≈13.1% D | **≈−12.8 pts** |

Removed donors: **Charles Johnson** (Giants, $11,035,700 = 23.5% of the
2016–20 total) and **Miriam Adelson** (Mavericks, $92,275,100 = ≈69.9% of the
2021–24 total).

**Plotted chart version** (`output/sports_owners_donations_chart.png` / `.svg`, built by
`scripts/build_chart.py`). The same data as a conventional
two-panel figure on shared row axes rather than a designed graphic: left panel
is the party composition stacked to 100% on a percentage axis; right panel is a
connected-dot (dumbbell) plot of the share going to Republican-leaning
recipients with all owners vs excluding that row's single largest donor.

Per-league megadonor effect (2016–20, recomputed from rows):

| League | %R all owners | %R excl. largest donor | Shift | Largest donor (share of league) |
|---|---|---|---|---|
| NASCAR | 80.3% | 78.5% | −1.8 | Roger Penske (58%) |
| NHL | 78.1% | 72.8% | −5.3 | Philip F. Anschutz (20%) |
| NFL | 76.1% | 70.3% | −5.8 | Jimmy and Susan Haslam (26%) |
| MLB | 70.2% | 39.3% | **−30.9** | Charles Johnson (51%) |
| NBA | 66.8% | 60.4% | −6.4 | Dan DeVos (16%) |
| WNBA | 45.7% | 24.2% | **−21.5** | Kelly Loeffler (28%) |

MLB is the extreme case: one donor supplies just over half of all MLB owner
money, and removing him flips the league from 70% Republican-leaning to 39%.

**League panel (Reddit cut only).** Within each league, dollars are shared out
by recipient party lean and drawn as a stacked bar against a 50% reference
line, sorted by Republican share. Computed from the 2016–20 row-level data —
the only source here with league-level detail. Owners holding teams in more
than one league (e.g. "NBA, WNBA") count toward **each** listed league, so
league dollar totals overlap; within-league shares are unaffected. Disclosed
on the chart.

| League | R | Bipartisan/other | D | Total | Owners |
|---|---|---|---|---|---|
| NASCAR | 80.3% | 6.8% | 12.9% | $0.7M | 12 |
| NHL | 78.1% | 2.8% | 19.1% | $9.1M | 31 |
| NFL | 76.1% | 10.7% | 13.2% | $6.6M | 41 |
| MLB | 70.2% | 5.9% | 23.9% | $21.7M | 49 |
| NBA | 66.8% | 6.8% | 26.4% | $14.2M | 42 |
| WNBA | 45.7% | 2.6% | 51.7% | $3.2M | 17 |

The WNBA is the only league whose owners gave more to Democratic-leaning than
Republican-leaning recipients.

**The point of the chart.** In both periods the headline partisan number is
driven heavily by one person. That is the finding — not a claim about how
sports owners as a group vote, donate, or believe. A topline built on a
distribution this skewed describes its largest contributor more than its
median one.

## Limitations

- **The two periods are not a continuous series.** Different compilers,
  different party-lean rules, different date ranges, and different sets of
  leagues (the Guardian window includes MLS and NWSL; the FiveThirtyEight set
  includes NASCAR). They are shown as two separate snapshots and should be
  read that way.
- **Source B is not independently verified at row level.** The Guardian's
  aggregates are transcribed as published. The Guardian itself notes its
  totals are "presumed to be a fraction of the actual contributions."
- **Source B calculations are approximate.** The published total is “at least
  $132.1M”; derived shares, the amount attributed to all other owners, and the
  counterfactual without Adelson use that rounded lower-bound denominator.
- **"Minus Adelson" assumes her giving is ~entirely Republican-leaning.** This
  is consistent with the reporting but is an assumption, not a computed split,
  and is disclosed on the chart.
- **Federal contributions only** — no state or local giving, and no
  undisclosed spending. Dark-money channels are by definition absent.
- **Party lean is the recipient committee's, not the donor's.** A contribution
  is classified by who received it.
- Owners who hold teams in multiple leagues appear once at the owner level;
  no league-level breakdown is drawn on this chart, so no double-counting
  applies here.
- Percentages are rounded for display; the audit output carries full precision.

---

# Appendix — the original league / top-owner graphic

Chart: `output/sports_owners_political_donations.png` / `.svg`
Build script: `scripts/build_leagues_and_owners.py` · Prepared 2026-08-18.

Same source, cleaning and party buckets as above. What differs is the layout,
plus two details specific to this chart.

**Neutral bucket, in detail.**

- **Neutral (gray):** "Bipartisan" + "Independent" + rows with **no party
  listed** — 9 rows totaling **$848,950**, most of it Jerry Reinsdorf's $800K
  to three PACs (Govern or Go Home; United Together; United for Progress),
  plus e.g. Laura Ricketts' $2,700 to Jill Stein. Footnoted on the chart.

**Headline figures.** Total **$46,978,697** — Republican bucket $34,517,109
(73.5%), Democratic $10,124,439 (21.6%), neutral/unlisted $2,337,149 (5.0%).

**League panel.** Within each league, dollars are shared out by recipient
party lean and drawn as a diverging bar centered on the 50/50 midline, sorted
by Republican share (NASCAR 80% R → WNBA, the only league whose ownership gave
a majority to Democrats: 51.7% D vs 45.7% R). Owners who hold teams in more
than one league (e.g. "NBA, WNBA") count toward **each** listed league — league
rows therefore double-count such owners across leagues (disclosed on the
chart); within-league shares are unaffected.

**Owner panel.** The twelve biggest donors by combined 2016–2020 giving, drawn
as stacked R / neutral / D bars with totals at the tip. Charles Johnson
(Giants) alone gave $11.04M — about 23.5% of every dollar in the data.
Couples listed jointly in FEC records (e.g. "Jimmy and Susan Haslam") are one
entry; league commissioners are included as compiled by FiveThirtyEight.

**Additional limitation.** The 2020 cycle reflects the dataset's fall-2020
compilation date, so late-2020 contributions are not included. All other
limitations listed above apply here too.
