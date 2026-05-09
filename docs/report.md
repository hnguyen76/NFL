# NFL Betting History Report

## Executive Summary

This report analyzes NFL game history from 1999 through 2025 using nflverse
game-level data. The focus is not to produce blind picks, but to identify
repeatable historical filters that can become a disciplined wager checklist.

The headline result is simple: broad market betting is negative after vig.
Favorites, home teams, overs, and even broad underdogs all fail to clear the
roughly 52.38% break-even threshold required at -110 odds. The dashboard is
therefore designed as an intelligence layer: it highlights context, price, and
risk rather than pretending that one universal angle can beat the market.

## Dataset

- Source: nflverse/nfldata `games.csv`, `teamcolors.csv`, and `logos.csv`
- Seasons covered: 1999-2025
- Total scored games analyzed: 7,276
- Regular season games used for baseline market analysis: 6,967
- Markets: against the spread, favorite/underdog ATS, home/away ATS, over/under

## Baseline Markets

| Market | Record | Win % | ROI |
| --- | ---: | ---: | ---: |
| Home ATS | 3319-3459-189 | 49.0% | -6.3% |
| Away ATS | 3459-3319-189 | 51.0% | -2.5% |
| Favorite ATS | 3298-3450-189 | 48.9% | -6.5% |
| Underdog ATS | 3450-3298-189 | 51.1% | -2.3% |
| Over | 3399-3469-99 | 49.5% | -5.4% |
| Under | 3469-3399-99 | 50.5% | -3.5% |

Underdogs and unders perform better than favorites and overs, but neither broad
side is profitable after standard -110 pricing. A useful wager framework needs
more context than side selection.

## Recent Season Read: 2020-2025

Single-season samples are noisier than the full 1999-2025 history, but they are
useful for reading how the market has recently shifted. The table below uses
regular season games only.

| Season | Games | Best broad market | ROI | Worst broad market | ROI | Practical read |
| --- | ---: | --- | ---: | --- | ---: | --- |
| 2020 | 256 | Underdog ATS | +5.9% | Favorite ATS | -15.0% | Dog season; favorite tax was punished. |
| 2021 | 272 | Under | +2.9% | Over | -11.9% | Unders improved, especially in wind. |
| 2022 | 271 | Under | +6.1% | Over | -15.1% | Strong under year; division unders and wind unders led. |
| 2023 | 272 | Under | +3.2% | Over | -12.2% | Under stayed playable, but favorites beat dogs ATS. |
| 2024 | 272 | Over | +2.9% | Under | -11.9% | Market flipped; blind under betting was punished. |
| 2025 | 272 | Over | -0.3% | Under | -8.8% | No broad edge; over was merely least bad after vig. |

### 2020

- Baseline: Underdog ATS went 142-114-0 for a +5.9% ROI, while Favorite ATS
  went 114-142-0 for a -15.0% ROI.
- Best filters: Division underdogs went 55-41-0 for +9.4% ROI; controlled-roof
  overs went 51-38-2 for +9.2% ROI.
- Traps: High-total unders and division-game unders both lost badly.
- Advice: In a similar market environment, look for inflated favorites and key
  underdog numbers such as +3.5, +7.5, and +10.5. Do not blindly pair "division"
  with "under"; 2020 punished that story.

### 2021

- Baseline: Under went 145-124-3 for +2.9% ROI; Over fell to -11.9% ROI.
- Best filters: Wind 10+ mph unders went 46-27-1 for +20.0% ROI; wind 15+ mph
  unders went 21-8-0 for +38.2% ROI.
- Traps: Double-digit underdogs went 21-29-3 for -18.7% ROI.
- Advice: Weather was the cleanest edge. Prioritize wind-confirmed unders, but
  avoid treating every big dog as a backdoor-cover candidate.

### 2022

- Baseline: Under went 149-119-3 for +6.1% ROI; Underdog ATS also held up at
  +4.4% ROI.
- Best filters: Division unders went 55-38-3 for +12.5% ROI; wind 10+ mph
  unders went 25-13-0 for +25.6% ROI.
- Traps: High-total overs and big home favorites were both negative.
- Advice: This was the best recent season for disciplined under betting. The
  strongest version was not "low total under"; it was under plus context:
  division familiarity, wind, or market total that had not already collapsed.

