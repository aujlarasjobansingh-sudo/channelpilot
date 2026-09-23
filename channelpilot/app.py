#!/usr/bin/env python3
"""ChannelPilot — a YouTube channel manager.

Local PC:      python app.py
Free server:   HOSTED=1 python app.py   (see DEPLOY_PHONE.md)
"""
import os
import sys
import argparse
from datetime import date
from functools import wraps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import yaml
from flask import Flask, render_template, request, jsonify, redirect, session

from agent.brain import Brain, BrainNotAvailable
from agent import youtube_client as ytc
from agent import analyst, seo

HOSTED = os.environ.get("HOSTED") == "1"


def load_config():
    with open(os.path.join(BASE_DIR, "config.yaml"), encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    # Environment overrides (used on the free server)
    b = cfg["brain"]
    b["provider"] = os.environ.get("BRAIN_PROVIDER", b.get("provider", "ollama"))
    b["api_base"] = os.environ.get("BRAIN_API_BASE", b.get("api_base", ""))
    b["api_key"] = os.environ.get("BRAIN_API_KEY", b.get("api_key", ""))
    b["api_model"] = os.environ.get("BRAIN_API_MODEL", b.get("api_model", ""))
    b["ollama_url"] = os.environ.get("OLLAMA_URL", b.get("ollama_url", "http://localhost:11434"))
    b["ollama_model"] = os.environ.get("OLLAMA_MODEL", b.get("ollama_model", "llama3.1:8b"))
    return cfg


CFG = load_config()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", CFG["server"].get("secret_key", "dev-key-change-me"))
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")
BRAIN = Brain(CFG)

_knowledge_cache = None


def knowledge_text():
    global _knowledge_cache
    if _knowledge_cache is None:
        parts = []
        p = os.path.join(BASE_DIR, "agent", "persona.md")
        if os.path.exists(p):
            parts.append(open(p, encoding="utf-8").read())
        kdir = os.path.join(BASE_DIR, "agent", "knowledge")
        for fn in sorted(os.listdir(kdir)):
            if fn.endswith(".md"):
                parts.append(
                    "\n\n# KNOWLEDGE FILE: " + fn + "\n"
                    + open(os.path.join(kdir, fn), encoding="utf-8").read()
                )
        _knowledge_cache = "\n".join(parts)
    return _knowledge_cache


def get_yt(manage=False):
    return ytc.YouTubeClient(CFG, manage=manage)


def channel_context_line():
    try:
        yt = get_yt()
        ok, ch = yt.channel_overview()
        if not ok:
            return ""
        return (
            f"LIVE CHANNEL DATA: '{ch['title']}' — {ch['subs']:,} subscribers, "
            f"{ch['total_views']:,} total views, {ch['video_count']} videos."
        )
    except Exception:
        return ""


# ---------------- password gate (only when APP_PASSWORD is set) ----------------
@app.before_request
def _gate():
    if not APP_PASSWORD:
        return None
    if session.get("authed"):
        return None
    if request.path in ("/login", "/oauth2callback") or request.path.startswith("/static"):
        return None
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and request.form.get("password") == APP_PASSWORD:
        session["authed"] = True
        return redirect("/")
    return ("""<body style="font-family:sans-serif;background:#14161a;color:#e8eaed;
              display:flex;justify-content:center;padding-top:80px">
              <form method="post" style="text-align:center">
              <h2>ChannelPilot</h2>
              <input type="password" name="password" placeholder="Password" autofocus
               style="padding:10px;border-radius:8px;border:1px solid #2c313a;background:#101216;color:#e8eaed"><br><br>
              <button style="padding:10px 24px;border-radius:8px;border:none;background:#4da3ff;font-weight:700">Open</button>
              </form></body>""")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- pages & chat ----------------
@app.route("/")
def home():
    return render_template("index.html", agent_name=CFG.get("agent_name", "ChannelPilot"))


@app.route("/api/status")
def api_status():
    yt = get_yt()
    ok, ch = yt.channel_overview()
    ytm = get_yt(manage=True)
    okm, _ = ytm.channel_overview()
    return jsonify({
        "brain": BRAIN.available(),
        "brain_provider": BRAIN.provider(),
        "youtube_read": ok,
        "youtube_manage": okm,
        "channel": ch["title"] if ok else None,
        "hosted": HOSTED,
    })


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True)
    history = data.get("messages", [])
    user_text = ""
    for m in reversed(history):
        if m.get("role") == "user":
            user_text = m.get("content", "")
            break
    low = user_text.lower()
    if any(k in low for k in ("briefing", "channel report", "how is my channel",
                              "how's my channel", "performance report", "channel health")):
        ok, text = analyst.run_briefing(get_yt(), BRAIN, CFG["briefing"]["days_back"])
        return jsonify({"reply": text})
    system = knowledge_text()
    ctx = channel_context_line()
    if ctx:
        system += "\n\n" + ctx
    try:
        reply = BRAIN.chat(history, system=system)
        return jsonify({"reply": reply})
    except BrainNotAvailable as e:
        return jsonify({"reply": str(e)})


