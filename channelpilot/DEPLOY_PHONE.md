# Use ChannelPilot from your phone (PC can stay off)

This puts your agent on a **free server** (Render) so you can open it from your phone's
browser any time. Your PC version keeps working too — same agent, two homes.

**Heads-up (straight talk):**
- The free server **sleeps** when nobody uses it. First open after a while takes ~1 minute to wake up. After that it's fast.
- On the server the brain is **Gemini (free)** instead of Ollama — same agent, same knowledge.

## Step 1 — Free brain key (2 min)

1. Go to **aistudio.google.com** → sign in → **Get API key** → **Create API key**.
2. Copy the key somewhere. It's free.

## Step 2 — Google login for the server (5 min)

Your PC version uses a "Desktop app" login. The server needs a "Web application" one:

1. Go to **console.cloud.google.com** → open your ChannelPilot project
   (or create one — same steps as in the README).
2. Make sure **YouTube Data API v3** and **YouTube Analytics API** are enabled.
3. **Credentials → Create Credentials → OAuth client ID** → type **Web application**.
4. Name it `ChannelPilot server`. Under **Authorized redirect URIs** click Add URI and type:
   `https://TEMP/oauth2callback` (you'll fix this in step 5 — Google just needs something for now).
5. Create → **Download JSON**. Open it in Notepad and **copy the whole text**.

## Step 3 — Put the code on GitHub (5 min)

1. Go to **github.com** → sign up/in → **New repository** → name it `channelpilot` → Create.
2. Click **uploading an existing file** → drag in **all files and folders** from your
   unzipped `channelpilot` folder (app.py, agent folder, templates, config.yaml,
   requirements.txt, README.md, DEPLOY_PHONE.md — everything) → **Commit changes**.

## Step 4 — Create the free server (5 min)

1. Go to **render.com** → sign up (GitHub login is easiest) → **New +** → **Web Service**.
2. Connect your `channelpilot` repo → choose the **Free** plan.
3. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
4. Scroll to **Environment Variables** and add these (names must match exactly):

| Name | Value |
|---|---|
| HOSTED | 1 |
| APP_PASSWORD | pick a password you'll type on your phone |
| SECRET_KEY | any long random text |
| BRAIN_PROVIDER | openai_compatible |
| BRAIN_API_BASE | https://generativelanguage.googleapis.com/v1beta/openai/ |
| BRAIN_API_KEY | your Gemini key from Step 1 |
| BRAIN_API_MODEL | gemini-2.0-flash |
| YOUTUBE_CLIENT_JSON | paste the whole JSON text from Step 2 |

5. Click **Deploy**. Wait until it says Live. Open the URL Render gives you
   (like `https://channelpilot-xxxx.onrender.com`) on your **phone** → log in with your password.

## Step 5 — Fix the Google redirect (2 min)

1. Copy your real Render URL, e.g. `https://channelpilot-xxxx.onrender.com`
2. Back in **console.cloud.google.com → Credentials** → open the `ChannelPilot server` client →
   **Authorized redirect URIs** → replace the TEMP one with:
   `https://channelpilot-xxxx.onrender.com/oauth2callback` → **Save**.

## Step 6 — Connect your channel (2 min)

1. On your phone, open your agent → **Connect tab** → **Connect channel**.
2. Google login → allow → you'll get a page with a box of text.
3. **Copy all of it** → in Render, open your service → **Environment** → add variable
   **YOUTUBE_TOKEN_JSON** → paste → Save (service restarts, stays connected).
4. For manage access (edit titles, reply to comments): same flow with **Grant manage access**,
   then save as **YOUTUBE_TOKEN_MANAGE_JSON**.

Done. Bookmark the URL on your phone. PC off? Doesn't matter — the agent lives on the server now.

## If something's wrong

- Page won't wake up: free servers sleep — wait ~60 seconds and refresh.
- "No YouTube client configured": YOUTUBE_CLIENT_JSON missing or pasted wrong — re-check Step 4.
- Google login error "redirect_uri_mismatch": the URI in Step 5 doesn't exactly match — copy it character for character.
- Brain not answering: check BRAIN_API_KEY is set and valid at aistudio.google.com.