### 2023

- Baseline: Under stayed positive at +3.2% ROI, but Favorite ATS beat Underdog
  ATS (+1.3% vs -9.9%).
- Best filters: Wind 10+ mph unders went 34-16-1 for +29.2% ROI; high-total
  unders went 24-12-0 for +27.3% ROI.
- Traps: High-total overs went 12-24-0 for -36.4% ROI.
- Advice: Keep the under/weather tool, but do not automatically fade favorites.
  This season rewarded selective favorite backing and punished chasing overs in
  already expensive totals.

### 2024

- Baseline: The market flipped. Over went 145-124-3 for +2.9% ROI, while Under
  dropped to -11.9% ROI.
- Best filters: Division underdogs went 53-41-2 for +7.5% ROI.
- Traps: Division-game unders went 40-56-0 for -20.5% ROI; road dogs +3.5 or
  more were also negative.
- Advice: Do not let old under bias override current scoring conditions. If the
  market has adjusted too far toward unders, the better wager may be pass or
  selective over rather than fighting the tape.

### 2025

- Baseline: No broad market cleared the -110 hurdle. Over was closest at -0.3%
  ROI, while Under lost -8.8% ROI.
- Best filters: High-total overs went 35-28-0 for +6.1% ROI; home favorites -7
  or more went 31-25-0 for +5.7% ROI.
- Traps: High-total unders went 28-35-0 for -15.2% ROI; double-digit dogs went
  13-21-0 for -27.0% ROI.
- Advice: Treat 2025 as a price-discipline season. Broad angles were weak.
  Prefer fewer bets, wait for stale numbers, and avoid forcing contrarian
  underdog or under narratives without a clear line advantage.

## Strongest Historical Signals

| Pattern | Market | Record | Win % | ROI | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| Wind 15+ mph unders | Total | 361-281-7 | 56.2% | +7.3% | Best blend of sample and edge. |
| Wind 10+ mph unders | Total | 969-801-23 | 54.8% | +4.5% | Larger sample, still positive after vig. |

Weather, especially wind, is the most actionable historical cluster in this
build. The signal is strongest when wind is treated as a constraint on passing,
deep-ball efficiency, kicking, and pace. The current line must still matter:
if the market has already adjusted the total down aggressively, the edge can
disappear.

## Trap Patterns

| Pattern | Market | Bets | Win % | ROI |
| --- | --- | ---: | ---: | ---: |
| Freezing outdoor unders | Total | 305 | 46.7% | -10.7% |
| High totals >=48 over | Total | 1,274 | 48.3% | -7.8% |
| Teams with 3+ days rest disadvantage | ATS | 1,320 | 49.1% | -6.0% |
| Home favorites -7 or more | ATS | 1,585 | 49.5% | -5.3% |
| Low totals <=39.5 under | Total | 1,581 | 49.8% | -4.8% |

Several narratives that sound intuitive are not enough after vig. Cold alone is
not the same as wind. High-total games are often already priced for offense.
Large home favorites carry favorite tax and late-game cover risk.

## Wager Framework

Use the dashboard as a filter stack:

1. Start with market context: spread size, total bucket, venue, weather, rest,
   division matchup, and team profile.
2. Require sample discipline: 250+ historical bets for a broad angle, or a clear
   football reason for a smaller sample.
3. Demand ROI after vig, not only a win rate over 50%.
4. Confirm the current matchup still matches the historical condition.
5. Track closing-line value. A good historical angle with a bad current number is
   usually a pass.
6. Cap stake size. Historical edges can regress quickly when books adjust.

## Formula Reference

- Home ATS margin = `result - spread_line`
- Away ATS margin = `-(result - spread_line)`
- Over margin = `total - total_line`
- Under margin = `-(total - total_line)`
- Win profit at -110 = `100 / 110 = 0.9091 units`
- ROI = `(wins * 0.9091 - losses) / total_bets`

Pushes are counted as bets with zero profit. Win percentage excludes pushes.

## Caveats

This is a historical research dashboard, not predictive certainty. NFL markets
change, rules change, scoring environments change, and sportsbook lines adapt.
Use these patterns to decide what deserves investigation, not as automatic
wagers.
