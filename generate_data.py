#!/usr/bin/env python3
"""Generate data.json for the dashboard from local data sources."""
import json
import sqlite3
import ssl
import urllib.request
from datetime import date
from pathlib import Path

BASE = Path(__file__).parent
AI_DB = Path.home() / "Develop/AI_limited_usage/ai_usage.db"
NLM_ARCHIVE = Path.home() / "Develop/notebooklm/archive/daily"


def get_ai_usage():
    conn = sqlite3.connect(AI_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # latest snapshot
    cur.execute("""
        SELECT service, metric, percent, captured_at
        FROM usage_snapshots
        WHERE captured_at = (SELECT MAX(captured_at) FROM usage_snapshots)
    """)
    rows = cur.fetchall()
    data = {"captured_at": None}
    for r in rows:
        svc = r["service"]
        if svc not in data:
            data[svc] = {}
        data[svc][r["metric"]] = r["percent"]
        data["captured_at"] = r["captured_at"]

    # daily history: last 14 days, pick the latest snapshot per day
    cur.execute("""
        SELECT date(captured_at) as day, service, metric, percent
        FROM usage_snapshots
        WHERE captured_at IN (
            SELECT MAX(captured_at) FROM usage_snapshots
            GROUP BY date(captured_at)
        )
        AND date(captured_at) >= date('now', '-13 days')
        ORDER BY day ASC
    """)
    history_rows = cur.fetchall()
    conn.close()

    # aggregate per day -> total score (session + weekly_all + gemini weekly)
    from collections import defaultdict
    days = defaultdict(dict)
    for r in history_rows:
        days[r["day"]][f"{r['service']}.{r['metric']}"] = r["percent"]

    history = []
    for day in sorted(days.keys()):
        d = days[day]
        total = (d.get("claude.session", 0) + d.get("claude.weekly_all", 0) + d.get("gemini.weekly", 0))
        history.append({"date": day, "total_score": round(total, 1),
                        "claude_session": d.get("claude.session", 0),
                        "claude_weekly": d.get("claude.weekly_all", 0),
                        "gemini_weekly": d.get("gemini.weekly", 0)})
    data["history"] = history
    return data


DUOLINGO_USERNAME = "RPhk251857"


def get_duolingo():
    url = f"https://www.duolingo.com/2017-06-30/users?username={DUOLINGO_USERNAME}"
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as res:
            data = json.loads(res.read())
        user = data["users"][0]
        en_xp = next(
            (c["xp"] for c in user.get("courses", []) if c["learningLanguage"] == "en"),
            None,
        )
        return {
            "streak": user.get("streak"),
            "total_xp": en_xp,
        }
    except Exception as e:
        print(f"⚠ Duolingo fetch failed: {e}")
        return {"streak": None, "total_xp": None}


def get_notebooklm():
    today_str = str(date.today())
    episodes = []

    for meta_path in sorted(NLM_ARCHIVE.rglob("episode.meta.json")):
        try:
            meta = json.loads(meta_path.read_text())
        except Exception:
            continue
        if meta.get("date") != today_str:
            continue

        title = meta.get("title", "")
        slot = "朝" if "朝" in title else ("夜" if "夜" in title else "—")
        episodes.append({
            "episode": meta.get("episode"),
            "slot": slot,
            "theme": meta.get("theme", ""),
            "languages": meta.get("languages", "ja"),
        })

    english_theme = next(
        (e["theme"] for e in episodes if "en" in e.get("languages", "")), None
    )

    return {"today": today_str, "episodes": episodes, "english_theme": english_theme}


def main():
    data = {
        "generated_at": str(date.today()),
        "ai_usage": get_ai_usage(),
        "notebooklm": get_notebooklm(),
        "duolingo": get_duolingo(),
    }
    out = BASE / "data.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"✓ data.json generated ({len(data['notebooklm']['episodes'])} episodes today)")


if __name__ == "__main__":
    main()
