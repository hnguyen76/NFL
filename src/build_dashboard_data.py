from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_PATH = DATA_DIR / "dashboard_data.js"

WIN_UNITS_AT_MINUS_110 = 100 / 110


TEAM_OVERRIDES = {
    "ARI": ("Arizona Cardinals", "Cardinals", "NFC", "NFC West"),
    "ATL": ("Atlanta Falcons", "Falcons", "NFC", "NFC South"),
    "BAL": ("Baltimore Ravens", "Ravens", "AFC", "AFC North"),
    "BUF": ("Buffalo Bills", "Bills", "AFC", "AFC East"),
    "CAR": ("Carolina Panthers", "Panthers", "NFC", "NFC South"),
    "CHI": ("Chicago Bears", "Bears", "NFC", "NFC North"),
    "CIN": ("Cincinnati Bengals", "Bengals", "AFC", "AFC North"),
    "CLE": ("Cleveland Browns", "Browns", "AFC", "AFC North"),
    "DAL": ("Dallas Cowboys", "Cowboys", "NFC", "NFC East"),
    "DEN": ("Denver Broncos", "Broncos", "AFC", "AFC West"),
    "DET": ("Detroit Lions", "Lions", "NFC", "NFC North"),
    "GB": ("Green Bay Packers", "Packers", "NFC", "NFC North"),
    "HOU": ("Houston Texans", "Texans", "AFC", "AFC South"),
    "IND": ("Indianapolis Colts", "Colts", "AFC", "AFC South"),
    "JAX": ("Jacksonville Jaguars", "Jaguars", "AFC", "AFC South"),
    "KC": ("Kansas City Chiefs", "Chiefs", "AFC", "AFC West"),
    "LA": ("Los Angeles Rams", "Rams", "NFC", "NFC West"),
    "LAR": ("Los Angeles Rams", "Rams", "NFC", "NFC West"),
    "LAC": ("Los Angeles Chargers", "Chargers", "AFC", "AFC West"),
    "LV": ("Las Vegas Raiders", "Raiders", "AFC", "AFC West"),
    "MIA": ("Miami Dolphins", "Dolphins", "AFC", "AFC East"),
    "MIN": ("Minnesota Vikings", "Vikings", "NFC", "NFC North"),
    "NE": ("New England Patriots", "Patriots", "AFC", "AFC East"),
    "NO": ("New Orleans Saints", "Saints", "NFC", "NFC South"),
    "NYG": ("New York Giants", "Giants", "NFC", "NFC East"),
    "NYJ": ("New York Jets", "Jets", "AFC", "AFC East"),
    "PHI": ("Philadelphia Eagles", "Eagles", "NFC", "NFC East"),
    "PIT": ("Pittsburgh Steelers", "Steelers", "AFC", "AFC North"),
    "SEA": ("Seattle Seahawks", "Seahawks", "NFC", "NFC West"),
    "SF": ("San Francisco 49ers", "49ers", "NFC", "NFC West"),
    "TB": ("Tampa Bay Buccaneers", "Buccaneers", "NFC", "NFC South"),
    "TEN": ("Tennessee Titans", "Titans", "AFC", "AFC South"),
    "WAS": ("Washington Commanders", "Commanders", "NFC", "NFC East"),
    "OAK": ("Oakland Raiders", "Raiders", "AFC", "AFC West"),
    "SD": ("San Diego Chargers", "Chargers", "AFC", "AFC West"),
    "STL": ("St. Louis Rams", "Rams", "NFC", "NFC West"),
}


def parse_float(value: str | None) -> float | None:
    if value is None or value == "" or value.upper() == "NA":
        return None
    return float(value)


def parse_int(value: str | None) -> int | None:
    parsed = parse_float(value)
    return None if parsed is None else int(parsed)


def outcome(value: float, tolerance: float = 1e-9) -> int:
    if value > tolerance:
        return 1
    if value < -tolerance:
        return -1
    return 0