# ---------------- briefing ----------------
@app.route("/api/briefing")
def api_briefing():
    save = request.args.get("save") == "1"
    ok, text = analyst.run_briefing(get_yt(), BRAIN, CFG["briefing"]["days_back"])
    if save and ok:
        d = os.path.join(BASE_DIR, CFG["briefing"]["save_to"])
        os.makedirs(d, exist_ok=True)
        fp = os.path.join(d, f"briefing-{date.today().isoformat()}.md")
        with open(fp, "w", encoding="utf-8") as f:
            f.write(text)
    return jsonify({"ok": ok, "briefing": text})


# ---------------- reads ----------------
@app.route("/api/videos")
def api_videos():
    yt = get_yt()
    ok, vids = yt.recent_videos(20)
    return jsonify({"ok": ok, "videos": vids if ok else [], "message": vids if not ok else ""})


@app.route("/api/comments")
def api_comments():
    yt = get_yt()
    ok, comments = yt.recent_comments(25)
    return jsonify({"ok": ok, "comments": comments if ok else [], "message": comments if not ok else ""})


# ---------------- writes (need manage access + your confirmation in the UI) ----------------
@app.route("/api/comment/reply", methods=["POST"])
def api_comment_reply():
    d = request.get_json(force=True)
    yt = get_yt(manage=True)
    ok, msg = yt.reply_to_comment(d.get("comment_id"), d.get("text", ""))
    return jsonify({"ok": ok, "message": msg})


@app.route("/api/video/update", methods=["POST"])
def api_video_update():
    d = request.get_json(force=True)
    yt = get_yt(manage=True)
    ok, msg = yt.update_video(d.get("video_id"), d.get("title"),
                              d.get("description"), d.get("tags"))
    return jsonify({"ok": ok, "message": msg})


@app.route("/api/video/upload", methods=["POST"])
def api_video_upload():
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify({"ok": False, "message": "No file received."})
    up = os.path.join(BASE_DIR, "data", "uploads")
    os.makedirs(up, exist_ok=True)
    path = os.path.join(up, f.filename)
    f.save(path)
    yt = get_yt(manage=True)
    ok, msg = yt.upload_video(
        path,
        request.form.get("title", ""),
        request.form.get("description", ""),
        (request.form.get("tags") or "").split(","),
        request.form.get("privacy", "private"),
    )
    return jsonify({"ok": ok, "message": msg})


# ---------------- seo ----------------
@app.route("/api/seo/<tool>", methods=["POST"])
def api_seo(tool):
    d = request.get_json(force=True)
    fn = {
        "titles": seo.write_titles,
        "description": seo.write_description,
        "tags": seo.write_tags,
        "hashtags": seo.write_hashtags,
        "chapters": seo.write_chapters,
        "package": seo.full_package,
    }.get(tool)
    if not fn:
        return jsonify({"ok": False, "message": "Unknown tool."})
    ok, text = fn(d, BRAIN)
    return jsonify({"ok": ok, "message": text})


