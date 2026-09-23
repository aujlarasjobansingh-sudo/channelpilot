"""YouTube access: OAuth login, channel stats, videos, analytics, comments, uploads."""
import os
import json

from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _p(*parts):
    return os.path.join(BASE_DIR, *parts)


class NotConnected(Exception):
    pass


class YouTubeClient:
    def __init__(self, cfg, manage=False):
        self.cfg = cfg
        self.manage = manage
        ycfg = cfg["youtube"]
        self.scopes = ycfg.get("scopes_manage") if manage else ycfg.get("scopes_read")
        self.secrets = _p(ycfg["client_secrets_file"])
        self.token_file = _p(ycfg["token_manage_file"] if manage else ycfg["token_read_file"])

    # ---------------- auth ----------------
    def _client_config(self):
        """OAuth client config: from env (server) or client_secrets.json (PC)."""
        env_json = os.environ.get("YOUTUBE_CLIENT_JSON")
        if env_json:
            try:
                return json.loads(env_json)
            except Exception:
                return None
        if os.path.exists(self.secrets):
            with open(self.secrets, encoding="utf-8") as f:
                return json.load(f)
        return None

    def _creds(self):
        # 1) token stored as env var (free server — disk is wiped on sleep)
        env_key = "YOUTUBE_TOKEN_MANAGE_JSON" if self.manage else "YOUTUBE_TOKEN_JSON"
        env_tok = os.environ.get(env_key)
        if env_tok:
            try:
                creds = Credentials.from_authorized_user_info(json.loads(env_tok), self.scopes)
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                if creds.valid:
                    return creds, None
            except Exception:
                pass
        # 2) token file (PC)
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        if creds and creds.valid:
            return creds, None
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self._save(creds)
                return creds, None
            except Exception as e:
                return None, f"Your saved login expired and refresh failed ({e}). Reconnect from the Connect tab."
        return None, None

    def _save(self, creds):
        os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
        with open(self.token_file, "w") as f:
            f.write(creds.to_json())

    def connect_interactive(self):
        """Runs the Google login in the user's browser (PC). Returns (ok, message)."""
        cfg = self._client_config()
        if not cfg:
            return False, (
                "I can't find your Google OAuth client. On PC: put client_secrets.json in the data folder "
                "(see README). On the server: set the YOUTUBE_CLIENT_JSON environment variable "
                "(see DEPLOY_PHONE.md)."
            )
        try:
            flow = InstalledAppFlow.from_client_config(cfg, self.scopes)
            creds = flow.run_local_server(port=0, prompt="consent")
            self._save(creds)
            ok, ch = self.channel_overview()
            if ok:
                return True, f"Connected to '{ch['title']}'."
            return True, "Login saved."
        except Exception as e:
            return False, f"Login failed: {e}"

    def web_auth_url(self, redirect_uri):
        """Start of the web OAuth flow (server). Returns (auth_url, state) or (None, error)."""
        cfg = self._client_config()
        if not cfg:
            return None, ("No YouTube client configured. Set YOUTUBE_CLIENT_JSON in the service's "
                          "environment variables (see DEPLOY_PHONE.md).")
        try:
            flow = Flow.from_client_config(cfg, scopes=self.scopes, redirect_uri=redirect_uri)
            auth_url, state = flow.authorization_url(
                access_type="offline", prompt="consent", include_granted_scopes="true")
            return auth_url, state
        except Exception as e:
            return None, f"Couldn't start Google login: {e}"

    def web_auth_finish(self, redirect_uri, authorization_response):
        """End of the web OAuth flow. Returns the token JSON (user saves it as an env var)."""
        cfg = self._client_config()
        flow = Flow.from_client_config(cfg, scopes=self.scopes, redirect_uri=redirect_uri)
        flow.fetch_token(authorization_response=authorization_response)
        self._save(flow.credentials)
        return flow.credentials.to_json()

    def _svc(self, api="youtube", version="v3"):
        creds, msg = self._creds()
        if not creds:
            raise NotConnected(
                msg or "I'm not connected to your channel yet. Open the Connect tab and connect it — "
                       "it takes a few minutes and the README walks you through it."
            )
        return build(api, version, credentials=creds)

    def _err(self, e):
        txt = str(e)
        if "quotaExceeded" in txt or "quota" in txt.lower():
            return "YouTube API quota ran out for today (it's a free daily limit). Try again tomorrow — I use very little, so this is rare."
        if "accessNotConfigured" in txt:
            return "The YouTube Data API isn't enabled in your Google Cloud project. Enable 'YouTube Data API v3' and try again."
        return f"YouTube said no: {txt[:300]}"

    # ---------------- reads ----------------
    def channel_overview(self):
        try:
            yt = self._svc()
            r = yt.channels().list(part="snippet,statistics,contentDetails", mine=True).execute()
            items = r.get("items", [])
            if not items:
                return False, "I connected, but found no channel on this Google account."
            c, s, st = items[0], items[0]["snippet"], items[0]["statistics"]
            return True, {
                "title": s["title"],
                "subs": int(st.get("subscriberCount", 0)),
                "total_views": int(st.get("viewCount", 0)),
                "video_count": int(st.get("videoCount", 0)),
                "uploads_playlist": c["contentDetails"]["relatedPlaylists"]["uploads"],
                "thumbnail": s["thumbnails"]["default"]["url"],
            }
        except NotConnected as e:
            return False, str(e)
        except HttpError as e:
            return False, self._err(e)
        except Exception as e:
            return False, f"Couldn't read your channel: {e}"

    def recent_videos(self, n=25):
        try:
            yt = self._svc()
            ok, ch = self.channel_overview()
            if not ok:
                return False, ch
            pl = yt.playlistItems().list(
                playlistId=ch["uploads_playlist"], part="contentDetails", maxResults=min(n, 50)
            ).execute()
            ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
            if not ids:
                return True, []
            r = yt.videos().list(
                part="snippet,statistics,contentDetails", id=",".join(ids)
            ).execute()
            vids = []
            for v in r.get("items", []):
                s, st = v["snippet"], v.get("statistics", {})
                vids.append({
                    "id": v["id"],
                    "title": s["title"],
                    "published_at": s["publishedAt"][:10],
                    "views": int(st.get("viewCount", 0)),
                    "likes": int(st.get("likeCount", 0)),
                    "comments": int(st.get("commentCount", 0)),
                    "duration": v.get("contentDetails", {}).get("duration", ""),
                    "url": f"https://youtu.be/{v['id']}",
                })
            return True, vids
        except NotConnected as e:
            return False, str(e)
        except HttpError as e:
            return False, self._err(e)
        except Exception as e:
            return False, f"Couldn't list your videos: {e}"

    def video_performance(self, video_ids, start_date, end_date):
        """Per-video analytics for a date window. Returns {video_id: {...}}."""
        try:
            ya = self._svc("youtubeAnalytics", "v2")
            out = {}
            ids = list(video_ids)
            for i in range(0, len(ids), 50):
                chunk = ids[i:i + 50]
                r = ya.reports().query(
                    ids="channel==MINE",
                    startDate=start_date, endDate=end_date,
                    metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,"
                            "subscribersGained,likes,comments,shares",
                    dimensions="video",
                    filters="video==" + ",".join(chunk),
                    sort="-views", maxResults=50,
                ).execute()
                for row in r.get("rows", []):
                    vid = row[0]
                    out[vid] = {
                        "views": int(row[1] or 0),
                        "minutes_watched": round(float(row[2] or 0), 1),
                        "avg_view_secs": round(float(row[3] or 0), 1),
                        "avg_view_pct": round(float(row[4] or 0), 1),
                        "subs_gained": int(row[5] or 0),
                        "likes": int(row[6] or 0),
                        "comments": int(row[7] or 0),
                        "shares": int(row[8] or 0),
                    }
            return True, out
        except NotConnected as e:
            return False, str(e)
        except HttpError as e:
            return False, self._err(e)
        except Exception as e:
            return False, f"Couldn't read analytics: {e}"

    def channel_totals(self, start_date, end_date):
        try:
            ya = self._svc("youtubeAnalytics", "v2")
            r = ya.reports().query(
                ids="channel==MINE",
                startDate=start_date, endDate=end_date,
                metrics="views,estimatedMinutesWatched,subscribersGained,subscribersLost",
            ).execute()
            row = (r.get("rows") or [[0, 0, 0, 0]])[0]
            return True, {
                "views": int(row[0] or 0),
                "minutes_watched": round(float(row[1] or 0), 1),
                "subs_gained": int(row[2] or 0),
                "subs_lost": int(row[3] or 0),
            }
        except NotConnected as e:
            return False, str(e)
        except HttpError as e:
            return False, self._err(e)
        except Exception as e:
            return False, f"Couldn't read analytics: {e}"

    def recent_comments(self, n=25):
        try:
            yt = self._svc()
            ok, vids = self.recent_videos(10)
            if not ok:
                return False, vids
            out = []
            for v in vids:
                try:
                    r = yt.commentThreads().list(
                        part="snippet", videoId=v["id"], maxResults=10,
                        order="time", textFormat="plainText",
                    ).execute()
                except HttpError:
                    continue  # comments disabled on this video
                for t in r.get("items", []):
                    s = t["snippet"]["topLevelComment"]["snippet"]
                    out.append({
                        "comment_id": t["id"],
                        "video_id": v["id"],
                        "video_title": v["title"],
                        "author": s["authorDisplayName"],
                        "text": s["textDisplay"],
                        "published_at": s["publishedAt"][:16].replace("T", " "),
                        "likes": s.get("likeCount", 0),
                    })
                    if len(out) >= n:
                        return True, out
            return True, out
        except NotConnected as e:
            return False, str(e)
        except HttpError as e:
            return False, self._err(e)
        except Exception as e:
            return False, f"Couldn't read comments: {e}"

    # ---------------- writes (need manage access) ----------------
    def _need_manage(self):
        if not self.manage:
            raise NotConnected(
                "That changes your channel, so I need manage access first. "
                "Open the Connect tab and click 'Grant manage access', then try again."
            )

    def reply_to_comment(self, comment_id, text):
        try:
            self._need_manage()
            yt = self._svc()
            if not text.strip():
                return False, "Reply text is empty — write something first."
            yt.comments().insert(part="snippet", body={
                "snippet": {"parentId": comment_id, "textOriginal": text.strip()}
            }).execute()
            return True, "Reply posted."
        except NotConnected as e:
            return False, str(e)
        except HttpError as e:
            return False, self._err(e)
        except Exception as e:
            return False, f"Couldn't post the reply: {e}"

    def update_video(self, video_id, title=None, description=None, tags=None):
        try:
            self._need_manage()
            yt = self._svc()
            r = yt.videos().list(part="snippet", id=video_id).execute()
            items = r.get("items", [])
            if not items:
                return False, "Video not found."
            snip = items[0]["snippet"]
            changes = []
            if title and title != snip.get("title"):
                changes.append(f"title -> {title}"); snip["title"] = title
            if description is not None and description != snip.get("description"):
                changes.append("description updated"); snip["description"] = description
            if tags is not None:
                tag_list = [t.strip() for t in tags if t.strip()] if isinstance(tags, list) else \
                           [t.strip() for t in str(tags).split(",") if t.strip()]
                changes.append(f"{len(tag_list)} tags"); snip["tags"] = tag_list
            if not changes:
                return False, "Nothing to change — the values are already the same."
            yt.videos().update(part="snippet", body={"id": video_id, "snippet": snip}).execute()
            return True, "Updated: " + ", ".join(changes) + "."
        except NotConnected as e:
            return False, str(e)
        except HttpError as e:
            return False, self._err(e)
        except Exception as e:
            return False, f"Couldn't update the video: {e}"

    def upload_video(self, path, title, description="", tags=(), privacy="private"):
        try:
            self._need_manage()
            yt = self._svc()
            if not os.path.exists(path):
                return False, "File not found."
            if not title.strip():
                return False, "Give the video a title first."
            body = {
                "snippet": {
                    "title": title.strip(),
                    "description": description or "",
                    "tags": [t.strip() for t in tags if str(t).strip()],
                    "categoryId": "22",
                },
                "status": {"privacyStatus": privacy if privacy in ("private", "unlisted", "public") else "private"},
            }
            media = MediaFileUpload(path, mimetype="video/*", resumable=True, chunksize=8 * 1024 * 1024)
            req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
            resp = None
            while resp is None:
                _, resp = req.next_chunk()
            vid = resp.get("id")
            return True, f"Uploaded ({privacy}): https://youtu.be/{vid}"
        except NotConnected as e:
            return False, str(e)
        except HttpError as e:
            return False, self._err(e)
        except Exception as e:
            return False, f"Upload failed: {e}"
