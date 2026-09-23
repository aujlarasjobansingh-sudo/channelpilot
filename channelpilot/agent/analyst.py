"""Channel health analysis: what's going on, and what to improve."""
import json
from datetime import date, timedelta


def _pct(cur, prev):
    if prev == 0:
        return "n/a" if cur == 0 else "+inf"
    d = (cur - prev) / prev * 100
    return f"{d:+.1f}%"


def build_snapshot(yt, days=28):
    ok, ch = yt.channel_overview()
    if not ok:
        return False, ch
    ok, vids = yt.recent_videos(25)
    if not ok:
        return False, vids

    end = date.today()
    start = end - timedelta(days=days)
    prev_start = end - timedelta(days=days * 2)
    prev_end = start

    ids = [v["id"] for v in vids]
    ok, perf = yt.video_performance(ids, start.isoformat(), end.isoformat()) if ids else (True, {})
    if not ok:
        return False, perf
    for v in vids:
        v.update(perf.get(v["id"], {}))

    ok, cur = yt.channel_totals(start.isoformat(), end.isoformat())
    if not ok:
        return False, cur
    ok, prev = yt.channel_totals(prev_start.isoformat(), prev_end.isoformat())
    if not ok:
        prev = {"views": 0, "minutes_watched": 0, "subs_gained": 0, "subs_lost": 0}

    views = sorted([v.get("views", 0) for v in vids])
    median = views[len(views) // 2] if views else 0
    by_views = sorted(vids, key=lambda v: v.get("views", 0), reverse=True)
    winners = [{"title": v["title"], "views": v.get("views", 0)} for v in by_views[:3]]
    losers = [{"title": v["title"], "views": v.get("views", 0)}
              for v in by_views if v.get("views", 0) < median * 0.5][:3]

    published_in_window = sum(1 for v in vids if v["published_at"] >= start.isoformat())
    avds = [v.get("avg_view_secs", 0) for v in vids if v.get("avg_view_secs")]
    median_avd = sorted(avds)[len(avds) // 2] if avds else 0

    snap = {
        "channel": ch["title"],
        "subs": ch["subs"],
        "total_views": ch["total_views"],
        "video_count": ch["video_count"],
        "days": days,
        "period_views": cur["views"],
        "period_views_prev": prev["views"],
        "period_minutes": cur["minutes_watched"],
        "period_minutes_prev": prev["minutes_watched"],
        "period_subs_net": cur["subs_gained"] - cur["subs_lost"],
        "period_subs_net_prev": prev["subs_gained"] - prev["subs_lost"],
        "uploads_in_window": published_in_window,
        "median_views": median,
        "median_avg_view_secs": round(median_avd, 1),
        "winners": winners,
        "losers": losers,
    }
    return True, snap


def _recommendations(s):
    recs = []
    expected = max(2, s["days"] // 7)
    if s["uploads_in_window"] < expected:
        recs.append(
            f"Consistency: {s['uploads_in_window']} uploads in {s['days']} days. "
            "Pick a cadence you can sustain (even 1/week) — the algorithm rewards predictable output."
        )
    if s["losers"]:
        titles = "; ".join(f"\"{l['title']}\" ({l['views']} views)" for l in s["losers"])
        recs.append(
            f"Packaging: these underperformed vs your median ({s['median_views']} views): {titles}. "
            "Rewrite their titles/thumbnails with a clearer curiosity gap — use the SEO Studio."
        )
    if s["median_avg_view_secs"] and s["median_avg_view_secs"] < 90:
        recs.append(
            f"Retention: median average view duration is only {s['median_avg_view_secs']}s. "
            "Cut slow intros — promise the payoff in the first 20 seconds and re-hook every 60-90s."
        )
    if s["period_subs_net"] <= 0:
        recs.append(
            "Growth is flat: subs net gained is zero or negative. Double down on the format of your "
            "top performer — make a direct follow-up or part 2 this week."
        )
    recs.append(
        "Note: I can't see impression click-through rate through the YouTube API. "
        "Check YouTube Studio > Analytics > Reach for CTR and fix anything under ~3%."
    )
    return recs


def render_rule_based(s):
    L = []
    L.append(f"# Channel briefing — last {s['days']} days")
    L.append("")
    L.append(f"**{s['channel']}** — {s['subs']:,} subscribers, {s['total_views']:,} total views, {s['video_count']} videos.")
    L.append("")
    L.append("## What's going on")
    L.append(f"- Views: {s['period_views']:,} ({_pct(s['period_views'], s['period_views_prev'])} vs previous {s['days']} days)")
    L.append(f"- Watch time: {s['period_minutes']:,.0f} minutes ({_pct(s['period_minutes'], s['period_minutes_prev'])})")
    L.append(f"- Subs (net): {s['period_subs_net']:+,} ({s['period_subs_net_prev']:+,} before)")
    L.append(f"- Uploads: {s['uploads_in_window']} in {s['days']} days")
    if s["winners"]:
        L.append("- Top performers: " + "; ".join(f"\"{w['title']}\" ({w['views']:,} views)" for w in s["winners"]))
    if s["losers"]:
        L.append("- Needs attention: " + "; ".join(f"\"{w['title']}\" ({w['views']:,} views)" for w in s["losers"]))
    L.append("")
    L.append("## What to improve")
    for r in _recommendations(s):
        L.append(f"- {r}")
    return "\n".join(L)


INSIGHT_PROMPT = """You are ChannelPilot, a blunt YouTube strategist. Here is the channel's data as JSON:

{data}

Write two short sections:
1. "What's going on" — 3-5 bullets, plain words, no jargon.
2. "What to improve" — 3-5 concrete actions for this week, specific to these numbers.
Be direct. If something looks bad, say so. Keep it under 200 words."""


def run_briefing(yt, brain, days=28):
    ok, snap = build_snapshot(yt, days)
    if not ok:
        return False, snap  # snap is the straight-talk error message
    text = render_rule_based(snap)
    if brain.available():
        try:
            compact = {k: v for k, v in snap.items()}
            insight = brain.chat(
                [{"role": "user", "content": INSIGHT_PROMPT.format(data=json.dumps(compact))}],
                system="You are ChannelPilot. Be direct and plain. Short answers.",
            )
            text += "\n\n---\n\n## My read\n\n" + insight
        except Exception:
            pass
    return True, text