def pct(numerator: float, denominator: float) -> float | None:
    if not denominator:
        return None
    return numerator / denominator


def summarize(outcomes: Iterable[int]) -> dict:
    values = list(outcomes)
    wins = sum(1 for item in values if item > 0)
    losses = sum(1 for item in values if item < 0)
    pushes = sum(1 for item in values if item == 0)
    bets = wins + losses + pushes
    decisions = wins + losses
    profit_units = (wins * WIN_UNITS_AT_MINUS_110) - losses
    return {
        "bets": bets,
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "win_pct": pct(wins, decisions),
        "push_pct": pct(pushes, bets),
        "roi": pct(profit_units, bets),
        "profit_units": profit_units,
        "break_even_win_pct": 110 / 210,
    }


def rounded_summary(outcomes: Iterable[int]) -> dict:
    summary = summarize(outcomes)
    for key in ("win_pct", "push_pct", "roi", "profit_units", "break_even_win_pct"):
        if summary[key] is not None:
            summary[key] = round(summary[key], 4)
    return summary


def load_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_team_meta() -> dict[str, dict]:
    meta: dict[str, dict] = {}

    teams_path = BASE_DIR / "nfl_teams.csv"
    if teams_path.exists():
        for row in load_csv(teams_path):
            team_id = row.get("team_id", "")
            if not team_id or team_id in meta:
                continue
            meta[team_id] = {
                "name": row.get("team_name", team_id),
                "short": row.get("team_name_short", team_id),
                "conference": row.get("team_conference", ""),
                "division": row.get("team_division", ""),
            }

    for team, values in TEAM_OVERRIDES.items():
        name, short, conference, division = values
        meta[team] = {
            "name": name,
            "short": short,
            "conference": conference,
            "division": division,
        }

    colors = {}
    colors_path = DATA_DIR / "teamcolors.csv"
    if colors_path.exists():
        for row in load_csv(colors_path):
            colors[row["team"]] = {
                "color": row.get("color") or "#151515",
                "color2": row.get("color2") or "#d5a642",
            }

    logos = {}
    logos_path = DATA_DIR / "logos.csv"
    if logos_path.exists():
        for row in load_csv(logos_path):
            logos[row["team"]] = row.get("team_logo", "")

    for team in set(meta) | set(colors) | set(logos):
        meta.setdefault(
            team,
            {"name": team, "short": team, "conference": "", "division": ""},
        )
        meta[team]["color"] = colors.get(team, {}).get("color", "#151515")
        meta[team]["color2"] = colors.get(team, {}).get("color2", "#d5a642")
        meta[team]["logo"] = logos.get(team, "")

    return meta


def spread_bucket(abs_spread: float) -> str:
    if abs_spread < 0.5:
        return "Pick'em"
    if abs_spread <= 2.5:
        return "Short 0.5-2.5"
    if abs_spread <= 3.5:
        return "Key 3-3.5"
    if abs_spread <= 6.5:
        return "Medium 4-6.5"
    if abs_spread <= 9.5:
        return "Large 7-9.5"
    return "Double digit"


def total_bucket(total_line: float) -> str:
    if total_line <= 39.5:
        return "Low <=39.5"
    if total_line <= 43.5:
        return "Lower mid 40-43.5"
    if total_line <= 47.5:
        return "Upper mid 44-47.5"
    return "High >=48"


def weather_bucket(game: dict) -> str:
    roof = game["roof"]
    wind = game["wind"]
    temp = game["temp"]
    if roof in {"dome", "closed"}:
        return "Controlled roof"
    if wind is not None and wind >= 15:
        return "Outdoor wind 15+"
    if wind is not None and wind >= 10:
        return "Outdoor wind 10-14"
    if temp is not None and temp <= 32:
        return "Outdoor freezing"
    return "Outdoor mild"


