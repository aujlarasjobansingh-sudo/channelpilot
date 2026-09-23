# ChannelPilot — your YouTube channel manager, running on your PC

A local agent that watches your channel, tells you what's going on, what to improve,
writes titles / descriptions / tags / SEO for you, and can manage videos and comments —
always showing you the exact change and asking first.

**Nothing leaves your PC** except calls to YouTube's own API.

## First-time setup (about 15 minutes)

1. Install **Python 3.10+** from https://www.python.org/downloads/
   (tick **"Add python.exe to PATH"** during install).
2. Unzip this folder anywhere on your PC and double-click **`install.bat`**.
3. Give the agent a brain — pick ONE:
   - **A. Free, fully local (recommended):** install Ollama from https://ollama.com/download,
     then open a terminal and run: `ollama pull llama3.1:8b`
   - **B.** Or paste an API key into `config.yaml` (under `brain` → `api_key`).
4. Double-click **`start.bat`**, then open **http://127.0.0.1:5000** in your browser.

That's it. Talk to it in the Chat tab.

## Connect your channel (do this later, whenever you're ready)

The agent works without this, but it can't see your channel until you connect it.

1. Go to **console.cloud.google.com** and create a project (call it `ChannelPilot`).
2. **APIs & Services → Library** → enable **YouTube Data API v3** and **YouTube Analytics API**.
3. **OAuth consent screen** → User type **External** → fill app name + your email → Save.
   Add your Gmail under **Test users**.
4. **Credentials → Create Credentials → OAuth client ID** → Application type: **Desktop app**
   → Create → **Download JSON**.
5. Rename the downloaded file to **`client_secrets.json`** and put it in the **`data`** folder.
6. Open ChannelPilot → **Connect tab** → **"Connect channel"**.
   Google will warn the app is unverified → click **Advanced → Go to ChannelPilot**.
   (Safe: it's your own app, made by you, running on your PC.)
7. To let the agent change titles/descriptions, reply to comments, or upload videos,
   also click **"Grant manage access"** in the Connect tab.

## What it does

- **Chat** — ask anything about your channel. Type "briefing" any time for a full report.
- **Briefing** — what's going on with your channel + what to improve, generated from real data.
- **SEO Studio** — titles, descriptions, tags, hashtags, chapters, or a full SEO package per video.
- **Manage** — see videos & comments, update titles/descriptions/tags, reply to comments,
  upload videos. Every change is shown to you and needs your yes first.
- **Connect** — connection status and the buttons to connect your channel.

## Daily briefing on autopilot (optional)

To get a briefing file every morning without opening the app:

1. Open **Task Scheduler** → Create Basic Task → Daily, pick a time.
2. Action: **Start a program**. Program: your `pythonw.exe`
   (usually `C:\Users\YOU\AppData\Local\Programs\Python\Python312\pythonw.exe`).
3. Arguments: `"C:\path\to\ChannelPilot\app.py" --briefing`
4. Briefings land in `data\briefings\briefing-YYYY-MM-DD.md`.

## Use it from your phone (PC off)

Want the agent on your phone even when your PC is off? Put it on a free server:
open **`DEPLOY_PHONE.md`** and follow the steps (~25 minutes, all free).

## If something's wrong

The agent talks straight: if it's blocked, it tells you exactly what's missing and what to do.
For setup problems, open `agent/knowledge/troubleshooting.md` — it covers the common ones.

To check everything from a terminal: `python app.py --check`
