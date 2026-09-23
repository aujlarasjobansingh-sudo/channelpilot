# Troubleshooting

## Brain problems
- "I can't reach Ollama": Ollama isn't running. Open the Ollama app (it sits in the system tray),
  or run `ollama serve` in a terminal. Then `ollama pull llama3.1:8b` once to download the model.
- Empty/slow answers: the first answer after starting Ollama is slow (model loading). Normal.
- Using an API key instead: paste key + base URL in config.yaml under brain, set provider to "openai_compatible".

## App problems
- "Port 5000 in use": another program uses it. Change `port:` in config.yaml (e.g. 5001) and restart.
- start.bat closes instantly: run `python app.py` from a terminal to see the error.

## Connecting your channel
- Google shows "unverified app" warning: click Advanced → "Go to ChannelPilot (unsafe)".
  It's safe — it's your own app that you created.
- "Access blocked" / Error 403: add your Gmail as a test user in the OAuth consent screen, then retry.
- "API not enabled": enable "YouTube Data API v3" AND "YouTube Analytics API" in your Cloud project.
- Login works but "no channel found": you logged in with a Google account that has no YouTube channel.
  Use the account that owns the channel (brand accounts: pick the right channel after login).
- "I'm not connected yet" from the agent: token expired — just reconnect from the Connect tab.
- Quota exceeded: free daily API limit hit. Wait until tomorrow; normal use never hits it.

## Channel problems the agent may flag
- Yellow $ icon (limited ads): check YouTube Studio > Content > restrictions. Often triggered by
  the first 30 seconds — avoid graphic/strong language early, then request a manual review.
- Copyright claim (not a strike): usually just means the claimant monetizes or blocks in some
  regions. Dispute only if you're sure, or trim/replace via Studio's editor.
- Copyright strike: serious — 3 strikes = channel termination. Take the "Copyright School",
  never re-upload struck content.
- Sudden view drop: see the Analytics Guide "Diagnosing a drop" checklist — don't panic-delete videos.

## When in doubt
Tell the agent exactly what you see, word for word. It will tell you straight what's wrong
and what to do next.