def game_market_outcome(game: dict, market: str) -> int | None:
    ats_margin = game["home_ats_margin"]
    total_margin = game["total_margin"]
    spread = game["spread_line"]
    if market == "Home ATS":
        return outcome(ats_margin)
    if market == "Away ATS":
        return outcome(-ats_margin)
    if market == "Favorite ATS":
        if abs(spread) < 0.5:
            return None
        return outcome(ats_margin if spread > 0 else -ats_margin)
    if market == "Underdog ATS":
        if abs(spread) < 0.5:
            return None
        return outcome(-ats_margin if spread > 0 else ats_margin)
    if market == "Over":
        return outcome(total_margin)
    if market == "Under":
        return outcome(-total_margin)
    raise ValueError(f"Unknown market: {market}")


def summarize_games(games: Iterable[dict], market: str) -> dict:
    values = [game_market_outcome(game, market) for game in games]
    return rounded_summary(item for item in values if item is not None)


def summarize_team_records(records: Iterable[dict]) -> dict:
    return rounded_summary(record["ats_outcome"] for record in records)


def confidence_label(summary: dict) -> str:
    bets = summary["bets"]
    roi = abs(summary["roi"] or 0)
    if bets >= 500 and roi >= 0.015:
        return "High sample"
    if bets >= 250 and roi >= 0.01:
        return "Medium sample"
    if bets >= 100:
        return "Watch only"
    return "Small sample"


def edge_score(summary: dict) -> float:
    sample_factor = min(summary["bets"], 700) / 700
    return round((summary["roi"] or 0) * 100 * sample_factor, 2)


def build_games() -> tuple[list[dict], list[dict]]:
    games = []
    team_records = []

    for row in load_csv(DATA_DIR / "games.csv"):
        result = parse_float(row.get("result"))
        total = parse_float(row.get("total"))
        spread = parse_float(row.get("spread_line"))
        total_line = parse_float(row.get("total_line"))
        if result is None or total is None or spread is None or total_line is None:
            continue

        season = parse_int(row.get("season"))
        week = parse_int(row.get("week"))
        if season is None or week is None:
            continue

        away_rest = parse_int(row.get("away_rest"))
        home_rest = parse_int(row.get("home_rest"))
        temp = parse_float(row.get("temp"))
        wind = parse_float(row.get("wind"))
        roof = (row.get("roof") or "unknown").lower()
        div_game = row.get("div_game") == "1"
        abs_spread = abs(spread)
        home_ats_margin = result - spread
        total_margin = total - total_line

        game = {
            "game_id": row["game_id"],
            "season": season,
            "week": week,
            "game_type": row.get("game_type", ""),
            "weekday": row.get("weekday", ""),
            "gameday": row.get("gameday", ""),
            "away_team": row.get("away_team", ""),
            "home_team": row.get("home_team", ""),
            "away_score": parse_int(row.get("away_score")),
            "home_score": parse_int(row.get("home_score")),
            "location": row.get("location", ""),
            "result": result,
            "total": total,
            "spread_line": spread,
            "total_line": total_line,
            "abs_spread": abs_spread,
            "spread_bucket": spread_bucket(abs_spread),
            "total_bucket": total_bucket(total_line),
            "home_ats_margin": home_ats_margin,
            "total_margin": total_margin,
            "div_game": div_game,
            "roof": roof,
            "surface": row.get("surface", ""),
            "temp": temp,
            "wind": wind,
            "weather_bucket": "",
            "away_rest": away_rest,
            "home_rest": home_rest,
            "rest_diff_home": (
                home_rest - away_rest
                if home_rest is not None and away_rest is not None
                else None
            ),
        }
        game["weather_bucket"] = weather_bucket(game)
        games.append(game)

        for is_home in (True, False):
            team = game["home_team"] if is_home else game["away_team"]
            opponent = game["away_team"] if is_home else game["home_team"]
            team_ats_margin = home_ats_margin if is_home else -home_ats_margin
            if abs_spread < 0.5:
                role = "Pick"
            elif (is_home and spread > 0) or ((not is_home) and spread < 0):
                role = "Favorite"
            else:
                role = "Underdog"

            rest_advantage = None
            if home_rest is not None and away_rest is not None:
                rest_advantage = (home_rest - away_rest) if is_home else (away_rest - home_rest)

            team_records.append(
                {
                    "team": team,
                    "opponent": opponent,
                    "season": season,
                    "week": week,
                    "game_type": game["game_type"],
                    "is_home": is_home,
                    "role": role,
                    "spread_abs": abs_spread,
                    "spread_bucket": game["spread_bucket"],
                    "total_bucket": game["total_bucket"],
                    "div_game": div_game,
                    "weather_bucket": game["weather_bucket"],
                    "rest_advantage": rest_advantage,
                    "ats_outcome": outcome(team_ats_margin),
                    "over_outcome": outcome(total_margin),
                }
            )

    return games, team_records