# ---------------- connect ----------------
def _redirect_uri():
    if HOSTED:
        # Behind Render's proxy the app only sees http; the public URL is https.
        return "https://" + request.host + "/oauth2callback"
    return request.url_root.rstrip("/") + "/oauth2callback"


@app.route("/connect")
def connect():
    if HOSTED:
        yt = get_yt(manage=False)
        auth_url, state = yt.web_auth_url(_redirect_uri())
        if not auth_url:
            return f"<p>{state}</p><p><a href='/'>Back</a></p>"
        session["oauth_state"] = state
        session["oauth_manage"] = False
        return redirect(auth_url)
    yt = get_yt(manage=False)
    ok, msg = yt.connect_interactive()
    title = "Connected" if ok else "Not connected"
    return (f"<body style='font-family:sans-serif;padding:40px'><h2>{title}</h2>"
            f"<p>{msg}</p><p><a href='/'>Back to ChannelPilot</a></p></body>")


@app.route("/connect-manage")
def connect_manage():
    if HOSTED:
        yt = get_yt(manage=True)
        auth_url, state = yt.web_auth_url(_redirect_uri())
        if not auth_url:
            return f"<p>{state}</p><p><a href='/'>Back</a></p>"
        session["oauth_state"] = state
        session["oauth_manage"] = True
        return redirect(auth_url)
    yt = get_yt(manage=True)
    ok, msg = yt.connect_interactive()
    title = "Manage access granted" if ok else "Not connected"
    return (f"<body style='font-family:sans-serif;padding:40px'><h2>{title}</h2>"
            f"<p>{msg}</p><p><a href='/'>Back to ChannelPilot</a></p></body>")


@app.route("/oauth2callback")
def oauth2callback():
    if not HOSTED:
        return redirect("/")
    yt = get_yt(manage=session.get("oauth_manage", False))
    try:
        token_json = yt.web_auth_finish(_redirect_uri(), request.url)
    except Exception as e:
        return (f"<body style='font-family:sans-serif;padding:40px'><h2>Login failed</h2>"
                f"<p>{e}</p><p><a href='/'>Back</a></p></body>")
    scope = "manage" if session.get("oauth_manage") else "read"
    env_name = "YOUTUBE_TOKEN_MANAGE_JSON" if scope == "manage" else "YOUTUBE_TOKEN_JSON"
    return (f"""<body style='font-family:sans-serif;padding:40px;max-width:700px'>
        <h2>Connected ({scope} access)</h2>
        <p>One last step: free servers forget files when they sleep, so save this login
        as a setting. Copy everything in the box below, then in Render go to your service
        → <b>Environment</b> → add variable <b>{env_name}</b> → paste → Save.
        The service will restart and stay connected.</p>
        <textarea rows="8" style="width:100%" onclick="this.select()">{token_json}</textarea>
        <p><a href='/'>Back to ChannelPilot</a></p></body>""")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--briefing", action="store_true", help="print channel briefing and save it")
    ap.add_argument("--check", action="store_true", help="check brain + channel connection")
    args = ap.parse_args()

    if args.check:
        print("brain:", "OK" if BRAIN.available() else "NOT RUNNING")
        yt = get_yt()
        ok, ch = yt.channel_overview()
        print("youtube:", ch["title"] if ok else ch)
        return

    if args.briefing:
        ok, text = analyst.run_briefing(get_yt(), BRAIN, CFG["briefing"]["days_back"])
        d = os.path.join(BASE_DIR, CFG["briefing"]["save_to"])
        os.makedirs(d, exist_ok=True)
        fp = os.path.join(d, f"briefing-{date.today().isoformat()}.md")
        with open(fp, "w", encoding="utf-8") as f:
            f.write(text)
        print(text)
        print(f"\nSaved to {fp}")
        return

    host = "0.0.0.0" if HOSTED else CFG["server"]["host"]
    port = int(os.environ.get("PORT", CFG["server"]["port"]))
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
