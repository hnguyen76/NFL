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