def group_market(games: list[dict], group_key: str, market: str) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for game in games:
        grouped[str(game[group_key])].append(game)

    rows = []
    for key, group in grouped.items():
        summary = summarize_games(group, market)
        rows.append({"group": key, **summary})

    def sort_key(row: dict) -> tuple:
        try:
            return (0, int(row["group"]))
        except ValueError:
            return (1, row["group"])

    return sorted(rows, key=sort_key)


def pattern(
    name: str,
    market: str,
    category: str,
    thesis: str,
    records: Iterable[dict],
    outcome_getter: Callable[[dict], int],
) -> dict:
    selected = list(records)
    summary = rounded_summary(outcome_getter(record) for record in selected)
    return {
        "name": name,
        "market": market,
        "category": category,
        "thesis": thesis,
        "confidence": confidence_label(summary),
        "edge_score": edge_score(summary),
        **summary,
    }


def build_patterns(games: list[dict], team_records: list[dict]) -> list[dict]:
    regular_games = [game for game in games if game["game_type"] == "REG"]
    outdoor_games = [game for game in regular_games if game["roof"] not in {"dome", "closed"}]

    patterns = [
        pattern(
            "Road underdogs +3.5 or more",
            "ATS",
            "Spread",
            "Tests whether market shade toward home favorites creates value on road dogs.",
            (
                record
                for record in team_records
                if record["game_type"] == "REG"
                and not record["is_home"]
                and record["role"] == "Underdog"
                and record["spread_abs"] >= 3.5
            ),
            lambda record: record["ats_outcome"],
        ),
        pattern(
            "Double-digit underdogs",
            "ATS",
            "Spread",
            "Large NFL spreads can invite backdoor-cover risk late in games.",
            (
                record
                for record in team_records
                if record["game_type"] == "REG"
                and record["role"] == "Underdog"
                and record["spread_abs"] >= 10
            ),
            lambda record: record["ats_outcome"],
        ),
        pattern(
            "Home favorites -7 or more",
            "ATS",
            "Spread",
            "Measures whether expensive home chalk covers often enough at -110.",
            (
                record
                for record in team_records
                if record["game_type"] == "REG"
                and record["is_home"]
                and record["role"] == "Favorite"
                and record["spread_abs"] >= 7
            ),
            lambda record: record["ats_outcome"],
        ),
        pattern(
            "Division underdogs",
            "ATS",
            "Division",
            "Familiar opponents can compress margins and support underdog covers.",
            (
                record
                for record in team_records
                if record["game_type"] == "REG"
                and record["role"] == "Underdog"
                and record["div_game"]
            ),
            lambda record: record["ats_outcome"],
        ),
        pattern(
            "Teams with 3+ days rest edge",
            "ATS",
            "Rest",
            "Rest advantages matter most when the schedule creates real prep separation.",
            (
                record
                for record in team_records
                if record["game_type"] == "REG"
                and record["rest_advantage"] is not None
                and record["rest_advantage"] >= 3
            ),
            lambda record: record["ats_outcome"],
        ),
        pattern(
            "Teams with 3+ days rest disadvantage",
            "ATS",
            "Rest",
            "A negative-control angle for schedule fatigue risk.",
            (
                record
                for record in team_records
                if record["game_type"] == "REG"
                and record["rest_advantage"] is not None
                and record["rest_advantage"] <= -3
            ),
            lambda record: record["ats_outcome"],
        ),
        pattern(
            "Wind 10+ mph unders",
            "Total",
            "Weather",
            "Wind is a practical scoring constraint for passing and kicking efficiency.",
            (
                game
                for game in outdoor_games
                if game["wind"] is not None and game["wind"] >= 10
            ),
            lambda game: outcome(-game["total_margin"]),
        ),
        pattern(
            "Wind 15+ mph unders",
            "Total",
            "Weather",
            "Higher wind threshold isolates the strongest weather games.",
            (
                game
                for game in outdoor_games
                if game["wind"] is not None and game["wind"] >= 15
            ),
            lambda game: outcome(-game["total_margin"]),
        ),
        pattern(
            "Freezing outdoor unders",
            "Total",
            "Weather",
            "Cold-weather games test whether scoring is suppressed after totals adjust.",
            (
                game
                for game in outdoor_games
                if game["temp"] is not None and game["temp"] <= 32
            ),
            lambda game: outcome(-game["total_margin"]),
        ),
        pattern(
            "Controlled-roof overs",
            "Total",
            "Venue",
            "Dome and closed-roof conditions remove weather drag from scoring.",
            (
                game
                for game in regular_games
                if game["roof"] in {"dome", "closed"}
            ),
            lambda game: outcome(game["total_margin"]),
        ),
        pattern(
            "Division game unders",
            "Total",
            "Division",
            "Division familiarity is often priced as a lower-variance matchup.",
            (
                game
                for game in regular_games
                if game["div_game"]
            ),
            lambda game: outcome(-game["total_margin"]),
        ),
        pattern(
            "Low totals <=39.5 under",
            "Total",
            "Total",
            "Tests whether already-low totals still clear the under at -110.",
            (
                game
                for game in regular_games
                if game["total_line"] <= 39.5
            ),
            lambda game: outcome(-game["total_margin"]),
        ),
        pattern(
            "High totals >=48 under",
            "Total",
            "Total",
            "High totals can expose over tax when the market chases offensive games.",
            (
                game
                for game in regular_games
                if game["total_line"] >= 48
            ),
            lambda game: outcome(-game["total_margin"]),
        ),
        pattern(
            "High totals >=48 over",
            "Total",
            "Total",
            "The opposite side is included to prevent one-sided storytelling.",
            (
                game
                for game in regular_games
                if game["total_line"] >= 48
            ),
            lambda game: outcome(game["total_margin"]),
        ),
    ]
    return sorted(patterns, key=lambda item: item["edge_score"], reverse=True)


