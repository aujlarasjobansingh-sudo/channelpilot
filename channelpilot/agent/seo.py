"""SEO studio: titles, descriptions, tags, hashtags, chapters, full packages."""
import os

from agent.brain import BrainNotAvailable

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GUIDE = None


def _guide():
    global _GUIDE
    if _GUIDE is None:
        p = os.path.join(BASE_DIR, "agent", "knowledge", "seo_guide.md")
        _GUIDE = open(p, encoding="utf-8").read()
    return _GUIDE


def _run(brain, task_prompt):
    if not brain.available():
        return False, (
            "My writing brain isn't running, so I can't write these. Start Ollama on your PC "
            "(or paste an API key in config.yaml), then try again. I won't fake them."
        )
    system = ("You are ChannelPilot, a YouTube SEO specialist. "
              "Follow this guide exactly:\n\n" + _guide())
    try:
        return True, brain.chat([{"role": "user", "content": task_prompt}], system=system)
    except BrainNotAvailable as e:
        return False, str(e)


def write_titles(d, brain):
    topic = d.get("topic", "").strip()
    niche = d.get("niche", "").strip() or "general"
    n = int(d.get("count", 10) or 10)
    if not topic:
        return False, "Tell me what the video is about first."
    return _run(brain,
        f"Write {n} YouTube titles for a video about: {topic}\nNiche: {niche}\n"
        "Numbered list. Each under 60 characters. No clickbait the video can't deliver.")


def write_description(d, brain):
    topic = d.get("topic", "").strip()
    points = d.get("points", "").strip()
    if not topic:
        return False, "Tell me what the video is about first."
    return _run(brain,
        f"Write a full YouTube description for a video about: {topic}\n"
        f"Key points to cover: {points or 'not provided'}\n"
        "Include: hook + keywords in the first 2 lines, a short summary, a chapters placeholder, "
        "and max 3 hashtags at the end.")


def write_tags(d, brain):
    topic = d.get("topic", "").strip()
    if not topic:
        return False, "Tell me what the video is about first."
    return _run(brain,
        f"Write a YouTube tag list for a video about: {topic}\n"
        "Return ONLY a comma-separated list, total under 500 characters. "
        "Mix broad, specific, and long-tail tags.")


def write_hashtags(d, brain):
    topic = d.get("topic", "").strip()
    if not topic:
        return False, "Tell me what the video is about first."
    return _run(brain,
        f"Write max 3 relevant YouTube hashtags for a video about: {topic}\n"
        "Return only the hashtags, space-separated.")


def write_chapters(d, brain):
    outline = d.get("outline", "").strip()
    if not outline:
        return False, "Paste your video outline or section list first."
    return _run(brain,
        f"Turn this video outline into YouTube chapters:\n{outline}\n"
        "Format: 00:00 Title on each line, starting at 00:00, clear benefit-driven chapter names.")


def full_package(d, brain):
    topic = d.get("topic", "").strip()
    niche = d.get("niche", "").strip() or "general"
    points = d.get("points", "").strip()
    if not topic:
        return False, "Tell me what the video is about first."
    return _run(brain,
        f"Create a complete YouTube SEO package for a video about: {topic}\nNiche: {niche}\n"
        f"Key points: {points or 'not provided'}\n\n"
        "Deliver, in order:\n"
        "1. 10 title options (numbered, under 60 chars)\n"
        "2. Your top pick with one line saying why\n"
        "3. Full description (hook + keywords first, summary, chapters placeholder, max 3 hashtags)\n"
        "4. Tag list (comma-separated, under 500 chars)\n"
        "No fluff, just the package.")