def build_team_rows(team_records: list[dict], team_meta: dict[str, dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in team_records:
        grouped[record["team"]].append(record)

    rows = []
    for team, records in grouped.items():
        regular = [record for record in records if record["game_type"] == "REG"]
        recent = [
            record
            for record in regular
            if record["season"] >= max(r["season"] for r in regular) - 2
        ]
        favorite = [record for record in regular if record["role"] == "Favorite"]
        underdog = [record for record in regular if record["role"] == "Underdog"]
        home = [record for record in regular if record["is_home"]]
        away = [record for record in regular if not record["is_home"]]
        over = rounded_summary(record["over_outcome"] for record in regular)
        ats = summarize_team_records(regular)
        meta = team_meta.get(team, {})
        rows.append(
            {
                "team": team,
                "name": meta.get("name", team),
                "short": meta.get("short", team),
                "conference": meta.get("conference", ""),
                "division": meta.get("division", ""),
                "color": meta.get("color", "#151515"),
                "color2": meta.get("color2", "#d5a642"),
                "logo": meta.get("logo", ""),
                "ats": ats,
                "recent_ats": summarize_team_records(recent),
                "favorite_ats": summarize_team_records(favorite),
                "underdog_ats": summarize_team_records(underdog),
                "home_ats": summarize_team_records(home),
                "away_ats": summarize_team_records(away),
                "over": over,
                "edge_score": edge_score(ats),
            }
        )

    return sorted(rows, key=lambda item: item["ats"]["roi"] or -999, reverse=True)


def build_output() -> dict:
    games, team_records = build_games()
    team_meta = load_team_meta()
    markets = ["Home ATS", "Away ATS", "Favorite ATS", "Underdog ATS", "Over", "Under"]
    regular_games = [game for game in games if game["game_type"] == "REG"]

    season_market = {
        market: group_market(regular_games, "season", market)
        for market in markets
    }
    week_market = {
        market: group_market(regular_games, "week", market)
        for market in markets
    }

    spread_buckets = [
        {"bucket": bucket, **summarize_games(group, "Favorite ATS")}
        for bucket, group in sorted(
            (
                (bucket, [game for game in regular_games if game["spread_bucket"] == bucket])
                for bucket in {game["spread_bucket"] for game in regular_games}
            ),
            key=lambda item: [
                "Pick'em",
                "Short 0.5-2.5",
                "Key 3-3.5",
                "Medium 4-6.5",
                "Large 7-9.5",
                "Double digit",
            ].index(item[0]),
        )
    ]
    total_buckets = [
        {"bucket": bucket, **summarize_games(group, "Under")}
        for bucket, group in sorted(
            (
                (bucket, [game for game in regular_games if game["total_bucket"] == bucket])
                for bucket in {game["total_bucket"] for game in regular_games}
            ),
            key=lambda item: [
                "Low <=39.5",
                "Lower mid 40-43.5",
                "Upper mid 44-47.5",
                "High >=48",
            ].index(item[0]),
        )
    ]
    weather_buckets = [
        {"bucket": bucket, **summarize_games(group, "Under")}
        for bucket, group in sorted(
            (
                (bucket, [game for game in regular_games if game["weather_bucket"] == bucket])
                for bucket in {game["weather_bucket"] for game in regular_games}
            ),
            key=lambda item: item[0],
        )
    ]

    last_game = max(games, key=lambda game: (game["season"], game["week"], game["gameday"]))
    latest_season = max(game["season"] for game in games)

    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "nflverse/nfldata games.csv, teamcolors.csv, logos.csv",
            "source_url": "https://github.com/nflverse/nfldata",
            "game_count": len(games),
            "regular_game_count": len(regular_games),
            "season_min": min(game["season"] for game in games),
            "season_max": latest_season,
            "latest_game": {
                "game_id": last_game["game_id"],
                "season": last_game["season"],
                "week": last_game["week"],
                "home_team": last_game["home_team"],
                "away_team": last_game["away_team"],
                "home_score": last_game["home_score"],
                "away_score": last_game["away_score"],
            },
            "assumptions": [
                "ROI assumes one unit risked at -110 odds for every bet.",
                "Win percentage excludes pushes; ROI includes pushes as zero-profit wagers.",
                "Patterns are historical filters, not predictions or guaranteed betting advice.",
            ],
        },
        "overall": [
            {"market": market, **summarize_games(regular_games, market)}
            for market in markets
        ],
        "season_market": season_market,
        "week_market": week_market,
        "spread_buckets": spread_buckets,
        "total_buckets": total_buckets,
        "weather_buckets": weather_buckets,
        "patterns": build_patterns(games, team_records),
        "teams": build_team_rows(team_records, team_meta),
    }


def main() -> None:
    data = build_output()
    payload = json.dumps(data, indent=2, sort_keys=True)
    OUTPUT_PATH.write_text(
        "window.NFL_BETTING_DASHBOARD = " + payload + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT_PATH.relative_to(BASE_DIR)}")
    print(
        f"Games: {data['meta']['game_count']} | "
        f"Seasons: {data['meta']['season_min']}-{data['meta']['season_max']}"
    )


if __name__ == "__main__":
    main()
